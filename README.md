# rocketchat-tab for Open edX

The Open edX module adds a new course tab that integrates a Rocket.Chat room.

To display the Chat tab after installing the module, add the module name `rocketchat-tab` to the *Advanced Module List* (`Settings -> Advanced Settings`).

    [
        "rocketchat-tab"
    ]

**Please note**

- These instructions are written for [Tutor](https://docs.tutor.overhang.io/) (the Docker-based Open edX distribution).
- The Rocket.Chat login assumes SSO (OAuth2, SAML, etc.) will be used because the accounts are created and validated automatically using random passwords.
- The new tab is accessible to all courses once installed because the `/chat` URL becomes registered globally. Adding the module name to the *Advanced Module List* shows the new tab in the list.

## Features

When the tab is opened by an enrolled user, the tab code:

1. Creates a new Rocket.Chat room using the course ID
2. Creates and validates a new Rocket.Chat user account using the user's Open edX username, email address, and display name
3. Adds the user to the Rocket.Chat room
4. Displays the room

## Install

- Development:

      cd $(tutor config printroot)/env/build/openedx/requirements
      git clone https://github.com/tony-h/rocketchat-tab
      echo "-e ./rocketchat-tab/" >> private.txt
    
      # Stop and start Tutor dev to rebuild the images to include the new tab
      tutor dev stop && tutor dev start -d

- Production:

      cd $(tutor config printroot)/env/build/openedx/requirements
      echo "git+https://github.com/tony-h/rocketchat-tab" >> private.txt

      # Build the images and then restart Tutor
      tutor images build openedx
      tutor local stop
      tutor local start -d

## Configuration

Edit *settings/common.py* to specify your Rocket.Chat data.

    settings.ROCKETCHAT_BASE_URL = 'https://your.rocketchat.instance/'
    settings.ROCKETCHAT_ADMIN_TOKEN = "your-admin-token"
    settings.ROCKETCHAT_ADMIN_USER_ID = "your-user-id"

## Production

Create a Tutor plugin to specify the Rocket.Chat environmental variables.

Here is the plugin template for `$(tutor plugins printroot)/rocketchat-auth.py`

    # Place this code in a new Tutor plugin file, such as 'rocketchat-auth.py'
    from tutor import hooks
    
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            """
    # RocketChat auth tokens
    ROCKETCHAT_BASE_URL = 'https://your.rocketchat.instance/'
    ROCKETCHAT_ADMIN_TOKEN = "your-admin-token"
    ROCKETCHAT_ADMIN_USER_ID = "your-user-id"
    """    )
    )
