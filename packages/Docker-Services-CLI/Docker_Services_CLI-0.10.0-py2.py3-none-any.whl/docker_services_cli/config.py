# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Docker-Services-CLI is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration module.

Configuration values (e.g. service configuration) need to be set through
environment variables. However, sane defaults are provided below.

The list of services to be configured is taken from ``SERVICES``. Each one
should contain a ``<SERVICE_NAME>_VERSION`` variable.

Service's version are treated slightly different:

- If the variable is not found in the environment, it will use the set default.
- If the variable is set with a version number (e.g. 10, 10.7) it will use
  said value.
- If the variable is set with a string point to one of the configured
  ``latests`` it will load the value of said ``latest`` and use it.

This means that the environment set/load logic will first set the default
versions before loading a given service's version.
"""

DOCKER_SERVICES_FILEPATH = "docker-services.yml"
"""Docker services file default path."""

# Elasticsearch
ELASTICSEARCH = {
    "ELASTICSEARCH_VERSION": "ELASTICSEARCH_7_LATEST",
    "DEFAULT_VERSIONS": {
        "ELASTICSEARCH_7_LATEST": "7.10.2",  # the last of the OSS versions (https://github.com/elastic/elasticsearch/issues/58303)
    },
}
"""Elasticsearch service configuration."""

# Opensearch
OPENSEARCH = {
    "OPENSEARCH_VERSION": "OPENSEARCH_2_LATEST",
    "DEFAULT_VERSIONS": {
        "OPENSEARCH_1_LATEST": "1.3.18",
        "OPENSEARCH_2_LATEST": "2.16.0",
    },
}
"""Opensearch service configuration."""

# PostgreSQL
POSTGRESQL = {
    "POSTGRESQL_VERSION": "POSTGRESQL_14_LATEST",
    "DEFAULT_VERSIONS": {
        "POSTGRESQL_11_LATEST": "11.15",  # 11.21 is published on DockerHub ONLY with `-<debian-version>`, which breaks `invenio-cli`
        "POSTGRESQL_12_LATEST": "12.16",
        "POSTGRESQL_13_LATEST": "13.12",
        "POSTGRESQL_14_LATEST": "14.9",
        "POSTGRESQL_15_LATEST": "15.4",
    },
    "CONTAINER_CONFIG_ENVIRONMENT_VARIABLES": {
        "POSTGRESQL_USER": "invenio",
        "POSTGRESQL_PASSWORD": "invenio",
        "POSTGRESQL_DB": "invenio",
    },
    "CONTAINER_CONNECTION_ENVIRONMENT_VARIABLES": {
        "db": {
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://invenio:invenio@localhost:5432/invenio"
        }
    },
}
"""Postgresql service configuration."""

# MySQL
MYSQL = {
    "MYSQL_VERSION": "MYSQL_8_LATEST",
    "DEFAULT_VERSIONS": {"MYSQL_5_LATEST": "5.7", "MYSQL_8_LATEST": "8.1"},
    "CONTAINER_CONFIG_ENVIRONMENT_VARIABLES": {
        "MYSQL_USER": "invenio",
        "MYSQL_PASSWORD": "invenio",
        "MYSQL_DB": "invenio",
        "MYSQL_ROOT_PASSWORD": "invenio",
    },
    "CONTAINER_CONNECTION_ENVIRONMENT_VARIABLES": {
        "db": {
            "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://invenio:invenio@localhost:3306/invenio"
        }
    },
}
"""MySQL service configuration."""

REDIS = {
    "REDIS_VERSION": "REDIS_7_LATEST",
    "DEFAULT_VERSIONS": {"REDIS_6_LATEST": "6", "REDIS_7_LATEST": "7"},
    "CONTAINER_CONNECTION_ENVIRONMENT_VARIABLES": {
        "mq": {"BROKER_URL": "redis://localhost:6379/0"},
        "cache": {"CACHE_TYPE": "redis"},
    },
}
"""Redis service configuration."""

RABBITMQ = {
    "RABBITMQ_VERSION": "RABBITMQ_3_LATEST",
    "DEFAULT_VERSIONS": {"RABBITMQ_3_LATEST": "3"},
    "CONTAINER_CONNECTION_ENVIRONMENT_VARIABLES": {
        "mq": {"BROKER_URL": "amqp://localhost:5672//"}
    },
}
"""RabbitMQ service configuration."""

SERVICES = {
    "elasticsearch": ELASTICSEARCH,
    "opensearch": OPENSEARCH,
    "postgresql": POSTGRESQL,
    "mysql": MYSQL,
    "redis": REDIS,
    "rabbitmq": RABBITMQ,
}
"""List of services to configure."""

SERVICES_ALL_DEFAULT_VERSIONS = {
    **ELASTICSEARCH.get("DEFAULT_VERSIONS", {}),
    **OPENSEARCH.get("DEFAULT_VERSIONS", {}),
    **POSTGRESQL.get("DEFAULT_VERSIONS", {}),
    **REDIS.get("DEFAULT_VERSIONS", {}),
    **MYSQL.get("DEFAULT_VERSIONS", {}),
    **RABBITMQ.get("DEFAULT_VERSIONS", {}),
}
"""Services default latest versions."""

SERVICE_TYPES = {
    "search": ["opensearch", "elasticsearch"],
    "db": ["mysql", "postgresql"],
    "cache": [
        "redis",
    ],
    "mq": ["rabbitmq", "redis"],
}
"""Types of offered services."""
