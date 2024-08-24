from .. import *

__all__ = ["git_path_loader", "run_test"]


def git_path_loader():
    return __file__.rstrip("main.py")


def run_test() -> bool:
    try:
        print("")
        log_test = LoggingTools(name="test", level=INFO)
        log_test.debug("Test Debug")
        log_test.info("Test Info")
        log_test.warning("Test Warning")
        log_test.error("Test Error")
        log_test.critical("Test Critical")
        return True
    except Exception as e:
        print("\nError: \n" + str(e))
        return False
