# -*- coding: utf-8 -*-


"""
Common settings for rocketchat-tab project.
"""

def plugin_settings(settings):
    """
    Backend settings
    """
    settings.ROCKETCHAT_BASE_URL = 'https://your-rocketchat-instance/'
    settings.ROCKETCHAT_ADMIN_TOKEN = "your-admin-token"
    settings.ROCKETCHAT_ADMIN_USER_ID = "your-user-id"
