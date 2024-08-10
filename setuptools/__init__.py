"""Extensions to the 'distutils' for large or complex distributions"""
# mypy: disable_error_code=override
# Command.reinitialize_command has an extra **kw param that distutils doesn't have
# Can't disable on the exact line because distutils doesn't exists on Python 3.12
# and mypy isn't aware of distutils_hack, causing distutils.core.Command to be Any,
# and a [unused-ignore] to be raised on 3.12+

from __future__ import annotations

from abc import ABC, abstractmethod
import functools
import os
import re
import sys
from typing import TYPE_CHECKING, TypeVar, overload, Literal


sys.path.extend(((vendor_path := os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setuptools', '_vendor')) not in sys.path) * [vendor_path])  # fmt: skip
# workaround for #4476
sys.modules.pop('backports', None)

import _distutils_hack.override  # noqa: F401
import distutils.core
from distutils.errors import DistutilsOptionError

from . import logging, monkey
from .version import __version__ as __version__
from .depends import Require
from .discovery import PackageFinder, PEP420PackageFinder
from .dist import Distribution
from .extension import Extension
from .warnings import SetuptoolsDeprecationWarning

__all__ = [
    'setup',
    'Distribution',
    'Command',
    'Extension',
    'Require',
    'SetuptoolsDeprecationWarning',
    'find_packages',
    'find_namespace_packages',
]

_CommandT = TypeVar("_CommandT", bound="Command")

bootstrap_install_from = None

find_packages = PackageFinder.find
find_namespace_packages = PEP420PackageFinder.find


def _install_setup_requires(attrs):
    # Note: do not use `setuptools.Distribution` directly, as
    # our PEP 517 backend patch `distutils.core.Distribution`.
    class MinimalDistribution(distutils.core.Distribution):
        """
        A minimal version of a distribution for supporting the
        fetch_build_eggs interface.
        """

        def __init__(self, attrs):
            _incl = 'dependency_links', 'setup_requires'
            filtered = {k: attrs[k] for k in set(_incl) & set(attrs)}
            super().__init__(filtered)
            # Prevent accidentally triggering discovery with incomplete set of attrs
            self.set_defaults._disable()

        def _get_project_config_files(self, filenames=None):
            """Ignore ``pyproject.toml``, they are not related to setup_requires"""
            try:
                cfg, toml = super()._split_standard_project_metadata(filenames)
            except Exception:
                return filenames, ()
            return cfg, ()

        def finalize_options(self):
            """
            Disable finalize_options to avoid building the working set.
            Ref #2158.
            """

    dist = MinimalDistribution(attrs)

    # Honor setup.cfg's options.
    dist.parse_config_files(ignore_option_errors=True)
    if dist.setup_requires:
        _fetch_build_eggs(dist)


def _fetch_build_eggs(dist):
    try:
        dist.fetch_build_eggs(dist.setup_requires)
    except Exception as ex:
        msg = """
        It is possible a package already installed in your system
        contains an version that is invalid according to PEP 440.
        You can try `pip install --use-pep517` as a workaround for this problem,
        or rely on a new virtual environment.

        If the problem refers to a package that is not installed yet,
        please contact that package's maintainers or distributors.
        """
        if "InvalidVersion" in ex.__class__.__name__:
            if hasattr(ex, "add_note"):
                ex.add_note(msg)  # PEP 678
            else:
                dist.announce(f"\n{msg}\n")
        raise


def setup(**attrs):
    # Make sure we have any requirements needed to interpret 'attrs'.
    logging.configure()
    _install_setup_requires(attrs)
    return distutils.core.setup(**attrs)


setup.__doc__ = distutils.core.setup.__doc__

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    # Work around a mypy issue where type[T] can't be used as a base: https://github.com/python/mypy/issues/10962
    _Command: TypeAlias = distutils.core.Command
else:
    _Command = monkey.get_unpatched(distutils.core.Command)


class Command(_Command, ABC):
    """
    Setuptools internal actions are organized using a *command design pattern*.
    This means that each action (or group of closely related actions) executed during
    the build should be implemented as a ``Command`` subclass.

    These commands are abstractions and do not necessarily correspond to a command that
    can (or should) be executed via a terminal, in a CLI fashion (although historically
    they would).

    When creating a new command from scratch, custom defined classes **SHOULD** inherit
    from ``setuptools.Command`` and implement a few mandatory methods.
    Between these mandatory methods, are listed:
    :meth:`initialize_options`, :meth:`finalize_options` and :meth:`run`.

    A useful analogy for command classes is to think of them as subroutines with local
    variables called "options".  The options are "declared" in :meth:`initialize_options`
    and "defined" (given their final values, aka "finalized") in :meth:`finalize_options`,
    both of which must be defined by every command class. The "body" of the subroutine,
    (where it does all the work) is the :meth:`run` method.
    Between :meth:`initialize_options` and :meth:`finalize_options`, ``setuptools`` may set
    the values for options/attributes based on user's input (or circumstance),
    which means that the implementation should be careful to not overwrite values in
    :meth:`finalize_options` unless necessary.

    Please note that other commands (or other parts of setuptools) may also overwrite
    the values of the command's options/attributes multiple times during the build
    process.
    Therefore it is important to consistently implement :meth:`initialize_options` and
    :meth:`finalize_options`. For example, all derived attributes (or attributes that
    depend on the value of other attributes) **SHOULD** be recomputed in
    :meth:`finalize_options`.

    When overwriting existing commands, custom defined classes **MUST** abide by the
    same APIs implemented by the original class. They also **SHOULD** inherit from the
    original class.
    """

    command_consumes_arguments = False
    distribution: Distribution  # override distutils.dist.Distribution with setuptools.dist.Distribution

    def __init__(self, dist: Distribution, **kw):
        """
        Construct the command for dist, updating
        vars(self) with any keyword parameters.
        """
        super().__init__(dist)
        vars(self).update(kw)

    def _ensure_stringlike(self, option, what, default=None):
        val = getattr(self, option)
        if val is None:
            setattr(self, option, default)
            return default
        elif not isinstance(val, str):
            raise DistutilsOptionError(
                "'%s' must be a %s (got `%s`)" % (option, what, val)
            )
        return val

    def ensure_string_list(self, option):
        r"""Ensure that 'option' is a list of strings.  If 'option' is
        currently a string, we split it either on /,\s*/ or /\s+/, so
        "foo bar baz", "foo,bar,baz", and "foo,   bar baz" all become
        ["foo", "bar", "baz"].

        ..
           TODO: This method seems to be similar to the one in ``distutils.cmd``
           Probably it is just here for backward compatibility with old Python versions?

        :meta private:
        """
        val = getattr(self, option)
        if val is None:
            return
        elif isinstance(val, str):
            setattr(self, option, re.split(r',\s*|\s+', val))
        else:
            if isinstance(val, list):
                ok = all(isinstance(v, str) for v in val)
            else:
                ok = False
            if not ok:
                raise DistutilsOptionError(
                    "'%s' must be a list of strings (got %r)" % (option, val)
                )

    if TYPE_CHECKING:
        from .command.alias import alias
        from .command.bdist_egg import bdist_egg
        from .command.bdist_rpm import bdist_rpm
        from .command.bdist_wheel import bdist_wheel
        from .command.build import build
        from .command.build_clib import build_clib
        from .command.build_ext import build_ext
        from .command.build_py import build_py
        from .command.develop import develop
        from .command.dist_info import dist_info
        from .command.easy_install import easy_install
        from .command.editable_wheel import editable_wheel
        from .command.egg_info import egg_info
        from .command.install import install
        from .command.install_egg_info import install_egg_info
        from .command.install_lib import install_lib
        from .command.install_scripts import install_scripts
        from .command.register import register
        from .command.rotate import rotate
        from .command.saveopts import saveopts
        from .command.sdist import sdist
        from .command.setopt import setopt
        from .command.test import test
        from .command.upload import upload
        from .command.upload_docs import upload_docs

    @overload  # type: ignore[override]
    def reinitialize_command(
        self, command: Literal["alias"], reinit_subcommands: bool = False, **kw
    ) -> alias: ...
    @overload
    def reinitialize_command(
        self, command: Literal["bdist_egg"], reinit_subcommands: bool = False, **kw
    ) -> bdist_egg: ...
    @overload
    def reinitialize_command(
        self, command: Literal["bdist_rpm"], reinit_subcommands: bool = False, **kw
    ) -> bdist_rpm: ...
    @overload
    def reinitialize_command(
        self, command: Literal["bdist_wheel"], reinit_subcommands: bool = False, **kw
    ) -> bdist_wheel: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build"], reinit_subcommands: bool = False, **kw
    ) -> build: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build_clib"], reinit_subcommands: bool = False, **kw
    ) -> build_clib: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build_ext"], reinit_subcommands: bool = False, **kw
    ) -> build_ext: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build_py"], reinit_subcommands: bool = False, **kw
    ) -> build_py: ...
    @overload
    def reinitialize_command(
        self, command: Literal["develop"], reinit_subcommands: bool = False, **kw
    ) -> develop: ...
    @overload
    def reinitialize_command(
        self, command: Literal["dist_info"], reinit_subcommands: bool = False, **kw
    ) -> dist_info: ...
    @overload
    def reinitialize_command(
        self, command: Literal["easy_install"], reinit_subcommands: bool = False, **kw
    ) -> easy_install: ...
    @overload
    def reinitialize_command(
        self, command: Literal["editable_wheel"], reinit_subcommands: bool = False, **kw
    ) -> editable_wheel: ...
    @overload
    def reinitialize_command(
        self, command: Literal["egg_info"], reinit_subcommands: bool = False, **kw
    ) -> egg_info: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install"], reinit_subcommands: bool = False, **kw
    ) -> install: ...
    @overload
    def reinitialize_command(
        self,
        command: Literal["install_egg_info"],
        reinit_subcommands: bool = False,
        **kw,
    ) -> install_egg_info: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_lib"], reinit_subcommands: bool = False, **kw
    ) -> install_lib: ...
    @overload
    def reinitialize_command(
        self,
        command: Literal["install_scripts"],
        reinit_subcommands: bool = False,
        **kw,
    ) -> install_scripts: ...
    @overload
    def reinitialize_command(
        self, command: Literal["register"], reinit_subcommands: bool = False, **kw
    ) -> register: ...
    @overload
    def reinitialize_command(
        self, command: Literal["rotate"], reinit_subcommands: bool = False, **kw
    ) -> rotate: ...
    @overload
    def reinitialize_command(
        self, command: Literal["saveopts"], reinit_subcommands: bool = False, **kw
    ) -> saveopts: ...
    @overload
    def reinitialize_command(
        self, command: Literal["sdist"], reinit_subcommands: bool = False, **kw
    ) -> sdist: ...
    @overload
    def reinitialize_command(
        self, command: Literal["setopt"], reinit_subcommands: bool = False, **kw
    ) -> setopt: ...
    @overload
    def reinitialize_command(
        self, command: Literal["test"], reinit_subcommands: bool = False, **kw
    ) -> test: ...
    @overload
    def reinitialize_command(
        self, command: Literal["upload"], reinit_subcommands: bool = False, **kw
    ) -> upload: ...
    @overload
    def reinitialize_command(
        self, command: Literal["upload_docs"], reinit_subcommands: bool = False, **kw
    ) -> upload_docs: ...
    @overload
    def reinitialize_command(
        self, command: str, reinit_subcommands: bool = False, **kw
    ) -> Command: ...
    @overload
    def reinitialize_command(
        self, command: _CommandT, reinit_subcommands: bool = False, **kw
    ) -> _CommandT: ...
    def reinitialize_command(
        self, command: str | _Command, reinit_subcommands: bool = False, **kw
    ) -> _Command:
        cmd = _Command.reinitialize_command(self, command, reinit_subcommands)
        vars(cmd).update(kw)
        return cmd

    @abstractmethod
    def initialize_options(self) -> None:
        """
        Set or (reset) all options/attributes/caches used by the command
        to their default values. Note that these values may be overwritten during
        the build.
        """
        raise NotImplementedError

    @abstractmethod
    def finalize_options(self) -> None:
        """
        Set final values for all options/attributes used by the command.
        Most of the time, each option/attribute/cache should only be set if it does not
        have any value yet (e.g. ``if self.attr is None: self.attr = val``).
        """
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """
        Execute the actions intended by the command.
        (Side effects **SHOULD** only take place when :meth:`run` is executed,
        for example, creating new files or writing to the terminal output).
        """
        raise NotImplementedError


def _find_all_simple(path):
    """
    Find all files under 'path'
    """
    results = (
        os.path.join(base, file)
        for base, dirs, files in os.walk(path, followlinks=True)
        for file in files
    )
    return filter(os.path.isfile, results)


def findall(dir=os.curdir):
    """
    Find all files under 'dir' and return the list of full filenames.
    Unless dir is '.', return full filenames with dir prepended.
    """
    files = _find_all_simple(dir)
    if dir == os.curdir:
        make_rel = functools.partial(os.path.relpath, start=dir)
        files = map(make_rel, files)
    return list(files)


class sic(str):
    """Treat this string as-is (https://en.wikipedia.org/wiki/Sic)"""


# Apply monkey patches
monkey.patch_all()
