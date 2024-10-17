from typing import Final

DEBUG: Final = 1
INFO: Final = 2
WARN: Final = 3
ERROR: Final = 4
FATAL: Final = 5

class Log:
    def __init__(self, threshold: int = 3) -> None: ...
    def log(self, level: int, msg: str, *args: object) -> None: ...
    def debug(self, msg: str, *args: object) -> None: ...
    def info(self, msg: str, *args: object) -> None: ...
    def warn(self, msg: str, *args: object) -> None: ...
    def error(self, msg: str, *args: object) -> None: ...
    def fatal(self, msg: str, *args: object) -> None: ...

def log(level: int, msg: str, *args: object) -> None: ...
def debug(msg: str, *args: object) -> None: ...
def info(msg: str, *args: object) -> None: ...
def warn(msg: str, *args: object) -> None: ...
def error(msg: str, *args: object) -> None: ...
def fatal(msg: str, *args: object) -> None: ...
def set_threshold(level: int) -> int: ...
def set_verbosity(v: int) -> None: ...
