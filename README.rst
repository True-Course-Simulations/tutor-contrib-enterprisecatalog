enterprisecatalog plugin for `Tutor <https://docs.tutor.overhang.io>`__
========================================================================

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

- ``ENTERPRISECATALOG_DOCKER_IMAGE``: pull an existing image (default: official ``openedx/enterprise-catalog`` tag matching your Open edX release).
- ``ENTERPRISECATALOG_BUILD_IMAGE``: set to ``true`` to build locally instead.
- ``ENTERPRISECATALOG_REPOSITORY`` / ``ENTERPRISECATALOG_REPOSITORY_VERSION``: source repo/ref when building.
- ``ENTERPRISECATALOG_HOST``: public hostname (default: ``enterprisecatalog.<LMS_HOST>``).

Kubernetes support
------------------

K8s manifests are patched for deployment/service/job and a configmap for settings. Render with:

.. code-block:: bash

    tutor k8s render --extra-plugin enterprisecatalog

License
-------

This software is licensed under the terms of the AGPLv3.
