# syntax=docker/dockerfile:1.4
# Build enterprise-catalog with the same Python/runtime stack as Open edX Teak+
FROM docker.io/ubuntu:22.04 AS base
LABEL maintainer="Sofiane Bebert <s.bebert:diceytech.co.uk>"

# Base system deps (cached) and locale
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y curl git-core language-pack-en \
    build-essential libffi-dev libmysqlclient-dev libxml2-dev libxslt-dev libjpeg-dev libssl-dev \
    pkg-config libsqlite3-dev libbz2-dev liblzma-dev media-types mailcap
ENV LC_ALL en_US.UTF-8

# Non-root app user
ARG APP_USER_ID=1000
RUN if [ "$APP_USER_ID" = 0 ]; then echo "app user may not be root" && false; fi
RUN useradd --home-dir /openedx --create-home --shell /bin/bash --uid ${APP_USER_ID} app
USER ${APP_USER_ID}

# Clone the enterprise-catalog repo at the configured ref
ARG ENTERPRISE_CATALOG_REPOSITORY={{ ENTERPRISECATALOG_REPOSITORY }}
ARG ENTERPRISE_CATALOG_VERSION={{ ENTERPRISECATALOG_REPOSITORY_VERSION }}
RUN mkdir -p /openedx/enterprise-catalog && \
    git clone $ENTERPRISE_CATALOG_REPOSITORY --branch $ENTERPRISE_CATALOG_VERSION --depth 1 /openedx/enterprise-catalog
WORKDIR /openedx/enterprise-catalog

# Provide an empty config file (required by production settings)
RUN echo "{}" > /openedx/config.yml
ENV ENTERPRISE_CATALOG_CFG /openedx/config.yml

# Install Python via pyenv (matches upstream images)
ARG PYTHON_VERSION={{ ENTERPRISECATALOG_PYTHON_VERSION }}
ENV PYENV_ROOT=/opt/pyenv
USER root
RUN git clone https://github.com/pyenv/pyenv $PYENV_ROOT --branch v2.3.36 --depth 1
RUN $PYENV_ROOT/bin/pyenv install $PYTHON_VERSION
USER app

# Virtualenv and tooling
RUN $PYENV_ROOT/versions/$PYTHON_VERSION/bin/python -m venv /openedx/venv
ENV PATH=/openedx/venv/bin:$PATH
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install \
    setuptools==77.0.0 pip==25.0.1 wheel==0.45.1

# Install app dependencies (cached)
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install -r requirements/production.txt
# Add redis cache backend
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install django-redis==5.4.0

FROM base AS openedx-enterprise-catalog

# uWSGI for the web process
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install uwsgi==2.0.28

{{ patch("enterprise-catalog-dockerfile-post-python-requirements") }}

# Collect static assets
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD uwsgi \
    --static-map /static=/openedx/enterprise-catalog/enterprise_catalog/assets \
    --http 0.0.0.0:8000 \
    --thunder-lock \
    --single-interpreter \
    --enable-threads \
    --processes=2 \
    --buffer-size=8192 \
    --wsgi-file enterprise_catalog/wsgi.py
