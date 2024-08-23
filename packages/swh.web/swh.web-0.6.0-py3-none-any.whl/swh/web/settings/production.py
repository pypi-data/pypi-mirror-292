# Copyright (C) 2017-2024  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""
Django production settings for swh-web.
"""

import django

from swh.web.config import DEFAULT_CONFIG

from .common import (
    CACHES,
    DEBUG,
    MIDDLEWARE,
    REST_FRAMEWORK,
    SECRET_KEY,
    WEBPACK_LOADER,
    swh_web_config,
)
from .common import *  # noqa

MIDDLEWARE += [
    "swh.web.utils.middlewares.HtmlMinifyMiddleware",
]

if swh_web_config.get("throttling", {}).get("cache_uri"):
    cache_backend = "django.core.cache.backends.memcached.MemcachedCache"
    if django.VERSION[:2] >= (3, 2):
        cache_backend = "django.core.cache.backends.memcached.PyMemcacheCache"
    CACHES.update(
        {
            "default": {
                "BACKEND": cache_backend,
                "LOCATION": swh_web_config["throttling"]["cache_uri"],
            },
            "rate-limit": {
                "BACKEND": cache_backend,
                "LOCATION": swh_web_config["throttling"]["cache_uri"],
            },
        }
    )

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# We're going through seven (or, in that case, 2) proxies thanks to Varnish
REST_FRAMEWORK["NUM_PROXIES"] = 2

db_conf = swh_web_config["production_db"]
if db_conf.get("name", "").startswith("postgresql://"):
    # poor man's support for dsn connection string...
    import psycopg2

    with psycopg2.connect(db_conf.get("name")) as cnx:
        dsn_dict = cnx.get_dsn_parameters()

    db_conf["name"] = dsn_dict.get("dbname")
    db_conf["host"] = dsn_dict.get("host")
    db_conf["port"] = dsn_dict.get("port")
    db_conf["user"] = dsn_dict.get("user")
    db_conf["password"] = dsn_dict.get("password")


# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_conf.get("name"),
        "HOST": db_conf.get("host"),
        "PORT": db_conf.get("port"),
        "USER": db_conf.get("user"),
        "PASSWORD": db_conf.get("password"),
    }
}

WEBPACK_LOADER["DEFAULT"]["CACHE"] = not DEBUG

if SECRET_KEY == DEFAULT_CONFIG["secret_key"][-1]:
    raise ValueError(
        "The SECRET_KEY value matches the development default, "
        "check the contents of SWH_CONFIG_FILENAME"
    )

browse_content_rate_limit = swh_web_config.get("browse_content_rate_limit", {})
RATELIMIT_ENABLE = browse_content_rate_limit.get("enabled", True)
