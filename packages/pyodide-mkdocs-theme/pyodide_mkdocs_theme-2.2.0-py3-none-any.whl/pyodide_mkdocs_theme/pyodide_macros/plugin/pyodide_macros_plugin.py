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


import os
import re
from collections import defaultdict, namedtuple
from functools import wraps
from pathlib import Path
from typing import ClassVar, List, Set


from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import BuildError
from mkdocs_macros.plugin import MacrosPlugin



from ...__version__ import __version__
from ..exceptions import PyodideConfigurationError
from ..pyodide_logger import logger
from ..macros import (
    autres,
    IDEs,
    isolated_components,
    qcm,
)
from .config import (
    PLUGIN_CONFIG_SRC,
    MISSING_MACROS_PROPS,
    EXTRAS_MACROS_PROPS,
)
from .maestro_base import BaseMaestro
from .maestro_meta import MaestroMeta
from .maestro_indent import MaestroIndent
from .maestro_IDE import MaestroIDE
from .maestro_extras import MaestroExtras





RegisteredPlugin = namedtuple('RegisteredPlugin', 'prefix name src')





class PyodideMacrosPlugin(
    MaestroExtras,
    MaestroIDE,
    MaestroIndent,
    MaestroMeta,
    BaseMaestro,
    MacrosPlugin,    # Always last, so that other classes may trigger super methods appropriately.
):
    """
    Class centralizing all the behaviors of the different parent classes.

    This is kinda the "controller", linking all the behaviors to mkdocs machinery, while the
    parent classes hold the "somewhat self contained" behaviors.

    For reference, here are the hooks defined in the original MacrosPlugin:
        - on_config
        - on_nav
        - on_page_markdown  (+ on_pre_page_macros + on_post_page_macros)
        - on_post_build     (on_post_build macros)
        - on_serve
    """

    __mkdocs_checked = False
    """ Flag to check the mkdocs.yml config once only """

    MATERIAL_PLUGINS: ClassVar[Set[str]] = set('''
        blog group info offline privacy search social tags
    '''.split())
    """
    All existing mkdocs-material plugins.
    See: https://github.com/squidfunk/mkdocs-material/tree/master/src/plugins
    """


    # Override
    def on_config(self, config:MkDocsConfig):
        # pylint: disable=attribute-defined-outside-init

        self._check_material_prefixes_plugins_config_once(config)

        # --------------------------------------------------------------
        # Section to always apply first:

        self._conf    = config # done in MacrosPlugin, but also here because needed here or there
        self.in_serve = config.dev_addr.host in config.site_url
        self.language = config.theme['language']

        self.docs_dir_path    = Path(config.docs_dir)
        self.docs_dir_cwd_rel = self.docs_dir_path.relative_to(Path.cwd())

        # --------------------------------------------------------------

        self._check_macros_plugin_props()
        self._check_docs_paths_validity()
        PLUGIN_CONFIG_SRC.handle_deprecated_options(self)

        super().on_config(config)



    #--------------------------------------------------------------------------



    # Override
    def _load_modules(self):
        """ Override the super method to register the Pyodide macros at appropriate time """

        def macro_with_warning(func):
            macro = func(self)
            logged = False          # log once only only per macro...

            @wraps(func)
            def wrapper(*a,**kw):
                nonlocal logged
                if not logged:
                    logged = True
                    self.warn_unmaintained(f'The macro {func.__name__!r}')
                return macro(*a,**kw)
            return wrapper


        macros = [
            IDEs.IDE,
            IDEs.IDEv,
            IDEs.terminal,
            IDEs.py_btn,
            IDEs.section,

            qcm.multi_qcm,

            isolated_components.py,
            isolated_components.figure,
        ]
        old_macros = [
            autres.cours,
            autres.exercice,
            autres.ext,
            autres.html_fig,
            autres.numworks,
            autres.python_carnet,
            autres.python_ide,
            autres.tit,
            autres.mult_col,
        ]

        for func in macros:
            self.macro(func(self))

        for func in old_macros:
            self.macro( macro_with_warning(func) )

        super()._load_modules()



    # Override
    def _load_yaml(self):
        """
        Override the MacrosPlugin method, replacing on the fly `__builtins__.open` with a version
        handling the encoding.
        """
        # pylint: disable=multiple-statements
        src_open = open
        def open_with_utf8(*a,**kw):
            return src_open(*a,**kw, encoding=self.load_yaml_encoding)

        # Depending on the python version/context, the __builtins__ can be of different types
        as_dct = isinstance(__builtins__, dict)

        if as_dct:  __builtins__['open'] = open_with_utf8
        else:       __builtins__.open = open_with_utf8
        try:
            super()._load_yaml()
        finally:
            if as_dct:  __builtins__['open'] = src_open
            else:       __builtins__.open = src_open



    #--------------------------------------------------------------------------


    def _check_material_prefixes_plugins_config_once(self, config:MkDocsConfig):
        """
        Following 2.2.0 breaking change: material plugins' do not _need_ to be prefixed
        anymore, but the json schema validation expect non prefixed plugin names, so:

            if config.theme.name is material:
                error + how to fix it (mismatched config)
            if "material/plugin":
                error + how to fix it (pmt/...)
            if config.theme.name is something else (theme extension):
                if not "pmt/plugin":  error + how to fix it (pmt/...)


        HOW TO SPOT VALUES:
            Access plugins (dict):  `config.plugins`

                Containing keys (behavior of material's plugins only!):
                * `{theme.name}/search`  <-  `mkdocs.yml:plugins: - search`
                * `{some}/search`        <-  `mkdocs.yml:plugins: - {some}/search`
                => The theme prefix IS ALWAYS THERE in the config!
        """
        if self.__mkdocs_checked:
            return
        self.__mkdocs_checked = True # pylint: disable=attribute-defined-outside-init

        material, pmt   = 'material', 'pyodide-mkdocs-theme'
        plugins_pattern = re.compile(
            f"(?:(?P<prefix>\\w*)/)?(?P<name>{ '|'.join(self.MATERIAL_PLUGINS) })"
        )

        theme        = config.theme.name
        is_extension = theme and theme not in (material, pmt, None)

        registered: List[RegisteredPlugin] = [
            RegisteredPlugin(m['prefix'], m['name'], m[0])
                for m in map(plugins_pattern.fullmatch, config.plugins)
                if m
        ]

        errors  = []

        if not theme or theme==material:
            errors.append(
                f"The { pmt }'s plugin is registered, so `theme.name` should be set "
                f"to `{ pmt }` instead of `{ theme }`."
            )

        features = config.theme.get('features', ())
        if 'navigation.instant' in features:
            errors.append(
                "Remove `navigation.instant` from `mkdocs.yml:theme.features`. "
                "It is not compatible with the pyodide-mkdocs-theme."
            )

        for plug in registered:
            if plug.prefix != theme:
                errors.append(
                    f"The `{ plug.src }` plugin should be registered " + (
                        f"with `pyodide-mkdocs-theme/{ plug.name }`."
                            if is_extension else
                        f"using `{ plug.name }` only{ ' (PMT >= 2.2.0)' * (theme==pmt) }."
                    )
                )

        if errors:
            str_errors = ''.join(map( '\n  {}'.format, errors ))
            raise BuildError(
                f"Invalid theme or material's plugin configuration(s):{ str_errors }"
            )





    def _check_docs_paths_validity(self) -> None :
        """
        Travel through all paths in the docs_dir and raises an BuildError if "special characters"
        are found in directory, py, or md file names (accepted characters are: r'[\\w.-]+' )

        NOTE: Why done here and not in `_on_files`?
                => because on_files is subject to files exclusions, and most python files SHOULD
                have been excluded from the build. So `on_files` could make more sense considering
                the kind of task, but is not technically appropriate/relevant anyway...
        """
        if self.skip_py_md_paths_names_validation:
            logger.warning("The build.skip_py_md_paths_names_validation option is activated.")
            return

        logger.debug("Markdown path names validation.")

        invalid_chars = re.compile(r'[^A-Za-z0-9_.-]+')
        wrongs = defaultdict(list)

        # Validation is done on the individual/current segments of the paths, so that an invalid
        # directory name is not affecting the validation of its children:
        for path,dirs,files in os.walk(self.docs_dir):

            files_to_check = [ file for file in files if re.search(r'\.(py|md)$', file)]

            for segment in dirs + files_to_check:
                invalids = frozenset(invalid_chars.findall(segment))
                if invalids:
                    wrongs[invalids].append( os.path.join(path,segment) )

        if wrongs:
            msg = ''.join(
                f"\nInvalid characters {repr(''.join(sorted(invalids)))} found in these filepaths:"
                + "".join(f"\n\t{ path }" for path in sorted(lst))
                for invalids,lst in wrongs.items()
            )
            raise BuildError(
                f"{ msg }\nPython and markdown files, and their parent directories' names "
                'should only contain alphanumerical characters (no accents or special chars), '
                "dots, underscores, and/or hyphens."
            )



    def _check_macros_plugin_props(self):
        """ Verify that the config of the MacroPlugin class is still the expected one """
        logger.debug("Check that the original MacrosPlugin implementation didn't change.")

        if not MISSING_MACROS_PROPS and not EXTRAS_MACROS_PROPS:
            return

        if self.ignore_macros_plugin_diffs:
            logger.error(
                "Inconsistent MacrosPlugin properties. `build.ignore_macros_plugin_diffs` "
                "is set to true"
            )

        else:
            raise PyodideConfigurationError(f"""
Cannot configure PyodideMacrosPlugin: the basic configuration of MacrosPlugin changed:
{ MISSING_MACROS_PROPS }{ EXTRAS_MACROS_PROPS }"""
"\n\nIf you absolutely need to run mkdocs before any fix is done, you can try the option "
"`ignore_macros_plugin_diffs: true` in the `plugin_macros` section of `mkdocs.yml`, "
"but there are no guarantees the build will succeed, depending on what the changes were.\n")
