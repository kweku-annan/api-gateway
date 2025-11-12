"""
Additional validation utilities
"""

import re
from typing import Optional


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Validate if string is a valid UUID

    Args:
        uuid_string: String to validate

    Returns:
        bool: True if valid UUID, False otherwise
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def sanitize_template_variables(variables: dict) -> dict:
    """
    Sanitize template variables to prevent injection

    Args:
        variables: Dictionary of template variables

    Returns:
        Sanitized variables dictionary
    """
    sanitized = {}
    for key, value in variables.items():
        # Ensure key and value are strings
        key_str = str(key).strip()
        value_str = str(value).strip()

        # Basic sanitization (remove potential script tags)
        value_str = re.sub(r'<script[^>]*>.*?</script>', '', value_str, flags=re.IGNORECASE)

        sanitized[key_str] = value_str

    return sanitized