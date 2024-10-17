from collections.abc import Callable
from typing import ClassVar

from _typeshed import Incomplete, Unused

from ..cmd import Command
from ..extension import Extension

class build_ext(Command):
    description: str
    sep_by: Incomplete
    user_options: ClassVar[list[tuple[str, str | None, str]]]
    boolean_options: ClassVar[list[str]]
    help_options: ClassVar[list[tuple[str, str | None, str, Callable[[], Unused]]]]
    extensions: Incomplete
    build_lib: Incomplete
    plat_name: Incomplete
    build_temp: Incomplete
    inplace: int
    package: Incomplete
    include_dirs: Incomplete
    define: Incomplete
    undef: Incomplete
    libraries: Incomplete
    library_dirs: Incomplete
    rpath: Incomplete
    link_objects: Incomplete
    debug: Incomplete
    force: Incomplete
    compiler: Incomplete
    swig: Incomplete
    swig_cpp: Incomplete
    swig_opts: Incomplete
    user: Incomplete
    parallel: Incomplete
    def initialize_options(self) -> None: ...
    def finalize_options(self) -> None: ...
    def run(self) -> None: ...
    def check_extensions_list(self, extensions) -> None: ...
    def get_source_files(self): ...
    def get_outputs(self): ...
    def build_extensions(self) -> None: ...
    def build_extension(self, ext) -> None: ...
    def swig_sources(self, sources, extension): ...
    def find_swig(self): ...
    def get_ext_fullpath(self, ext_name: str) -> str: ...
    def get_ext_fullname(self, ext_name: str) -> str: ...
    def get_ext_filename(self, ext_name: str) -> str: ...
    def get_export_symbols(self, ext: Extension) -> list[str]: ...
    def get_libraries(self, ext: Extension) -> list[str]: ...
