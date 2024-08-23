"""Project utils."""


def get_cache_key(value: str) -> str:
    """Get cache key for the value."""
    return f"djangocms_jq_src:{value}"
