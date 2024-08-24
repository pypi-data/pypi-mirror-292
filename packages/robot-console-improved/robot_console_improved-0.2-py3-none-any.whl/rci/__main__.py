"""
This is a wrapper script for robot that enables our console by default.
It overwrites the default (verbose) console output type.
If the current TTY is not a terminal, it doesn't do anything.
"""
import sys

import robot.output.logger
from robot.output.console import NoOutput
from robot.output.listeners import ListenerV3Facade

from rci.improved import Improved

_ORIGINAL_CONSOLE_OUTPUT = robot.output.logger.ConsoleOutput
_ORIGINAL_IMPORT_LISTENERS = robot.output.listeners.Listeners._import_listeners


def import_listeners(*args, **kwargs):
    listeners = _ORIGINAL_IMPORT_LISTENERS(*args, **kwargs)
    if not isinstance(args[0], robot.output.listeners.LibraryListeners):
        custom_listener = ListenerV3Facade(Improved(), 'own_listener', None)
        listeners.append(custom_listener)
    return listeners


# noinspection PyPep8Naming,PyShadowingBuiltins
def ConsoleOutputWrapper(type, *args, **kwargs):
    if type == "verbose" and sys.stdout.isatty():
        robot.output.listeners.Listeners._import_listeners = import_listeners
        return NoOutput()
    print(f"Started via rci but falling back to normal console output because {type!='verbose'=} or {not sys.stdout.isatty()=}.")
    return _ORIGINAL_CONSOLE_OUTPUT(type, *args, **kwargs)


def main():
    robot.output.logger.ConsoleOutput = ConsoleOutputWrapper
    robot.run_cli()


if __name__ == "__main__":
    main()
