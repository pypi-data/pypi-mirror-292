"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""
# pylint: disable=multiple-statements



from collections import defaultdict
from operator import attrgetter
from typing import Any, ClassVar, Dict, List, Optional, Set
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path

import yaml

from mkdocs.structure.files import Files
from mkdocs.exceptions import BuildError
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page


from ..plugin.maestro_base import BaseMaestro
from ..plugin.maestro_tools import CopyableConfig, PythonLib
from ..exceptions import PyodideMacrosMetaError, PyodideMacrosPyLibsError
from .config import PyodideMacrosConfig, PLUGIN_CONFIG_SRC









class MaestroMeta(BaseMaestro):
    """ Handles the .meta.pmt.yml values and the meta sections in Pages. """

    __pmt_meta_wrapped__: str = "__pmt_meta_wrapped__"
    """
    Property added to the mkdocs events decorated with MaestroMeta.meta_config_swap. This property
    allows to enforce proper contracts on the config values, whatever the plugin inheritance chain.
    """

    _meta_tree: Optional['MetaTree'] = None
    """
    Tree holding all the meta configs, merging the data appropriately at any depth.
    """

    libs: List[PythonLib]  = None       # added on the fly
    base_py_libs: Set[str] = None       # added on the fly



    def on_config(self, config:MkDocsConfig):

        self.check_config_swap_decorations()

        super().on_config(config)

        self._handle_python_libs()

        # Gather all the meta files AFTER the super call, so that the config is up to date:
        self._meta_tree = MetaTree.create(self.config)

        for meta_path in self.docs_dir_path.rglob(self._pmt_meta_filename):

            content  = meta_path.read_text(encoding=self.meta_yaml_encoding)
            meta_rel = meta_path.relative_to(self.docs_dir_path)
            meta_dct = yaml.load(content, Loader=yaml.Loader)
            self._validate_meta_python_libs(meta_rel, meta_dct)

            self._meta_tree.insert_meta_file(meta_dct, meta_rel, self.docs_dir_cwd_rel)



    def on_files(self, files: Files, /, *, config: MkDocsConfig):
        """
        If python libs directories are registered, create one archive for each of them.
        It's on the responsibility of the user to work with them correctly...
        """
        for lib in self.libs:
            # Remove any cached files to make the archive lighter (the version won't match
            # pyodide compiler anyway!):
            for cached in lib.path.rglob("*.pyc"):
                cached.unlink()
            file = lib.create_archive_and_get_file(self)
            files.append(file)



    # Override
    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Suppress the python archives from the CWD.
        """
        for lib in self.libs:
            lib.unlink()

        super().on_post_build(config)



    #-------------------------------------------------------------------------



    def apply_macro(self, name, func, *args, **kwargs):            # pylint: disable=unused-argument
        """ Apply all default arguments from the current config """

        args, kwargs = PLUGIN_CONFIG_SRC.assign_defaults_to_macro_call_args(
            name, args, kwargs, self
        )
        return super().apply_macro(name, func, *args, **kwargs)



    @classmethod
    def meta_config_swap(cls, method):
        """
        Static decorator for mkdocs events that are using a Page argument.

        For the decorated event, the global mkdocs config content will be swapped with a version
        of it merged with the content of the .meta.pmt.yml files, and any metadata section in the
        page itself.
        """

        page_getter = None  # extract the Page argument from the hook call arguments

        def build_page_getter(self, args:tuple, kwargs:dict):
            nonlocal page_getter

            i_arg = next((i for i,v in enumerate(args) if isinstance(v,Page)), None)
            name  = next( (name for name,v in kwargs.items() if isinstance(v,Page)), None)
            # pylint: disable=unnecessary-lambda-assignment
            if i_arg is not None:
                page_getter = lambda args, _: args[i_arg]
            elif name is not None:
                page_getter = lambda _,kwargs: kwargs[name]
            else:
                raise PyodideMacrosMetaError(
                    "Couldn't find an argument whose the value is a mkdocs Page instance on "
                    f"the { method.__name__ } method of { self }"
                )
            return page_getter


        @wraps(method)
        def wrapper(self:MaestroMeta, *a, **kw):
            # pylint: disable=protected-access
            page: Page   = ( page_getter or build_page_getter(self,a,kw) )(a, kw)
            current_conf = self.config
            self._validate_meta_python_libs(page.file.src_uri, page.meta)
            meta_config  = self._meta_tree.get_config_for_page_with_metadata(page)
            self.config  = meta_config
            try:
                out = method(self, *a,**kw)
            finally:
                self.config = current_conf
            return out

        setattr(wrapper, cls.__pmt_meta_wrapped__, True)
        return wrapper



    def check_config_swap_decorations(self):
        """
        Check the top event calls in the hierarchy are wrapped with the MaestroMeta decorator.
        At the time of writing this class, the hierarchy leads to these qualified names:

            PyodideMacrosPlugin
            MaestroExtras
            MaestroIDE
            MaestroIndent
            MaestroMeta
            BaseMaestro
            BasePlugin[PyodideMacrosConfig]
            MacrosPlugin                        <<< Meta configs also must be seen here!
            BasePlugin
            Generic
        """

        mro_depth = { cls.__qualname__: i for i,cls in enumerate(self.__class__.mro()) }
        no_wrapper_depth = mro_depth['BasePlugin']
        for hook in '''
            on_pre_page
            on_page_read_source
            on_page_markdown
            on_page_content
            on_page_context
            on_post_page
        '''.split():

            method = getattr(self, hook, None)
            if not method:
                continue

            cls_qualname = method.__qualname__[:-len(method.__name__)-1]
            need_wrapper = mro_depth[cls_qualname] < no_wrapper_depth

            if need_wrapper and not hasattr(method, self.__pmt_meta_wrapped__):
                raise PyodideMacrosMetaError(
                    f'The { method.__qualname__ } event method should be decorated with the '
                    f'pyodide_mkdocs_theme.pyodide_macros.{ self.meta_config_swap.__qualname__ } '
                     'class method decorator (use it as outer decorator).'
                )



    #-------------------------------------------------------------------------



    def _handle_python_libs(self):
        """
        Add the python_libs directory to the watch list, create the internal PythonLib objects,
        and check python_libs validity:
            1. No python_lib inside another.
            2. If not a root level, must not be importable.
            3. No two python libs with the same name (if registered at different levels)
        """

        self._conf.watch.extend(
            str(py_lib.absolute()) for py_lib in map(Path, self.python_libs)
                                   if py_lib.exists()
        )

        self.libs = sorted(
            filter(None, map(PythonLib, self.python_libs)), key=attrgetter('abs_slash')
        )


        libs_by_name: Dict[str, List[PythonLib]] = defaultdict(list)
        for lib in self.libs:
            libs_by_name[lib.lib_name].append(lib)


        same_names = ''.join(
            f"\nLibraries that would be imported as {name!r}:" + ''.join(
                f'\n\t{ lib.lib }' for lib in libs
            )
            for name,libs in libs_by_name.items() if len(libs)>1
        )
        if same_names:
            raise PyodideMacrosPyLibsError(
                "Several custom python_libs ending with the same final name are not allowed."
                + same_names
            )


        parenting = ''.join(
            f"\n\t{ self.libs[i-1].lib } contains at least { lib.lib }"
                for i,lib in enumerate(self.libs)
                if i and self.libs[i-1].is_parent_of(lib)
        )
        if parenting:
            raise PyodideMacrosPyLibsError(
                "Custom python libs defined in the project cannot contain others:" + parenting
            )

        self.base_py_libs = set(p.lib for p in self.libs)


    def _validate_meta_python_libs(self, file:Path, meta_dct:Dict[str,Any], in_headers=False):
        """
        Validate that all the python_libs names are found in the mkdocs.yml initial configuration.
        If @meta_dct is None, check the content of self.python_libs instead (allow to validate
        headers).
        """
        if 'build' not in meta_dct: return
        dct = meta_dct['build']
        if 'python_libs' not in dct: return
        lst = dct['python_libs']

        bad_libs = [lib for lib in lst if lib not in self.base_py_libs]
        if bad_libs:
            raise PyodideMacrosMetaError(
                f"Invalid build.python_libs in { file }{ ' headers' * in_headers }:\n  "
                + ' '.join(bad_libs)
            )







@dataclass
class MetaTree:

    segment: str
    """ Directory name or file name. """

    config: CopyableConfig

    children: Dict[str,'MetaTree'] = field(default_factory=dict)


    _CACHE: ClassVar[Dict[str,Any]] = {}


    @classmethod
    def create(cls, config:CopyableConfig):

        cls._CACHE.clear()

        # Remove anything that is invalid for a PyodideMacrosConfig instance => allow to get rid of
        # the macro related parts and various things that shouldn't be there...
        #
        # TODO: this has become pointless, I think... => to remove + test without it.
        # note: get rid of the classmethod on the way? (using a marker on the segment argument? meh...)
        cfg:CopyableConfig = PyodideMacrosConfig()
        cfg = cfg.copy_with(config)
        return cls('_docs_', cfg)


    def insert_meta_file(self, yml_dct:dict, meta_path:Path, docs_dir:Path):

        tree = self
        for segment in meta_path.parent.parts:
            if segment not in tree.children:
                tree.children[segment] = MetaTree(segment, tree.config)
            tree = tree.children[segment]
        tree.config = tree.config.copy_with(yml_dct, consume_dict=True)

        if yml_dct:
            raise BuildError(
                f"Invalid key/value pairs in { docs_dir / meta_path }:"
                + "".join( f'\n    {k} : {v!r}' for k,v in yml_dct.items())
            )



    def get_config_for_page_with_metadata(self, page:Page):
        """
        Extract the appropriated config for the given Page directory, then merge it with
        any metadata section coming from the Page itself.

        NOTE: Only the metadata matching some of the plugin's config options will be merged.
              Other values/items will stay ignored (they are still usable in macros call using
              the original way the macros plugin handles them). For more information, see:
              https://mkdocs-macros-plugin.readthedocs.io/en/latest/post_production/#html-templates
        """

        src = Path(page.file.src_uri)       # Relative to docs_dir!

        if src not in self._CACHE:
            tree = self
            segments = src.parent.parts     # Note:  Path('index.md').parent.parts == () => ok!
            for segment in segments:
                if segment not in tree.children:
                    break
                tree = tree.children[segment]

            config = tree.config if not page.meta else tree.config.copy_with(page.meta)
            self._CACHE[src] = config

        return self._CACHE[src]
