import sys
import shutil

def _do_nothing(*args: object) -> None:
    pass

def shutil_rmtree(path, ignore_errors=False, onexc=_do_nothing):
    if sys.version_info >= (3, 12):
        return shutil.rmtree(path, ignore_errors, onexc=onexc)

    def _handler(fn, path, excinfo):
        return onexc(fn, path, excinfo[1])

    return shutil.rmtree(path, ignore_errors, onerror=_handler)
