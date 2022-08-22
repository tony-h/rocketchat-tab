# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.conf import settings
from .views import RocketChatView


urlpatterns = (
    url(
        r'courses/{}/chat$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        RocketChatView.as_view(),
        name='rocketchat_view',
    ),
)
