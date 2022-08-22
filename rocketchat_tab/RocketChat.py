# -*- coding: utf-8 -*-


import uuid
from django.conf import settings

from .RocketChatError import RocketChatError
from .ApiRequest import ApiRequest

# Group API calls
# groups.info       https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/info
# groups.create     https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/groups-endpoints/create
# groups.members    https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/groups-endpoints/members
# groups.invite     https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/groups-endpoints/invite
# groups.addowner   https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/addowner

## User API calls
# users.info        https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/users-endpoints/get-users-info
# users.create      https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/users-endpoints/create-user-endpoint

# TODO
# Check if user already in the room
# Add the room prefix to the settings file
# Localization and translate messages

class RocketChat(object):

    # Constructor
    def __init__(self, edx_info):

        # Error checking
        if (not isinstance(edx_info, dict)):
            error = "{'ArgError': 'Course data was not set'}"
            message = "Error obtaining course data."
            raise RocketChatError(error, message)

        course_id = edx_info.get('course', {}).get('key')
        
        if(course_id is None):
            error = "{'ArgError': 'Course key was not set'}"
            message = "Error obtaining course data."
            raise RocketChatError(error, message)
        
        self.edx_info = edx_info
        self.group_name = self.build_group_name(course_id)
        self.user_info = edx_info['user']
        self.api_call = ApiRequest()
        
        # verify user enrollment        
        if (not self.user_info['is_enrolled']):
            error = "{{'ValidationError':'User {0} is not enrolled in the course.'}}".format(self.user_info['username'])
            message = "Enrollment in course '{0}' is required to access the group chat.".format(course_id)
            raise RocketChatError(error, message)

        # change user to lowercase to prevent this error:
        #   Fi_Last is already in use :( [error-field-unavailable]
        #   Error data: {"success": false, "error": "FiLast is already in use :( [error-field-unavailable]"}
        # Fi_Last --> fi_last
        self.user_info['username'] = str(self.user_info['username']).lower()


    def build_group_name(self, course_id):
        """Gets the room/group name from the course ID

        Args:
            course_id (string): The course ID associated with a RocketChat room

        Returns:
            string: The room name in the format of: edx-IT_IS-NAU_01-2021_2022
                    platform-SCHOOL-COURSE_ID-YEAR
        """

        try:

            course_parts = course_id.split(':')
            course_id = course_parts[1]
            
            # Only replace + with - in the course ID. All other chars should remain
            # IT_IS+ICT_01+2022_SUMMER --> IT_IS-ICT_01-2022_SUMMER
            course_id = course_id.replace('+', '-')

            # Alternatively, replace all non-alphanumeric characters with a '-': 
            # course = re.sub('[^A-Za-z0-9]+', '-', course_id)
            
            group_name = "{}-{}".format("edx", course_id)
            return group_name

        except Exception as e:
            
            error = "{{'ArgError': 'Course ID \"{0}\" is not valid.', 'Exception': {1} }}".format(course_id, e)
            message = "Error parsing course data."
            raise RocketChatError(error, message)


    def get_room_url(self):
        """Gets the room URL

        Returns:
            string: The URL to the RocketChat room
        """
        
        return "{0}group/{1}".format(settings.ROCKETCHAT_BASE_URL, self.group_name)


    def get_group_info(self):
        """Gets group info from the RocketChat room name

        Returns:
            dict: A JSON dict containing the room information
                If room does exist, returns: {'errorType': 'error-room-not-found'}
        """
        
        # https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/info
        # Get group info. If does not exist, create it

        api_url = '{0}/api/v1/groups.info?roomName={1}'.format \
            (settings.ROCKETCHAT_BASE_URL, self.group_name)

        # Get the room info
        json_resp = self.api_call.get(api_url)

        # Check for an unsuccessful response 
        # JSON response on failure {"success": false, "error": "The room...", "errorType": "error-room-not-found"}
        if(json_resp.get('success') == False):
            # Attempt to create the room and then try again.
            json_resp = self.create_group()
        
        self.check_json_for_success(json_resp)
        return json_resp


    def create_group(self):
        """Creates a RocketChat group/room

        Returns:
            dict: A JSON dict containing the group information
        """

        json_string = '{{ "name": "{0}" }}'.format(self.group_name)

        # https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/groups-endpoints/create
        api_url = '{0}/api/v1/groups.create'.format \
            (settings.ROCKETCHAT_BASE_URL)

        json_resp = self.api_call.post(api_url, json_string)
        self.check_json_for_success(json_resp)
        return json_resp


    def add_user_to_group(self, room_id, user_id):
        """Adds a user to the RocketChat group

        Args:
            room_id (string): Room/group ID to add the user to
            user_id (string): User ID to add to the room

        Returns:
            dict: JSON dict of the group the user was added to
        """

        # https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/invite
        json_string = '{{ "roomId": "{0}", "userId": "{1}" }}'.format(room_id, user_id)

        api_url = '{0}/api/v1/groups.invite'.format \
            (settings.ROCKETCHAT_BASE_URL)

        group_info = self.api_call.post(api_url, json_string)

        # Add the user as an owner if flag is set
        if(self.user_info['is_staff']):
            
            # There is no easy to check for the group owner. Instead, add the user as owner,
            #   but don't evaluate response (silently fail if the user is already the owner)
            # https://github.com/RocketChat/Rocket.Chat/issues/12870
            # Error data: {"success": false, "error": 
            #   "User is already an owner [error-user-already-owner]", 
            #   "errorType": "error-user-already-owner", 
            #   "details": {"method": "addRoomOwner"}}
            
            # https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/addowner
            api_url = '{0}/api/v1/groups.addOwner'.format \
                (settings.ROCKETCHAT_BASE_URL)
            self.api_call.post(api_url, json_string)

        # Validate and return the initial response
        self.check_json_for_success(group_info)
        return group_info


    def get_user_info(self):
        """Gets ther RocketChat user's info from the username. Creates the user
            using their edX user info if they do not exist in the system.

        Returns:
            dict: JSON dict containing the user's information 
        """

        # https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/users-endpoints/get-users-info
        api_url = '{0}/api/v1/users.info?username={1}'.format \
            (settings.ROCKETCHAT_BASE_URL, self.user_info['username'])

        # Attempt to get the user info
        json_resp = self.api_call.get(api_url)

        # Check for an unsuccessful response 
        # JSON response on failure {"success":false,"error":"User not found."}
        if(json_resp.get('success') == False):
            # Attempt to create the user and then try again.
            return self.create_user()
        else:
            self.check_json_for_success(json_resp)
            return json_resp


    def create_user(self):
        """Creates a RocketChat user

        Returns:
            dict: A JSON dict containing the new user information

        API call required
        curl -H "X-Auth-Token: $TOKEN" \
            -H "X-User-Id: $USER_ID" \
            -H "Content-type:application/json" \
            https://my.chat.site/api/v1/users.create \
            -d '{ "username": "someuser",  "email": "someuser@example.com", "password": "uChqlORdB5", 
                "name": "Some User", "active": true, "verified": true, "requirePasswordChange": false,
                "sendWelcomeEmail": false }'

        """
        username = self.user_info['username']
        email = self.user_info['email']
        name = self.user_info['display_name']
        # Generate a random password (users only login using OAuth)
        password = uuid.uuid4().hex

        json_string = '{{ "username": "{0}",  "email": "{1}", "password": "{2}", \
                "name": "{3}", "active": true, "verified": true, "requirePasswordChange": false, \
                "sendWelcomeEmail": false }}'.format(
                    username, email, password, name)

        # https://developer.rocket.chat/reference/api/rest-api/endpoints/team-collaboration-endpoints/groups-endpoints/create
        api_url = '{0}/api/v1/users.create'.format \
            (settings.ROCKETCHAT_BASE_URL)

        json_resp = self.api_call.post(api_url, json_string)
        self.check_json_for_success(json_resp)
        return json_resp


    def check_json_for_success(self, json):

        # Response types:
        # - Connection failure: {"status": "Failure"}
        # - Invalid content: {"status": "Failure"}
        # - Not logged in: {'status': 'error'}

        # - Room not found: {'success': False}
        # - Request successfull: {'success': True}

        # Throw exception if a failure is found

        # Response type one: {'success': Boolean}
        if(json.get('success') == 'True' or json.get('success') == True ):
            return
        elif('success' in json):
            # Success is set, but is False
            # Some other error occured. Display error message
            
            message = json.get('error')
            raise RocketChatError(json, message)

        # Response type two (connection or access erorr): {'status': Value}
        elif('status' in json):

            message = "An error occurred connecting to the server"
            raise RocketChatError(json, message)

        else:

            # Uknown JSON response
            raise RocketChatError(json)
