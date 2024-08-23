"""App settings."""

from app_utils.app_settings import clean_setting

METENOX_ADMIN_NOTIFICATIONS_ENABLED = clean_setting(
    "METENOX_ADMIN_NOTIFICATION_ENABLED", True
)
"""Whether admins will get notifications about important events like
when someone adds a new owner.
"""
