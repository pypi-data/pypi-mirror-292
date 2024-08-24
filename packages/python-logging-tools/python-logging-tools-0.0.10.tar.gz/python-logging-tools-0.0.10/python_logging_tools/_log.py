from logging import ERROR, WARNING, INFO, DEBUG, CRITICAL, Logger
from colorama import Fore

__all__ = ["ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL", "_Log"]


class _Log:
    def __init__(self, logger: Logger):
        self.__logger = logger

    def info(self, msg, color=Fore.LIGHTWHITE_EX):
        """Logs an info message."""
        self.__log(color, msg, INFO)

    def debug(self, msg, color=Fore.WHITE):
        self.__log(color, msg, DEBUG)

    def warning(self, msg, color=Fore.LIGHTYELLOW_EX):
        """Logs a warning message."""
        self.__log(color, msg, WARNING)

    def error(self, msg, color=Fore.LIGHTRED_EX):
        """Logs an error message."""
        self.__log(color, msg, ERROR)

    def critical(self, msg, color=Fore.RED):
        """Logs a critical message."""
        self.__log(color, msg, CRITICAL)

    def __log(self, color, msg, level, *args, **kwargs):
        self.__logger.log(msg=color + msg + Fore.RESET, level=level)

    def get_logger(self) -> Logger | None:
        """Returns the logger object"""
        return self.__logger
