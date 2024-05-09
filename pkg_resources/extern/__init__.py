from importlib.machinery import ModuleSpec
import importlib.util
import sys
from types import ModuleType
from typing import Generator, Iterable, Optional, Sequence


class VendorImporter:
    """
    A PEP 302 meta path importer for finding optionally-vendored
    or otherwise naturally-installed packages from root_name.
    """

    def __init__(
        self,
        root_name: str,
        vendored_names: Iterable[str] = (),
        vendor_pkg: Optional[str] = None,
    ) -> None:
        self.root_name = root_name
        self.vendored_names = set(vendored_names)
        self.vendor_pkg = vendor_pkg or root_name.replace('extern', '_vendor')

    @property
    def search_path(self) -> Generator[str, None, None]:
        """
        Search first the vendor package then as a natural package.
        """
        yield self.vendor_pkg + '.'
        yield ''

    def _module_matches_namespace(self, fullname):
        """Figure out if the target module is vendored."""
        root, base, target = fullname.partition(self.root_name + '.')
        return not root and any(map(target.startswith, self.vendored_names))

    def load_module(self, fullname: str) -> ModuleType:
        """
        Iterate over the search path to locate and load fullname.
        """
        root, base, target = fullname.partition(self.root_name + '.')
        for prefix in self.search_path:
            try:
                extant = prefix + target
                __import__(extant)
                mod = sys.modules[extant]
                sys.modules[fullname] = mod
                return mod
            except ImportError:
                pass
        else:
            raise ImportError(
                "The '{target}' package is required; "
                "normally this is bundled with this package so if you get "
                "this warning, consult the packager of your "
                "distribution.".format(**locals())
            )

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        return self.load_module(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        pass

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]] = None,
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        """Return a module spec for vendored names."""
        return (
            # FIXME: VendorImporter doesn't subclass importlib.abc.Loader
            importlib.util.spec_from_loader(fullname, self)  # type: ignore[arg-type]
            if self._module_matches_namespace(fullname)
            else None
        )

    def install(self) -> None:
        """
        Install this importer into sys.meta_path if not already present.
        """
        if self not in sys.meta_path:
            sys.meta_path.append(self)


# [[[cog
# import cog
# from tools.vendored import yield_root_package
# names = "\n".join(f"    {x!r}," for x in yield_root_package('pkg_resources'))
# cog.outl(f"names = (\n{names}\n)")
# ]]]
names = (
    'packaging',
    'platformdirs',
    'jaraco',
    'importlib_resources',
    'zipp',
    'more_itertools',
    'backports',
)
# [[[end]]]
VendorImporter(__name__, names).install()
