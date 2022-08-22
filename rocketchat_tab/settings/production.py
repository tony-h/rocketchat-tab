# -*- coding: utf-8 -*-


def plugin_settings(settings):
    """
    Defines rocketchat-tab settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.ROCKETCHAT_BASE_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'ROCKETCHAT_BASE_URL',
        settings.ROCKETCHAT_BASE_URL
    )
    settings.ROCKETCHAT_ADMIN_TOKEN = getattr(settings, 'ENV_TOKENS', {}).get(
        'ROCKETCHAT_ADMIN_TOKEN',
        settings.ROCKETCHAT_ADMIN_TOKEN
    )
    settings.ROCKETCHAT_ADMIN_USER_ID = getattr(settings, 'ENV_TOKENS', {}).get(
        'ROCKETCHAT_ADMIN_USER_ID',
        settings.ROCKETCHAT_ADMIN_USER_ID
    )
