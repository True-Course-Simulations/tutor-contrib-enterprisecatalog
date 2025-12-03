from __future__ import annotations

import os
from glob import glob

import importlib.resources as importlib_resources

from tutor import fmt, hooks as tutor_hooks
from tutor.hooks import priorities

from .__about__ import __version__

config = {
    "add": {
        "MYSQL_PASSWORD": "{{ 8|random_string }}",
        "SECRET_KEY": "{{ 24|random_string }}",
        "OAUTH2_SECRET": "{{ 8|random_string }}",
        "OAUTH2_SECRET_SSO": "{{ 8|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "REPOSITORY": "https://github.com/edx/enterprise-catalog.git",
        "REPOSITORY_VERSION": "{% set ver = OPENEDX_COMMON_VERSION %}{% if ver.startswith('open-release/') %}{{ ver }}{% elif ver.startswith('release/redwood') %}open-release/redwood.master{% elif ver.startswith('release/quince') %}open-release/quince.master{% else %}{{ ver }}{% endif %}",
        # Allow operators to point to a prebuilt image; if blank we build/push BUILT_IMAGE.
        "DOCKER_IMAGE": "",
        "BUILD_IMAGE": True,
        "BUILT_IMAGE": "{{ DOCKER_REGISTRY }}diceytech/openedx-enterprise-catalog:{{ ENTERPRISECATALOG_REPOSITORY_VERSION | replace('/', '-') }}",
        "PYTHON_VERSION": "3.12.2",
        "HOST": "enterprisecatalog.{{ LMS_HOST }}",
        "MYSQL_DATABASE": "enterprisecatalog",
        "MYSQL_USERNAME": "enterprisecatalog",
        "OAUTH2_KEY": "enterprisecatalog",
        "OAUTH2_KEY_DEV": "enterprisecatalog-dev",
        "OAUTH2_KEY_SSO": "enterprisecatalog-sso",
        "OAUTH2_KEY_SSO_DEV": "enterprisecatalog-sso-dev",
        "CACHE_REDIS_DB": "{{ OPENEDX_CACHE_REDIS_DB }}",
    },
}

# Register configuration entries with Tutor
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        (f"ENTERPRISECATALOG_{key}", value)
        for key, value in config.get("add", {}).items()
    ]
)
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        (f"ENTERPRISECATALOG_{key}", value)
        for key, value in config.get("defaults", {}).items()
    ]
)

# Template roots and targets
templates_dir = str(importlib_resources.files("tutorenterprisecatalog") / "templates")
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(templates_dir)
tutor_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("enterprisecatalog/apps", "plugins"),
        ("enterprisecatalog/build", "plugins"),
    ]
)

# Load patches
patches_dir = importlib_resources.files("tutorenterprisecatalog") / "patches"
for path in glob(str(patches_dir / "*")):
    with open(path, encoding="utf-8") as patch_file:
        tutor_hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read()),
            priority=priorities.DEFAULT,
        )

# Images to build: only when external images are not provided
@tutor_hooks.Filters.IMAGES_BUILD.add()
def _images_build(images, settings):
    if settings.get("ENTERPRISECATALOG_BUILD_IMAGE") and not settings.get(
        "ENTERPRISECATALOG_DOCKER_IMAGE"
    ):
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
def _images_pull(images, settings):
    if settings.get("ENTERPRISECATALOG_DOCKER_IMAGE"):
        images.append(("enterprisecatalog", settings["ENTERPRISECATALOG_DOCKER_IMAGE"]))
    return images


@tutor_hooks.Actions.CONFIG_LOADED.add()
def _warn_image_config(config):
    if not config.get("ENTERPRISECATALOG_BUILD_IMAGE", True) and not config.get(
        "ENTERPRISECATALOG_DOCKER_IMAGE"
    ):
        fmt.echo_alert(
            "enterprisecatalog: BUILD_IMAGE is false but no ENTERPRISECATALOG_DOCKER_IMAGE is configured. Set an external image or enable building."
        )
# Init tasks
hooks_dir = importlib_resources.files("tutorenterprisecatalog") / "templates" / "enterprisecatalog" / "tasks"
for task_name in ["mysql", "enterprisecatalog", "lms"]:
    task_path = hooks_dir / task_name / "init"
    with open(task_path, encoding="utf-8") as task_file:
        tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item((task_name, task_file.read()))
