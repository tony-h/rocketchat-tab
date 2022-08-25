# rocketchat-tab for Open edX

The Open edX module adds a new course tab that integrates a Rocket.Chat room.

Add the module name `rocketchat-tab` to the *Advanced Module List* (`Settings -> Advanced Settings`) to display the Chat tab after installing the module.

``` json
[
    "rocketchat-tab"
]
```

**Please note**

- These instructions are written for [Tutor](https://docs.tutor.overhang.io/) (the Docker-based Open edX distribution).
- The Rocket.Chat login assumes SSO (OAuth2, SAML, etc.) will be used because the accounts are created and validated automatically using random passwords.
- The new tab is accessible to all courses once installed because the `/chat` URL becomes registered globally. Adding the module name to the *Advanced Module List* shows the new tab in the list.

## Features

When the tab is opened by an enrolled user, the chat module:

1. Creates a new Rocket.Chat room using the course ID
2. Creates and validates a new Rocket.Chat user account using the user's Open edX username, email address, and display name
3. Adds the user to the Rocket.Chat room
4. Displays the room

## Development

**Installation**

The installation method is similar to installing XBlocks or other custom modules.

``` bash
cd $(tutor config printroot)/env/build/openedx/requirements
git clone https://github.com/tony-h/rocketchat-tab.git
echo "-e ./rocketchat-tab/" >> private.txt

# Stop and start Tutor dev to rebuild the images to include the new tab
tutor dev stop && tutor dev start -d
```

**Configuration**

See Rocket.Chat's instructions on obtaining a
[Personal Access Token](https://docs.rocket.chat/guides/user-guides/user-panel/managing-your-account/personal-access-token).

Edit *settings/common.py* to specify your Rocket.Chat data. 
  
``` python
settings.ROCKETCHAT_BASE_URL = 'https://your.rocketchat.instance/'
settings.ROCKETCHAT_ADMIN_TOKEN = "your-admin-token"
settings.ROCKETCHAT_ADMIN_USER_ID = "your-user-id"
```

## Production

**Installation**

The installation method is similar to installing XBlocks or other custom modules.

``` bash
cd $(tutor config printroot)/env/build/openedx/requirements
echo "git+https://github.com/tony-h/rocketchat-tab.git" >> private.txt

# Build the images and then restart Tutor
tutor images build openedx
tutor local stop & tutor local start -d
```

**Configuration**

1. Create a Tutor plugin to specify the Rocket.Chat environmental variables.
  
    Here is the plugin template for `$(tutor plugins printroot)/rocketchat-auth.py`

    ``` python
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
    ```

2. Enable and activate the plugin.

    ``` bash
    # Verify the plugin is listed
    tutor plugins list

    # Enable the plugin
    tutor plugins enable rocketchat-auth

    # Update the environment to include the plugin
    tutor config save

    # Run tutor quickstart
    tutor local quickstart
    ```
