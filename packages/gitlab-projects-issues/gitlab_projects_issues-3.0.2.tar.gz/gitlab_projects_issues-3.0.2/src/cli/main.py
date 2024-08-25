#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os import environ
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.environments import Environments
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 31

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    environments: Environments
    group: _ArgumentGroup
    result: Entrypoint.Result = Entrypoint.Result.ERROR

    # Configure environment variables
    environments = Environments()
    environments.group = 'environment variables'
    environments.add(
        'gitlab_token',
        Bundle.ENV_GITLAB_TOKEN,
        'GitLab API token environment variable',
    )
    environments.add(
        'ci_job_token',
        Bundle.ENV_CI_JOB_TOKEN,
        'GitLab CI job token environment variable (CI only)',
    )

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
        epilog=environments.help(HELP_POSITION),
        add_help=False,
        formatter_class=lambda prog: RawTextHelpFormatter(
            prog,
            max_help_position=HELP_POSITION,
            width=min(
                120,
                get_terminal_size().columns - 2,
            ),
        ),
    )

    # Arguments internal definitions
    group = parser.add_argument_group('internal arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '--version',
        dest='version',
        action='store_true',
        help='Show the current version',
    )
    group.add_argument(
        '--no-color',
        dest='no_color',
        action='store_true',
        help=f'Disable colors outputs with \'{Bundle.ENV_NO_COLOR}=1\'\n'
        '(or default settings: [themes] > no_color)',
    )
    group.add_argument(
        '--update-check',
        dest='update_check',
        action='store_true',
        help='Check for newer package updates',
    )
    group.add_argument(
        '--settings',
        dest='settings',
        action='store_true',
        help='Show the current settings path and contents',
    )
    group.add_argument(
        '--set',
        dest='set',
        action='store',
        metavar=('GROUP', 'KEY', 'VAL'),
        nargs=3,
        help='Set settings specific \'VAL\' value to [GROUP] > KEY\n' \
             'or unset by using \'UNSET\' as \'VAL\'',
    )

    # Arguments credentials definitions
    group = parser.add_argument_group('credentials arguments')
    group.add_argument(
        '-c',
        '--config',
        dest='configs',
        action='append',
        metavar='FILES',
        help=f'Python GitLab configuration files'
        f' (default: {Bundle.ENV_PYTHON_GITLAB_CFG} environment)',
    )

    # Arguments common definitions
    group = parser.add_argument_group('common arguments')
    group.add_argument(
        '--dump',
        dest='dump',
        action='store_true',
        help='Dump Python objects of projects',
    )

    # Arguments issues definitions
    group = parser.add_argument_group('issues arguments')
    group.add_argument(
        '--default-estimate',
        dest='default_estimate',
        default='8',
        action='store',
        metavar='ESTIMATE',
        help='Default issue time estimate if none provided'
        'in hours (default: %(default)s)',
    )
    group.add_argument(
        '--exclude-closed-issues',
        dest='exclude_closed_issues',
        action='store_true',
        help='Exclude issues in closed state',
    )

    # Arguments milestones definitions
    group = parser.add_argument_group('milestones arguments')
    group.add_argument(
        '--milestone',
        dest='milestone',
        action='store',
        help='Use a specific milestone by name, by ID, or "None"',
    )
    group.add_argument(
        '--milestones-statistics',
        dest='milestones_statistics',
        action='store_true',
        help='Inject milestones statistics into milestones\' description',
    )
    group.add_argument(
        '--exclude-closed-milestones',
        dest='exclude_closed_milestones',
        action='store_true',
        help='Exclude milestones in closed state',
    )

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument(
        '--',
        dest='double_dash',
        action='store_true',
        help='Positional arguments separator (recommended)',
    )
    group.add_argument(
        dest='url_path',
        action='store',
        nargs='?',
        help='GitLab project path URL',
    )

    # Arguments parser
    options: Namespace = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Instantiate settings
    settings: Settings = Settings(name=Bundle.NAME)

    # Prepare no_color
    if not options.no_color:
        if settings.has('themes', 'no_color'):
            options.no_color = settings.get_bool('themes', 'no_color')
        else:
            options.no_color = False
            settings.set_bool('themes', 'no_color', options.no_color)

    # Configure no_color
    if options.no_color:
        environ[Bundle.ENV_NO_COLOR] = '1'

    # Prepare colors
    Colors.prepare()

    # Settings setter
    if options.set:
        settings.set(options.set[0], options.set[1], options.set[2])
        settings.show()
        sys_exit(0)

    # Settings informations
    if options.settings:
        settings.show()
        sys_exit(0)

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.NAME,
        settings=settings,
    )

    # Version informations
    if options.version:
        print(
            f'{Bundle.NAME} {Version.get()} from {Version.path()} (python {Version.python()})'
        )
        Platform.flush()
        sys_exit(0)

    # Check for current updates
    if options.update_check:
        if not updates.check():
            updates.check(older=True)
        sys_exit(0)

    # Arguments validation
    if not options.url_path:
        result = Entrypoint.Result.CRITICAL

    # Header
    print(' ')
    Platform.flush()

    # Tool identifier
    if result != Entrypoint.Result.CRITICAL:
        print(f'{Colors.BOLD} {Bundle.NAME}'
              f'{Colors.YELLOW_LIGHT} ({Version.get()})'
              f'{Colors.RESET}')
        Platform.flush()

    # CLI entrypoint
    if result != Entrypoint.Result.CRITICAL:
        result = Entrypoint.cli(
            options,
            environments,
        )

    # CLI helper
    else:
        parser.print_help()

    # Footer
    print(' ')
    Platform.flush()

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    if result in [
            Entrypoint.Result.SUCCESS,
            Entrypoint.Result.FINALIZE,
    ]:
        sys_exit(0)
    else:
        sys_exit(1)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
