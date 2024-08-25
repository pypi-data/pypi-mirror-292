#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from importlib.resources import files as resources_files
from pathlib import Path
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from time import sleep
from typing import List, Union

# Components
from ..features.argcomplete import Argcomplete
from ..features.commitizen import Commitizen
from ..features.git import Git
from ..features.precommit import PreCommit
from ..features.readme import Readme
from ..package.bundle import Bundle
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform

# Entrypoint class, pylint: disable=too-few-public-methods,too-many-statements
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # TempFile type
    TempFile = Union[_TemporaryFileWrapper] # type: ignore[type-arg]

    # CLI, pylint: disable=too-many-boolean-expressions,too-many-branches,too-many-locals
    @staticmethod
    def cli(options: Namespace, ) -> Result:

        # List hooks
        if options.list:

            # Detect hooks directory
            hooks_dir = Git.hooks_dir()

            # List hooks directory
            if Path(hooks_dir).exists():

                # Detect hooks files
                hooks_files = Git.hooks_files()

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
                or options.clean or options.run:

            # Install pre-commit dependency
            if options.install or not PreCommit.exists():
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}pre-commit'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                PreCommit.dependencies()

            # Install commitizen dependency
            if options.install or not Commitizen.exists() or not Commitizen.compatible():
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}commitizen'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                Commitizen.dependencies()

            # Install argcomplete completion
            if options.install and not Argcomplete.configured():
                print(' ')
                print(f'{Colors.BOLD} - Install bash completion: '
                      f'{Colors.YELLOW_LIGHT}argcomplete'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                Argcomplete.configure()
                sleep(2)

            # Install commitizen completion
            if options.install and not Commitizen.configured():
                print(' ')
                print(f'{Colors.BOLD} - Install dependencies: '
                      f'{Colors.YELLOW_LIGHT}commitizen completion'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                commitizen_file: str = Commitizen.configure()
                print(f'commitizen completion enabled in: {commitizen_file}')
                sleep(1)

        # Bind specific configurations
        if options.config:
            Commitizen.set_configuration(options.config + Platform.PATH_SEPARATOR +
                                         Commitizen.CONFIGURATION_FILE)
            PreCommit.set_configuration(options.config + Platform.PATH_SEPARATOR +
                                        PreCommit.CONFIGURATION_FILE)

        # Bind default configurations
        elif options.default:

            # Bind configurations files, pylint: disable=consider-using-with
            commitizen_configuration: Entrypoint.TempFile = NamedTemporaryFile(
                delete_on_close=True,
                suffix=Commitizen.CONFIGURATION_EXTENSION,
            )
            precommit_configuration: Entrypoint.TempFile = NamedTemporaryFile(
                delete_on_close=True,
                suffix=PreCommit.CONFIGURATION_EXTENSION,
            )

            # Bind configurations flags
            Commitizen.set_configuration(commitizen_configuration.name)
            PreCommit.set_configuration(precommit_configuration.name)

            # Default pre-commit configuration
            with open(
                    precommit_configuration.name,
                    encoding='utf8',
                    mode='w+t',
            ) as file:

                # Acquire pre-commit configuration
                file.write(resources_files(Bundle.RESOURCES_ASSETS) \
                    .joinpath(PreCommit.CONFIGURATION_FILE) \
                    .read_text(encoding='utf8') \
                    .replace(PreCommit.REV_TEMPLATE, Version.revision()))
                file.flush()

            # Default commitizen configuration
            with open(
                    commitizen_configuration.name,
                    encoding='utf8',
                    mode='w+t',
            ) as file:

                # Acquire commitizen configuration
                file.write(resources_files(Bundle.RESOURCES_ASSETS) \
                    .joinpath(Commitizen.CONFIGURATION_FILE) \
                    .read_text(encoding='utf8') \
                    .replace(PreCommit.REV_TEMPLATE, Version.revision()))
                file.flush()

            # Configure unused hooks
            PreCommit.configure_unused_hooks(
                default=options.default,
                configuration_file=precommit_configuration.name,
            )

        # Configure sources
        if options.configure:

            # Install sources configurations
            print(' ')
            print(f'{Colors.BOLD} - Configure sources: '
                  f'{Colors.YELLOW_LIGHT}{Bundle.NAME}'
                  f'{Colors.RESET}')
            print(' ')

            # List configurations files
            configurations_files: List[str] = [
                Commitizen.CONFIGURATION_FILE,
                PreCommit.CONFIGURATION_FILE,
            ]

            # Export assets files
            for asset in configurations_files:
                print(f'exporting configuration in {asset} configuration')
                data: str = resources_files(Bundle.RESOURCES_ASSETS) \
                    .joinpath(asset) \
                    .read_text(encoding='utf8') \
                    .replace(PreCommit.REV_TEMPLATE, Version.revision())
                with open(
                        asset,
                        encoding='utf8',
                        mode='w',
                ) as f:
                    f.write(data)
                    sleep(1)

            # Configure unused hooks
            PreCommit.configure_unused_hooks(default=options.default)

            # Inject badge to README
            if Readme.exists():

                # Configure README sources
                print(' ')
                print(f'{Colors.BOLD} - Configure sources: '
                      f'{Colors.YELLOW_LIGHT}{Readme.FILE}'
                      f'{Colors.RESET}')
                print(' ')
                configurations_files += [Readme.FILE]

                # Acquire README contents
                readme_lines: List[str] = Readme.read()

                # Validate badge in README
                if not any(Bundle.NAME in line for line in readme_lines):

                    # Inject badge line
                    print(f'injecting badge in {Readme.FILE} documentation')
                    print(' ')
                    for i, line in enumerate(readme_lines):
                        if not line.strip():
                            readme_lines.insert(
                                i + 1,
                                line,
                            )
                            readme_lines.insert(
                                i + 1,
                                f'[![{Bundle.NAME}]({Bundle.BADGE})]({Bundle.DOCUMENTATION}){line}',
                            )
                            break

                    # Export README contents
                    Readme.write(readme_lines)

                # Keep existing README
                else:
                    print(f'keeping original {Readme.FILE} documentation')
                    print(' ')

            # Show sources status
            print(' ')
            Git.status(untracked=True)

            # Show commit hints
            command_add: str = ' '.join([
                Git.BINARY,
                'add',
                '-v',
            ] + [f'./{asset}' for asset in configurations_files])
            command_commit: str = ' '.join([
                Git.BINARY,
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

            # Detect Git remotes
            git_remotes: List[str] = Git.remotes()

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
                Git.update_remote_head(remote)

            # Enable pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Enable hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            PreCommit.install()

        # Disable hooks
        if options.disable:

            # Disable pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Disable hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            PreCommit.uninstall()

        # Autoupdate hooks
        if options.autoupdate:

            # Autoupdate pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Autoupdate hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            PreCommit.autoupdate()

        # Cleanup hooks
        if options.clean:

            # Disable pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Cleanup hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            PreCommit.clean()

        # Run hooks
        if options.run:

            # Run pre-commit hooks
            print(' ')
            print(f'{Colors.BOLD} - Run hooks: '
                  f'{Colors.YELLOW_LIGHT}pre-commit'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            PreCommit.run(all_files=True)

            # Run commitizen hooks
            print(' ')
            print(f'{Colors.BOLD} - Run hooks: '
                  f'{Colors.YELLOW_LIGHT}commitizen'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            Commitizen.check('HEAD~1..HEAD')

        # Result
        return Entrypoint.Result.SUCCESS
