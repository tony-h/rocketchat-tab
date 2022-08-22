# -*- coding: utf-8 -*-

from django.conf import settings
from lms.djangoapps.courseware.courses import get_course_with_access
from django.template.loader import render_to_string
from web_fragments.fragment import Fragment
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from xblock.fields import Scope
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.courseware.access import has_access
from common.djangoapps.student.models import CourseEnrollment
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_noop

from .RocketChatError import RocketChatError
from .RocketChat import RocketChat

# Create your views here.


class RocketChatView(EdxFragmentView):
    def render_to_fragment(self, request, course_id, **kwargs):

        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, "load", course_key)
        user = request.user
        display_name_course = course.display_name
        
        staff_access = bool(has_access(request.user, 'staff', course))
        user_is_enrolled = CourseEnrollment.is_enrolled(user, course.id)

        # Check for AnonymousUser user
        if(isinstance(user, AnonymousUser)):
            user_email = ""
            user_display_name = ""
        else:
            profile = user.profile
            user_email = user.email
            user_display_name = profile.name
            # Additional profile fields
            # https://github.com/openedx/edx-platform/blob/master/common/djangoapps/student/models.py
        
        # For rocket_chat.html
        context = {
            "course": course,           # must in the root level to avoid "proctored exam error"
            "show_chat_frame": True,
            "user_info": {
                "username": user.username,
                "email": user_email,
                "display_name": user_display_name,
                "is_staff": staff_access,
                "is_enrolled": user_is_enrolled,
            },
            "course_info": {
                "course": course,
                "name": display_name_course,
                "key": course_key,
            },
            "rocket_chat": {
                "base_url": settings.ROCKETCHAT_BASE_URL,
                "room_url": settings.ROCKETCHAT_BASE_URL,
                "error": "",
            }
        }

        # For RocketChat.py
        edx_info = {
            "user": context['user_info'],
            "course": {
                "name": display_name_course,
                "key": course_id,
            }
        }
          
        try:
            # Set the room_url if everything processed correctly
            context["rocket_chat"]['room_url'] = self.init_rocket_chat_room(edx_info)
        except RocketChatError as e:
            # Oops
            # Set error field and use the base RocketChat URL
            context["rocket_chat"]['error'] = str(e)

        html = render_to_string(
            'rocket_chat/rocket_chat.html', context, )

        fragment = Fragment(html)
        return fragment


    def init_rocket_chat_room(self, edx_info):
        """Initializes the chat room using the edX course and user information
            - Creates the room (if it does not exist)
            - Creates the user (if they do not exist)
            - Add the user to the room

        Args:
            edx_info (dict): The essential user and course information

        Returns:
            string: The URL to the RocketChat room
        """
        
        rocketChat = RocketChat(edx_info)
        
        # 1) Get the room info
        #    The room will be created if it does not exist
        group_info = rocketChat.get_group_info()

        # 2) Get the user info and add user to group
        #    The user will be created if they do not exist
        user_info = rocketChat.get_user_info()

        # 3) Add the user to the group
        #   is_staff users will be added as room owers
        user_id = user_info.get('user', {}).get('_id')
        group_id = group_info.get('group', {}).get('_id')
        rocketChat.add_user_to_group(group_id, user_id)
        
        return rocketChat.get_room_url()
