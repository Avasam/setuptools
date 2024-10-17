from _typeshed import BytesPath, StrOrBytesPath, StrPath, Unused
from abc import abstractmethod
from collections.abc import Callable, Iterable
from typing import Any, ClassVar, TypeVar, overload
from distutils.command.bdist import bdist
from distutils.command.bdist_dumb import bdist_dumb
from distutils.command.bdist_rpm import bdist_rpm
from distutils.command.build import build
from distutils.command.build_clib import build_clib
from distutils.command.build_ext import build_ext
from distutils.command.build_py import build_py
from distutils.command.build_scripts import build_scripts
from distutils.command.check import check
from distutils.command.clean import clean
from distutils.command.config import config
from distutils.command.install import install
from distutils.command.install_data import install_data
from distutils.command.install_egg_info import install_egg_info
from distutils.command.install_headers import install_headers
from distutils.command.install_lib import install_lib
from distutils.command.install_scripts import install_scripts
from distutils.command.register import register
from distutils.command.sdist import sdist
from distutils.command.upload import upload
from distutils.dist import Distribution
from typing import Any, ClassVar, Literal, TypeVar, overload
from typing_extensions import TypeVarTuple, Unpack

from .dist import Distribution

_StrPathT = TypeVar("_StrPathT", bound=StrPath)
_BytesPathT = TypeVar("_BytesPathT", bound=BytesPath)
_CommandT = TypeVar("_CommandT", bound=Command)
_Ts = TypeVarTuple("_Ts")

class Command:
    dry_run: bool  # Exposed from __getattr_. Same as Distribution.dry_run
    distribution: Distribution
    # Any to work around variance issues
    sub_commands: ClassVar[list[tuple[str, Callable[[Any], bool] | None]]]
    def __init__(self, dist: Distribution) -> None: ...
    def ensure_finalized(self) -> None: ...
    @abstractmethod
    def initialize_options(self) -> None: ...
    @abstractmethod
    def finalize_options(self) -> None: ...
    @abstractmethod
    def run(self) -> None: ...
    def announce(self, msg: str, level: int = 10) -> None: ...
    def debug_print(self, msg: str) -> None: ...
    def ensure_string(self, option: str, default: str | None = None) -> None: ...
    def ensure_string_list(self, option: str) -> None: ...
    def ensure_filename(self, option: str) -> None: ...
    def ensure_dirname(self, option: str) -> None: ...
    def get_command_name(self) -> str: ...
    def set_undefined_options(self, src_cmd: str, *option_pairs: tuple[str, str]) -> None: ...
    # NOTE: This list comes directly from the distutils/command folder. Minus bdist_msi and bdist_wininst.
    @overload
    def get_finalized_command(self, command: Literal["bdist"], create: bool = True) -> bdist: ...
    @overload
    def get_finalized_command(self, command: Literal["bdist_dumb"], create: bool = True) -> bdist_dumb: ...
    @overload
    def get_finalized_command(self, command: Literal["bdist_rpm"], create: bool = True) -> bdist_rpm: ...
    @overload
    def get_finalized_command(self, command: Literal["build"], create: bool = True) -> build: ...
    @overload
    def get_finalized_command(self, command: Literal["build_clib"], create: bool = True) -> build_clib: ...
    @overload
    def get_finalized_command(self, command: Literal["build_ext"], create: bool = True) -> build_ext: ...
    @overload
    def get_finalized_command(self, command: Literal["build_py"], create: bool = True) -> build_py: ...
    @overload
    def get_finalized_command(self, command: Literal["build_scripts"], create: bool = True) -> build_scripts: ...
    @overload
    def get_finalized_command(self, command: Literal["check"], create: bool = True) -> check: ...
    @overload
    def get_finalized_command(self, command: Literal["clean"], create: bool = True) -> clean: ...
    @overload
    def get_finalized_command(self, command: Literal["config"], create: bool = True) -> config: ...
    @overload
    def get_finalized_command(self, command: Literal["install"], create: bool = True) -> install: ...
    @overload
    def get_finalized_command(self, command: Literal["install_data"], create: bool = True) -> install_data: ...
    @overload
    def get_finalized_command(
        self, command: Literal["install_egg_info"], create: bool = True
    ) -> install_egg_info: ...
    @overload
    def get_finalized_command(self, command: Literal["install_headers"], create: bool = True) -> install_headers: ...
    @overload
    def get_finalized_command(self, command: Literal["install_lib"], create: bool = True) -> install_lib: ...
    @overload
    def get_finalized_command(self, command: Literal["install_scripts"], create: bool = True) -> install_scripts: ...
    @overload
    def get_finalized_command(self, command: Literal["register"], create: bool = True) -> register: ...
    @overload
    def get_finalized_command(self, command: Literal["sdist"], create: bool = True) -> sdist: ...
    @overload
    def get_finalized_command(self, command: Literal["upload"], create: bool = True) -> upload: ...
    @overload
    def get_finalized_command(self, command: str, create: bool = True) -> Command: ...
    @overload
    def reinitialize_command(self, command: Literal["bdist"], reinit_subcommands: bool = False) -> bdist: ...
    @overload
    def reinitialize_command(
        self, command: Literal["bdist_dumb"], reinit_subcommands: bool = False
    ) -> bdist_dumb: ...
    @overload
    def reinitialize_command(self, command: Literal["bdist_rpm"], reinit_subcommands: bool = False) -> bdist_rpm: ...
    @overload
    def reinitialize_command(self, command: Literal["build"], reinit_subcommands: bool = False) -> build: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build_clib"], reinit_subcommands: bool = False
    ) -> build_clib: ...
    @overload
    def reinitialize_command(self, command: Literal["build_ext"], reinit_subcommands: bool = False) -> build_ext: ...
    @overload
    def reinitialize_command(self, command: Literal["build_py"], reinit_subcommands: bool = False) -> build_py: ...
    @overload
    def reinitialize_command(
        self, command: Literal["build_scripts"], reinit_subcommands: bool = False
    ) -> build_scripts: ...
    @overload
    def reinitialize_command(self, command: Literal["check"], reinit_subcommands: bool = False) -> check: ...
    @overload
    def reinitialize_command(self, command: Literal["clean"], reinit_subcommands: bool = False) -> clean: ...
    @overload
    def reinitialize_command(self, command: Literal["config"], reinit_subcommands: bool = False) -> config: ...
    @overload
    def reinitialize_command(self, command: Literal["install"], reinit_subcommands: bool = False) -> install: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_data"], reinit_subcommands: bool = False
    ) -> install_data: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_egg_info"], reinit_subcommands: bool = False
    ) -> install_egg_info: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_headers"], reinit_subcommands: bool = False
    ) -> install_headers: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_lib"], reinit_subcommands: bool = False
    ) -> install_lib: ...
    @overload
    def reinitialize_command(
        self, command: Literal["install_scripts"], reinit_subcommands: bool = False
    ) -> install_scripts: ...
    @overload
    def reinitialize_command(self, command: Literal["register"], reinit_subcommands: bool = False) -> register: ...
    @overload
    def reinitialize_command(self, command: Literal["sdist"], reinit_subcommands: bool = False) -> sdist: ...
    @overload
    def reinitialize_command(self, command: Literal["upload"], reinit_subcommands: bool = False) -> upload: ...
    @overload
    def reinitialize_command(self, command: str, reinit_subcommands: bool = False) -> Command: ...
    @overload
    def reinitialize_command(self, command: _CommandT, reinit_subcommands: bool = False) -> _CommandT: ...
    def run_command(self, command: str) -> None: ...
    def get_sub_commands(self) -> list[str]: ...
    def warn(self, msg: str) -> None: ...
    def execute(
        self, func: Callable[[Unpack[_Ts]], Unused], args: tuple[Unpack[_Ts]], msg: str | None = None, level: int = 1
    ) -> None: ...
    def mkpath(self, name: str, mode: int = 0o777) -> None: ...
    @overload
    def copy_file(
        self,
        infile: StrPath,
        outfile: _StrPathT,
        preserve_mode: bool = True,
        preserve_times: bool = True,
        link: str | None = None,
        level: Unused = 1,
    ) -> tuple[_StrPathT | str, bool]: ...
    @overload
    def copy_file(
        self,
        infile: BytesPath,
        outfile: _BytesPathT,
        preserve_mode: bool = True,
        preserve_times: bool = True,
        link: str | None = None,
        level: Unused = 1,
    ) -> tuple[_BytesPathT | bytes, bool]: ...
    def copy_tree(
        self,
        infile: StrPath,
        outfile: str,
        preserve_mode: bool = True,
        preserve_times: bool = True,
        preserve_symlinks: bool = False,
        level: Unused = 1,
    ) -> list[str]: ...
    @overload
    def move_file(self, src: StrPath, dst: _StrPathT, level: Unused = 1) -> _StrPathT | str: ...
    @overload
    def move_file(self, src: BytesPath, dst: _BytesPathT, level: Unused = 1) -> _BytesPathT | bytes: ...
    def spawn(self, cmd: Iterable[str], search_path: bool = True, level: Unused = 1) -> None: ...
    @overload
    def make_archive(
        self,
        base_name: str,
        format: str,
        root_dir: StrOrBytesPath | None = None,
        base_dir: str | None = None,
        owner: str | None = None,
        group: str | None = None,
    ) -> str: ...
    @overload
    def make_archive(
        self,
        base_name: StrPath,
        format: str,
        root_dir: StrOrBytesPath,
        base_dir: str | None = None,
        owner: str | None = None,
        group: str | None = None,
    ) -> str: ...
    def make_file(
        self,
        infiles: str | list[str] | tuple[str, ...],
        outfile: StrOrBytesPath,
        func: Callable[[Unpack[_Ts]], Unused],
        args: tuple[Unpack[_Ts]],
        exec_msg: str | None = None,
        skip_msg: str | None = None,
        level: Unused = 1,
    ) -> None: ...
