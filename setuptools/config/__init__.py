"""For backward compatibility, expose main functions from
``setuptools.config.setupcfg``
"""

from functools import wraps
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

from ..warnings import SetuptoolsDeprecationWarning
from . import setupcfg

_R = TypeVar("_R")
_P = ParamSpec("_P")

__all__ = ("parse_configuration", "read_configuration")


def _deprecation_notice(fn: Callable[_P, _R]) -> Callable[_P, _R]:
    @wraps(fn)
    def _wrapper(*args: _P.args, **kwargs: _P.kwargs):
        SetuptoolsDeprecationWarning.emit(
            "Deprecated API usage.",
            f"""
            As setuptools moves its configuration towards `pyproject.toml`,
            `{__name__}.{fn.__name__}` became deprecated.

            For the time being, you can use the `{setupcfg.__name__}` module
            to access a backward compatible API, but this module is provisional
            and might be removed in the future.

            To read project metadata, consider using
            ``build.util.project_wheel_metadata`` (https://pypi.org/project/build/).
            For simple scenarios, you can also try parsing the file directly
            with the help of ``configparser``.
            """,
            # due_date not defined yet, because the community still heavily relies on it
            # Warning introduced in 24 Mar 2022
        )
        return fn(*args, **kwargs)

    return _wrapper


read_configuration = _deprecation_notice(setupcfg.read_configuration)
parse_configuration = _deprecation_notice(setupcfg.parse_configuration)
