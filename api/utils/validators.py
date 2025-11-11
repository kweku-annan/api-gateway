#!/usr/bin/env python3
"""Utility functions for validating request data"""

def validate_notification_data(data):
    """"
    Validates requests data for notifications.
    -- Checks for required fields and correct data types.
    """
    if not data.get("user_id"):
        return "'user_id' is required.", False
    if not isinstance(data.get("user_id"), str):
        return "'user_id' must be a string.", False
    if not data.get("template_id"):
        return "'template_id' is required.", False
    if not isinstance(data.get("template_id"), str):
        return "'template_id' must be a string.", False

    return None