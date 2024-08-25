#!/usr/bin/env python3

# Bundle class, pylint: disable=too-few-public-methods
class Bundle:

    # Modules
    MODULE: str = 'pre_commit_crocodile'

    # Names
    NAME: str = 'pre-commit-crocodile'

    # Packages
    PACKAGE: str = 'pre-commit-crocodile'

    # Resources
    RESOURCES_ASSETS: str = f'{MODULE}.assets'

    # Details
    DESCRIPTION: str = 'Git hooks intended for developers using pre-commit'

    # Sources
    REPOSITORY: str = 'https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile'

    # Releases
    RELEASE_FIRST_TIMESTAMP: int = 1579337311

    # Environment
    ENV_DEBUG_REVISION_SHA: str = 'DEBUG_REVISION_SHA'
    ENV_DEBUG_UPDATES_DAILY: str = 'DEBUG_UPDATES_DAILY'
    ENV_DEBUG_UPDATES_DISABLE: str = 'DEBUG_UPDATES_DISABLE'
    ENV_DEBUG_UPDATES_FAKE: str = 'DEBUG_UPDATES_FAKE'
    ENV_DEBUG_UPDATES_OFFLINE: str = 'DEBUG_UPDATES_OFFLINE'
    ENV_DEBUG_VERSION_FAKE: str = 'DEBUG_VERSION_FAKE'
    ENV_NO_COLOR: str = 'NO_COLOR'
