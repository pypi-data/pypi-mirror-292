"""Source fetcher."""

from typing import Any, Optional

import jq  # type: ignore[import-not-found]
import requests
from django.conf import settings
from django.core.cache import cache

from .utils import get_cache_key

ERROR_CODE = "__ERROR__"


class SourceIsNotAvailable(Exception):
    """Source is not available."""


def load_source(url: str) -> dict[str, Any]:
    """Load JSON data from source."""
    timeout = getattr(settings, "DJANGOCMS_JQ_LOAD_TIMEOUT", 6)
    verify = getattr(settings, "DJANGOCMS_JQ_VERIFY", True)
    response = requests.get(url, timeout=timeout, verify=verify)
    response.raise_for_status()
    return response.json()


def get_data(url: str) -> dict[str, Any]:
    """Get cached data or load data from the source."""
    key = get_cache_key(url)
    data = cache.get(key)
    if data is None:
        timeout = getattr(settings, "DJANGOCMS_JQ_CACHE_TIMEOUT", 600)  # 10 min.
        error_timeout = getattr(settings, "DJANGOCMS_JQ_ERROR_CACHE_TIMEOUT", 60)  # 1 min.
        try:
            data = load_source(url)
            cache.set(key, data, timeout)
        except requests.RequestException:
            cache.set(key, ERROR_CODE, error_timeout)
            raise SourceIsNotAvailable
    else:
        if data == ERROR_CODE:
            raise SourceIsNotAvailable
    return data


def get_value(url: str, query: str, fetcher: str) -> Optional[Any]:
    """Get JSON value from url."""
    try:
        data = get_data(url)
    except SourceIsNotAvailable:
        return None
    try:
        return getattr(jq.compile(query).input(data), fetcher)()
    except ValueError:
        return None
