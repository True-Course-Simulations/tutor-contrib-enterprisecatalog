enterprisecatalog plugin for `Tutor <https://docs.tutor.overhang.io>`__
========================================================================

Original plugin by Dicey-Tech. Updated and maintained by Cannon Smith for Tutor v16+ compatibility.

Tutor plugin that deploys the Open edX Enterprise Catalog service alongside your LMS/CMS.

Installation
------------

Install from source:

.. code-block:: bash

    pip install git+https://github.com/Dicey-Tech/tutor-contrib-enterprisecatalog

Then enable the plugin:

.. code-block:: bash

    tutor plugins enable enterprisecatalog

Usage
-----

Generate configuration and environment with the plugin enabled:

.. code-block:: bash

    tutor config save --extra-plugin enterprisecatalog
    tutor local quickstart  # or `tutor dev start` in dev mode

Key settings (override in ``config.yml`` or via ``TUTOR_`` env vars):

- ``ENTERPRISECATALOG_DOCKER_IMAGE``: optional external image to pull; if empty, the plugin builds ``ENTERPRISECATALOG_BUILT_IMAGE`` from ``ENTERPRISECATALOG_REPOSITORY``.
- ``ENTERPRISECATALOG_REPOSITORY`` / ``ENTERPRISECATALOG_REPOSITORY_VERSION``: source repo/ref when building.
- ``ENTERPRISECATALOG_HOST``: public hostname (default: ``enterprisecatalog.<LMS_HOST>``).
- ``ENTERPRISECATALOG_OAUTH2_SECRET_*``: separate dev/prod secrets for client-credentials and SSO apps seeded during init.

Enterprise Catalog admin users
------------------

Use the bundled management commands inside the Enterprise Catalog service
to create or promote superadmins. Examples for local Tutor:

.. code-block:: shell

    # Create or update a superadmin (SSO-only login)
    tutor local run enterprisecatalog ./manage.py create_enterprisecatalog_superadmin \
        --username dev --email dev@example.com --no-password

    # Create a superadmin with a local password
    tutor local run enterprisecatalog ./manage.py create_enterprisecatalog_superadmin \
        --username ecadmin --email ecadmin@example.com --password 'SomeStrongPassword123'

    # Promote an existing SSO user after their first login
    tutor local run enterprisecatalog ./manage.py promote_enterprisecatalog_superadmin \
        --username dev --email dev@example.com

Omit arguments to be prompted interactively. In Kubernetes environments,
replace ``tutor local run`` with the equivalent ``tutor k8s exec enterprisecatalog --`` command.


Kubernetes support
------------------

K8s manifests are patched for deployment/service/job and a configmap for settings. Render with:

.. code-block:: bash

    tutor k8s render --extra-plugin enterprisecatalog

License
-------

This software is licensed under the terms of the AGPLv3.
