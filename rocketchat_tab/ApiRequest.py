# -*- coding: utf-8 -*-


import json, requests
from requests.structures import CaseInsensitiveDict

from django.conf import settings

class ApiRequest(object):

    def post(self, url, data, pretty_print=False):
        """
        Makes a POST API call to a Rocket Chat instance.

        :param url: The complete endpoint
            For example: https://my.chat.site/api/v1/groups.create
        :param data: JSON data to send with the POST request
            For example: { "name": "NAU_01-2021_2022" }
        :param pretty_print: Specifies that the JSON should return in a 
            human-readable string for display
        
        :return: a json.loads() object; Type Dict -OR- string if used 'pretty_print'
        """

        # curl -H "X-Auth-Token: some-token" \
        #      -H "X-User-Id: some-id" \
        #      -H "Content-type:application/json" \
        #      https://my.chat.site/api/v1/groups.create \
        #      -d '{ "name": "NAU_01-2021_2022" }'

        # See https://reqbin.com/req/python/c-dwjszac0/curl-post-json-example

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["X-Auth-Token"] = settings.ROCKETCHAT_ADMIN_TOKEN
        headers["X-User-Id"] = settings.ROCKETCHAT_ADMIN_USER_ID
        headers["Content-type"] = "application/json"
        
        try:
            # Make the call, handle the exception
            resp = requests.post(url, headers=headers, data=data)
            return self.verify_api_request(resp, url, pretty_print)
            
        except requests.exceptions.RequestException as e:
            # Oops...the service is probably down
            return self.handle_request_exception(e)



    def get(self, url, pretty_print=False):
        """
        Makes a GET API call to a Rocket Chat instance.

        :param url:     The complete endpoint
                    For example: https://my.chat.site//api/v1/groups.info?roomName=NAU_01-2021_2022
        :param pretty_print: Specifies that the JSON should return in a 
            human-readable string for display
        
        :return: a json.loads() object; Type Dict -OR- string if used 'pretty_print'
        """

        # curl -H "X-Auth-Token: some-token" \ 
        #      -H "X-User-Id: some-id" \ 
        #       https://my.chat.site//api/v1/groups.info?roomName=NAU_01-2021_2022

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["X-Auth-Token"] = settings.ROCKETCHAT_ADMIN_TOKEN
        headers["X-User-Id"] = settings.ROCKETCHAT_ADMIN_USER_ID
        
        try:
            # Make the call, handle the exception
            resp = requests.get(url, headers=headers)
            return self.verify_api_request(resp, url, pretty_print)

        except requests.exceptions.RequestException as e:
            # Oops...the service is probably down
            return self.handle_request_exception(e)

    def verify_api_request(self, resp, url, pretty_print):
        """Verfies the response the request and returns a verified JSON object

        Args:
            resp (requests.Response object): HTTP response object of the request 
            url (string): The URL of the request
            :param pretty_print: Specifies that the JSON should return in a 
                human-readable string for display
        
        Returns:
            :return: a json.loads() object; Type Dict -OR- string if used 'pretty_print'
        """

        # If response is valid JSON, return object
        if (self.is_json(resp.content)):
            # Convert the JSON string to a dictionary
            json_object = json.loads(resp.content)

            if (pretty_print):
                # Return human readable output
                return json.dumps(json_object, indent=2)
            else:
                # Return the dictionary object if not for display
                return json_object
        else:
            # The response was valid, but did not sent back a JSON object
            json_error = '{{"status": "Failure", \
                "message": "The API returned invalid JSON. Verify the URL:\\n{0}"}}'.format(url)

            # Note: Must use double {{ }} when using .format with a JSON string
            # https://stackoverflow.com/questions/16356810/string-format-a-json-string-gives-keyerror
                
            return json.loads(json_error)


    def is_json(self, json_string):
        """
        Returns true or false if the text string is valid JSON.

        :param json_string: A text string to test for valid JSON

        :return: 
            bool: True if valid JSON. Otherwise, returns False
            https://stackoverflow.com/questions/5508509/how-do-i-check-if-a-string-is-valid-json-in-python#answer-20725965
        """
        try:
            json.loads(json_string)
        except ValueError as e:
            return False
        return True


    def handle_request_exception(self, e):
        """
        Handles a RequestException
        
        Args:
            e (exception): The exception to display the message for

        Returns:
            dict: JSON object describing the error
        """

        json_error = '{{"status": "Failure", \
            "message": "Error connecting to the Chat server", \
            "exception": "{0}"}}'.format(str(e))

        if(self.is_json(json_error)):
            return json.loads(json_error)
        else:
            json_error = '{"status": "Failure", \
                "message": "Error connecting to the Chat server"}'
            
            return json.loads(json_error)
