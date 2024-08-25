#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from importlib.resources import files as resources_files
from os import linesep
from pathlib import Path
from time import sleep
from typing import List

# Components
from ..package.bundle import Bundle
from ..package.version import Version
from ..prints.colors import Colors
from ..system.commands import Commands
from ..system.platform import Platform

# Entrypoint class, pylint: disable=too-few-public-methods,too-many-statements
class Entrypoint:

    # Constants
    ARGCOMPLETE_BINARY: str = 'activate-global-python-argcomplete'
    ARGCOMPLETE_MARKER: str = 'added by argcomplete'
    COMMITIZEN_BINARY: str = 'cz'
    COMMITIZEN_MARKER: str = '# register-python-argcomplete cz'
    COMMITIZEN_PACKAGE: str = 'commitizen'
    COMMITIZEN_SOURCES: str = 'git+https://github.com/AdrianDC/commitizen.git@prerelease'
    COMMITIZEN_VERSION: str = '3.29.0.AdrianDC.20240813'
    GIT_BINARY: str = 'git'
    PRECOMMIT_BINARY: str = 'pre-commit'
    PRECOMMIT_HOOKS_APPLY_ERROR: str = ' does not apply to this repository'
    PRECOMMIT_PACKAGE: str = 'pre-commit'

    # Configurations
    CONFIGURATION_COMMITIZEN_FILE: str = '.cz.yaml'
    CONFIGURATION_PRECOMMIT_FILE: str = '.pre-commit-config.yaml'
    CONFIGURATIONS_ASSETS: List[str] = [
        CONFIGURATION_COMMITIZEN_FILE,
        CONFIGURATION_PRECOMMIT_FILE,
    ]

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # CLI, pylint: disable=too-many-branches,too-many-locals
    @staticmethod
    def cli(options: Namespace, ) -> Result:

        # Variables
        data_lines: List[str]
        git_remotes: List[str]
        hooks_unused: List[str]
        user_bashrc: Path
        user_home: Path = Path.home()

        # List hooks
        if options.list:

            # Detect hooks directory
            hooks_dir = Commands.output(Entrypoint.GIT_BINARY, [
                'rev-parse',
                '--git-path',
                'hooks',
            ])

            # List hooks directory
            if Path(hooks_dir).exists():

                # Detect hooks files
                hooks_files = [
                    hook.name for hook in Path(hooks_dir).iterdir()
                    if hook.is_file() and '.' not in hook.name
                ]

                # List hooks files
                if hooks_files:
                    print(' ')
                    print(f'{Colors.BOLD} - List hooks: '
                          f'{Colors.GREEN}Hooks installed in "{hooks_dir}"'
                          f'{Colors.RESET}')
                    print(' ')
                    for hook in hooks_files:
                        print(f'{Colors.BOLD}   - Hook: {Colors.RESET}{hook}')
                    print(' ')
                    Platform.flush()

                # Missing hooks files
                else:
                    print(' ')
                    print(f'{Colors.BOLD} - List hooks: '
                          f'{Colors.YELLOW_LIGHT}No hooks installed in "{hooks_dir}"'
                          f'{Colors.RESET}')
                    print(' ')
                    Platform.flush()

            # Missing hooks directory
            else:
                print(' ')
                print(f'{Colors.BOLD} - List hooks: '
                      f'{Colors.RED}No hooks directory found in "{hooks_dir}"'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()

        # Prepare dependencies
        if options.install or options.configure or options.enable or options.autoupdate \
                or options.run:

            # Install pre-commit dependency
            if options.install or not Commands.exists(Entrypoint.PRECOMMIT_BINARY):
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}pre-commit'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                if Commands.exists(Entrypoint.PRECOMMIT_BINARY):
                    Commands.pip([
                        'uninstall',
                        Entrypoint.PRECOMMIT_PACKAGE,
                    ])
                Commands.pip([
                    'install',
                    Entrypoint.PRECOMMIT_PACKAGE,
                ])

            # Install commitizen dependency
            if options.install or not Commands.exists(
                    Entrypoint.COMMITIZEN_BINARY) or Commands.output(
                        Entrypoint.COMMITIZEN_BINARY, [
                            'version',
                        ]) != Entrypoint.COMMITIZEN_VERSION:
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}commitizen'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                if Commands.exists(Entrypoint.COMMITIZEN_BINARY):
                    Commands.pip([
                        'uninstall',
                        Entrypoint.COMMITIZEN_PACKAGE,
                    ])
                Commands.pip([
                    'install',
                    Entrypoint.COMMITIZEN_SOURCES,
                ])

            # Install argcomplete completion
            if options.install and (not Commands.grep(
                    Path(user_home / '.bash_completion'),
                    Entrypoint.ARGCOMPLETE_MARKER,
            ) or not Commands.grep(
                    Path(user_home / '.zshenv'),
                    Entrypoint.ARGCOMPLETE_MARKER,
            )):
                print(' ')
                print(f'{Colors.BOLD} - Install bash completion: '
                      f'{Colors.YELLOW_LIGHT}argcomplete'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                Commands.run(Entrypoint.ARGCOMPLETE_BINARY, [
                    '--user',
                ])
                sleep(2)

            # Detect user .bashrc
            user_bashrc = user_home / '.bashrc'
            if Path(user_home / '.bash_user.rc').exists():
                user_bashrc = user_home / '.bash_user.rc'

            # Install commitizen completion
            if options.install and not Commands.grep(
                    user_bashrc,
                    Entrypoint.COMMITIZEN_MARKER,
            ):
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}commitizen completion'
                      f'{Colors.RESET}')
                print(' ')
                print(f'commitizen completion enabled in: {user_bashrc}')
                Platform.flush()
                with open(user_bashrc, encoding='utf8', mode='a') as f:
                    f.write(f'{linesep}')
                    f.write(f'# register-python-argcomplete cz{linesep}')
                    f.write(f'eval "$(register-python-argcomplete cz)"{linesep}')
                    sleep(1)

        # Configure sources
        if options.configure:

            # Install sources configurations
            print(' ')
            print(f'{Colors.BOLD} - Configure sources: '
                  f'{Colors.YELLOW_LIGHT}{Bundle.NAME}'
                  f'{Colors.RESET}')
            print(' ')

            # Export assets files
            for asset in Entrypoint.CONFIGURATIONS_ASSETS:
                print(f'exporting configuration in {asset} configuration')
                data: str = resources_files(Bundle.RESOURCES_ASSETS) \
                    .joinpath(asset) \
                    .read_text(encoding='utf8') \
                    .replace('{PACKAGE_REVISION}', Version.revision())
                with open(
                        asset,
                        encoding='utf8',
                        mode='w',
                ) as f:
                    f.write(data)
                    sleep(1)

            # Prestage pre-commit configuration
            Commands.run(Entrypoint.GIT_BINARY, [
                'add',
                Entrypoint.CONFIGURATION_PRECOMMIT_FILE,
            ])

            # Configure pre-commit unused hooks
            print(' ')
            print(f'{Colors.BOLD} - Configure sources: '
                  f'{Colors.YELLOW_LIGHT}check-hooks-apply'
                  f'{Colors.RESET}')
            print(' ')
            hooks_unused = []
            for line in Commands.output(Entrypoint.PRECOMMIT_BINARY, [
                    'run',
                    '--all-files',
                    'check-hooks-apply',
            ]).splitlines():
                if Entrypoint.PRECOMMIT_HOOKS_APPLY_ERROR not in line:
                    continue
                hooks_unused += [
                    line[0:line.find(Entrypoint.PRECOMMIT_HOOKS_APPLY_ERROR)]
                ]

            # Reset pre-commit configuration
            Commands.run(Entrypoint.GIT_BINARY, [
                'reset',
                'HEAD',
                Entrypoint.CONFIGURATION_PRECOMMIT_FILE,
            ])

            # Disable pre-commit unused hooks
            if hooks_unused:
                with open(
                        Entrypoint.CONFIGURATION_PRECOMMIT_FILE,
                        encoding='utf8',
                        mode='r',
                ) as f:
                    data_lines = f.readlines()
                with open(
                        Entrypoint.CONFIGURATION_PRECOMMIT_FILE,
                        encoding='utf8',
                        mode='w',
                ) as f:
                    hook_offset: str
                    hook_section: bool = False
                    hook_id: str = '- id: '
                    for line in data_lines:
                        line_stripped = line.strip()
                        if not line_stripped:
                            f.write(line)
                            hook_section = False
                        elif any(line_stripped == f'{hook_id}{hook}'
                                 for hook in hooks_unused):
                            f.write(line.replace(hook_id, f'# {hook_id}'))
                            hook_offset = line[0:line.find(hook_id)]
                            hook_section = True
                        elif line_stripped.startswith(hook_id):
                            f.write(line)
                            hook_section = False
                        elif hook_section:
                            f.write(f'{hook_offset}#   {line.lstrip()}')
                        else:
                            f.write(line)

            # Show sources status
            print(' ')
            Commands.run(Entrypoint.GIT_BINARY, [
                'status',
                '--untracked-files',
            ])

            # Show commit hints
            command_add: str = ' '.join([
                Entrypoint.GIT_BINARY,
                'add',
                '-v',
            ] + [f'./{asset}' for asset in Entrypoint.CONFIGURATIONS_ASSETS])
            command_commit: str = ' '.join([
                Entrypoint.GIT_BINARY,
                'commit',
                '-m',
                f'"chore(pre-commit): import \'{Bundle.NAME}\' configurations"',
                '-s',
            ])
            print(' ')
            print(f'{Colors.BOLD}Add configurations: '
                  f'{Colors.CYAN}{command_add}'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}Commit changes: '
                  f'{Colors.CYAN}{command_commit}'
                  f'{Colors.RESET}')

            # Delay user interactions
            sleep(5)

        # Enable hooks
        if options.enable:

            # Detect Git branches
            git_remotes = [
                branch.lstrip('*').strip()
                for branch in Commands.output(Entrypoint.GIT_BINARY, [
                    'remote',
                ]).splitlines()
            ]

            # Enable Git hooks
            print(' ')
            print(f'{Colors.BOLD} - Enable hooks: '
                  f'{Colors.YELLOW_LIGHT}Git remote'
                  f'{Colors.RESET}')
            print(' ')
            print(f'detected Git remotes: {", ".join(git_remotes)}')
            Platform.flush()
            for remote in git_remotes:
                print(f'updating git remote for {remote}')
                Commands.run(Entrypoint.GIT_BINARY, [
                    'remote',
                    'set-head',
                    f'{remote}',
                    '-a',
                ])

            # Enable pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Enable hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commands.run(Entrypoint.PRECOMMIT_BINARY, [
                'install',
                '--allow-missing-config',
            ])

        # Disable hooks
        if options.disable:

            # Disable pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Disable hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commands.run(Entrypoint.PRECOMMIT_BINARY, [
                'uninstall',
            ])

        # Autoupdate hooks
        if options.autoupdate:

            # Autoupdate pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Autoupdate hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commands.run(Entrypoint.PRECOMMIT_BINARY, [
                'autoupdate',
            ])

        # Run hooks
        if options.run:

            # Run pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Run hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commands.run(Entrypoint.PRECOMMIT_BINARY, [
                'run',
                '--all-files',
            ])

            # Run commitizen hooks
            print(' ')
            print(f'{Colors.BOLD} - Run hooks: '
                  f'{Colors.YELLOW_LIGHT}commitizen'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commands.run(Entrypoint.COMMITIZEN_BINARY, [
                'check',
                '--rev-range',
                'HEAD~1..HEAD',
            ])

        # Result
        return Entrypoint.Result.SUCCESS
