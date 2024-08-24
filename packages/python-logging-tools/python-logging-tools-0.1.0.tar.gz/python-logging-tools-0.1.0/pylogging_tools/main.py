from logging import ERROR, WARNING, INFO, DEBUG, CRITICAL, Logger
from colorama import Fore
import logging

logging.basicConfig(level=logging.INFO, format="log [%(name)s]> %(levelname)s - %(message)s")

__all__ = [
    "LoggingTools",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "CRITICAL",
]


class Filter(logging.Filter):
    def __init__(self, name):
        self.name = name
        super().__init__()

    def filter(self, record):
        if record.name.startswith("log "):
            return False
        return True


class LoggingTools:
    """
    A class that provides logging functionality.
    """
    _name: str | None
    __logger: logging.Logger | None
    __file_handler: logging.FileHandler | None
    level: int | None

    def __init__(self,
                 name: str,
                 level: int = INFO,
                 file: str | None = None,
                 filemode: str = "a",
                 log_format: str = "%(asctime)s [%(name)s]> %(levelname)s - %(message)s"):
        self._name = name
        self.level: int = level
        self.log_format = logging.Formatter(
            log_format.replace("&time", "%(asctime)s").replace("&name", name).replace("&level",
                                                                                      "%(levelname)s").replace(
                "&message", "%(message)s"))
        if file is not None:
            self.add_file_handler(file=file, mode=filemode)

        # logger settings
        self.__logger: Logger = logging.getLogger(name)
        logger_handler = logging.StreamHandler()
        self.__logger.setLevel(level)
        self.__logger.addHandler(logger_handler)
        logger_handler.setFormatter(self.log_format)
        filter_ = Filter(name)
        self.__logger.addFilter(filter_)

    def add_file_handler(self, file, mode):
        self.__file_handler = logging.FileHandler(filename=file, mode=mode)
        self.__logger.addHandler(self.__file_handler)

    def remove_file_handler(self):
        self.__logger.removeHandler(self.__file_handler)
        self.__file_handler = None

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

    def __log(self, color, msg, level):
        self.__logger.log(msg=color + msg + Fore.RESET, level=level)

    def get_logger(self) -> Logger | None:
        """Returns the logger object"""
        return self.__logger

    def get_file_handler(self) -> logging.FileHandler | None:
        """Returns the file handler object"""
        return self.__file_handler
