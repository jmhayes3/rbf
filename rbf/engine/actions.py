"""
This module contains a collection of Action classes to be used by bot modules.
"""


class Action:
    """Action base class."""


class Log(Action):

    def __init__(self) -> None:
        pass

    def execute(self) -> None:
        print("Executing log action.")
