from __future__ import annotations

import os
from glob import glob

import importlib.resources as importlib_resources

from tutor import hooks as tutor_hooks
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
        "DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}diceytech/openedx-enterprise-catalog:{{ ENTERPRISECATALOG_VERSION }}",
        "WORKER_DOCKER_IMAGE": "openedx-enterprise-catalog-worker",
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

# Images to build
tutor_hooks.Filters.IMAGES_BUILD.add_items(
    [
        (
            "enterprisecatalog",
            os.path.join("plugins", "enterprisecatalog", "build", "enterprisecatalog"),
            "{{ ENTERPRISECATALOG_DOCKER_IMAGE }}",
            (),
        ),
        (
            "enterprisecatalog-worker",
            os.path.join("plugins", "enterprisecatalog", "build", "enterprisecatalog"),
            "{{ ENTERPRISECATALOG_WORKER_DOCKER_IMAGE }}",
            ("--target=openedx-enterprise-catalog-worker",),
        ),
    ]
)

# Init tasks
hooks_dir = importlib_resources.files("tutorenterprisecatalog") / "templates" / "enterprisecatalog" / "hooks"
for task_name in ["mysql", "enterprisecatalog", "lms"]:
    task_path = hooks_dir / task_name / "init"
    with open(task_path, encoding="utf-8") as task_file:
        tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item((task_name, task_file.read()))
