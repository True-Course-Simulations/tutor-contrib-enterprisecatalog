from __future__ import annotations

import importlib.resources as importlib_resources
import os
from glob import glob

from tutor import hooks as tutor_hooks
from tutor.hooks import priorities

from .__about__ import __version__

# ######################################
# CONFIGURATION
# ######################################
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("ENTERPRISECATALOG_MYSQL_PASSWORD", "{{ 8|random_string }}"),
        ("ENTERPRISECATALOG_SECRET_KEY", "{{ 24|random_string }}"),
        ("ENTERPRISECATALOG_OAUTH2_SECRET", "{{ 8|random_string }}"),
        ("ENTERPRISECATALOG_OAUTH2_SECRET_SSO", "{{ 8|random_string }}"),
    ]
)

tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("DOCKER_REGISTRY", ""),
        ("DOCKER_IMAGE_PREFIX", ""),

        ("ENTERPRISECATALOG_REPOSITORY", "https://github.com/openedx/enterprise-catalog.git"),
        (
            "ENTERPRISECATALOG_BUILT_IMAGE",
            "{{ DOCKER_REGISTRY }}{{ DOCKER_IMAGE_PREFIX }}enterprise-catalog:{{ OPENEDX_COMMON_VERSION | replace('/', '-') }}",
        ),
        ("ENTERPRISECATALOG_DOCKER_IMAGE", ""),

        ("ENTERPRISECATALOG_VERSION", __version__),
        ("ENTERPRISECATALOG_HOST", "enterprisecatalog.{{ LMS_HOST }}"),
        ("ENTERPRISECATALOG_MYSQL_DATABASE", "enterprisecatalog"),
        ("ENTERPRISECATALOG_MYSQL_USERNAME", "enterprisecatalog"),
        ("ENTERPRISECATALOG_OAUTH2_KEY", "enterprisecatalog"),
        ("ENTERPRISECATALOG_OAUTH2_KEY_DEV", "enterprisecatalog-dev"),
        ("ENTERPRISECATALOG_OAUTH2_KEY_SSO", "enterprisecatalog-sso"),
        ("ENTERPRISECATALOG_OAUTH2_KEY_SSO_DEV", "enterprisecatalog-sso-dev"),
        ("ENTERPRISECATALOG_CACHE_REDIS_DB", "{{ OPENEDX_CACHE_REDIS_DB }}"),
    ]
)


# ######################################
# TEMPLATE RENDERING
# ######################################
templates_dir = str(importlib_resources.files("tutorenterprisecatalog") / "templates")
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(templates_dir)
tutor_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("enterprisecatalog/apps", "plugins"),
        ("enterprisecatalog/build", "plugins"),
    ]
)


# ######################################
# PATCH LOADING
# ######################################
patches_dir = importlib_resources.files("tutorenterprisecatalog") / "patches"
for path in glob(str(patches_dir / "*")):
    with open(path, encoding="utf-8") as patch_file:
        tutor_hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read()),
            priority=priorities.DEFAULT,
        )


# ######################################
# DOCKER IMAGE MANAGEMENT
# ######################################
@tutor_hooks.Filters.IMAGES_BUILD.add()
def enterprisecatalog_images_build(images, settings):
    external_image = settings.get("ENTERPRISECATALOG_DOCKER_IMAGE")
    if external_image:
        # Operator supplies an image; skip building.
        return images

    images.append(
        (
            "enterprisecatalog",
            os.path.join("plugins", "enterprisecatalog", "build", "enterprisecatalog"),
            settings["ENTERPRISECATALOG_BUILT_IMAGE"],
            (),
        )
    )
    return images


@tutor_hooks.Filters.IMAGES_PULL.add()
def enterprisecatalog_images_pull(images, settings):
    if settings.get("ENTERPRISECATALOG_DOCKER_IMAGE"):
        images.append(("enterprisecatalog", settings["ENTERPRISECATALOG_DOCKER_IMAGE"]))
    return images


# ######################################
# INITIALIZATION TASKS
# ######################################
hooks_dir = (
    importlib_resources.files("tutorenterprisecatalog")
    / "templates"
    / "enterprisecatalog"
    / "tasks"
)
for task_name in ["mysql", "enterprisecatalog", "lms"]:
    task_path = hooks_dir / task_name / "init"
    with open(task_path, encoding="utf-8") as task_file:
        tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item((task_name, task_file.read()))
