# -*- coding: utf-8 -*-


import json

class RocketChatError(Exception):
    """Exception raised for errors connecting to RocketChat.

    Attributes:
        json_dict -- the json dict data with the error
        message -- explanation of the error
    """

    def __init__(self, json_dict, message="There was a unexpected error with the chat server."):
        
        json_str = ""
        
        if(isinstance(json_dict, dict)):
            json_str = json.dumps(json_dict)
        elif(isinstance(json_dict, str)):
            json_str = json_dict
        else:
            json_str = str(json_dict)
        
        self.message = message + "\nError data: " + json_str
        self.message = "\n{0}\n".format(self.message)
        super().__init__(self.message)
