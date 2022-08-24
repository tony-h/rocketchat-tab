# -*- coding: utf-8 -*-


import setuptools

setuptools.setup(
    name="rocketchat-tab",
    version="0.1.0",
    author="Tony Hetrick",
    license="MIT",
    author_email="tony.hetrick@gmail.com",
    description="rocketchat-tab Open edX course_tab",
    long_description="Integrates Rocket.Chat into each course by adding a new tab.",
    url="https://github.com/tony-h/rocketchat-tab",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Platform :: Open edX",
        "Natural Language :: English",
        "Environment :: Web Environment",
    ],
    entry_points={
        "lms.djangoapp": [
            "rocketchat_tab = rocketchat_tab.apps:RocketChatConfig",
        ],
        "openedx.course_tab": [
            "rocketchat_tab = rocketchat_tab.plugins:RocketChatTab",
        ]
    },
)
