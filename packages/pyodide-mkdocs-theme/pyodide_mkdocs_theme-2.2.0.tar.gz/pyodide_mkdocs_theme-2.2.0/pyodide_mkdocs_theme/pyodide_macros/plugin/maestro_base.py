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

# pylint: disable=multiple-statements, line-too-long, protected-access



import re
import json
from typing import  Any, Dict, List, Optional
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import BuildError
from mkdocs.structure.pages import Page
from mkdocs.plugins import BasePlugin

from ...__version__ import __version__
from ..tools_and_constants import ICONS_IN_TEMPLATES_DIR
from ..exceptions import PyodideMacrosDeprecationError, PyodideMacrosError
from ..messages import LangBase, Lang
from ..messages.classes import JsDumper
from ..pyodide_logger import logger
from .maestro_tools import ConfigExtractor, dump_and_dumper
from .config import PyodideMacrosConfig, PLUGIN_CONFIG_SRC





# Do NOT declare these as class level attributes (see `dump_to_js_config` hack, using None as self)
TO_DUMP_TO_CONFIG = """
    args_figure_div_id
    base_url
    button_icons_directory
    cut_feedback
    language
    pmt_url
    python_libs
    in_serve
    version
""".split()





class BaseMaestro(BasePlugin[PyodideMacrosConfig]):
    """
    Main class, regrouping the basic configurations, properties, getters and/or constants
    for the different children classes: each of them will inherit from MaestroConfig.
    It is also used as "sink" for the super calls of other classes that are not implemented
    on the MacrosPlugin class.

    Note that, for the ConfigExtractor for to properly work, the class hierarchy has to
    extend MacrosPlugin at some point.
    """

    # global mkdocs config data:
    docs_dir:  str = ConfigExtractor('_conf')
    repo_url:  str = ConfigExtractor('_conf')
    site_name: str = ConfigExtractor('_conf')
    site_url:  str = ConfigExtractor('_conf')
    site_dir:  str = ConfigExtractor('_conf')

    # ARGS EXTRACTOR TOKEN
    args_IDE_py_name:   str = ConfigExtractor('config.args.IDE', prop='py_name')
    args_IDE_SANS:      str = ConfigExtractor('config.args.IDE', prop='SANS')
    args_IDE_WHITE:     str = ConfigExtractor('config.args.IDE', prop='WHITE')
    args_IDE_REC_LIMIT: int = ConfigExtractor('config.args.IDE', prop='REC_LIMIT')
    args_IDE_MERMAID:  bool = ConfigExtractor('config.args.IDE', prop='MERMAID')
    args_IDE_MAX:       int = ConfigExtractor('config.args.IDE', prop='MAX')
    args_IDE_LOGS:     bool = ConfigExtractor('config.args.IDE', prop='LOGS')
    args_IDE_MODE:      str = ConfigExtractor('config.args.IDE', prop='MODE')
    args_IDE_MIN_SIZE:  int = ConfigExtractor('config.args.IDE', prop='MIN_SIZE')
    args_IDE_MAX_SIZE:  int = ConfigExtractor('config.args.IDE', prop='MAX_SIZE')
    args_IDE_TERM_H:    int = ConfigExtractor('config.args.IDE', prop='TERM_H')

    args_terminal_py_name:   str = ConfigExtractor('config.args.terminal', prop='py_name')
    args_terminal_SANS:      str = ConfigExtractor('config.args.terminal', prop='SANS')
    args_terminal_WHITE:     str = ConfigExtractor('config.args.terminal', prop='WHITE')
    args_terminal_REC_LIMIT: int = ConfigExtractor('config.args.terminal', prop='REC_LIMIT')
    args_terminal_MERMAID:  bool = ConfigExtractor('config.args.terminal', prop='MERMAID')
    args_terminal_TERM_H:    int = ConfigExtractor('config.args.terminal', prop='TERM_H')
    args_terminal_FILL:      str = ConfigExtractor('config.args.terminal', prop='FILL')

    args_py_btn_py_name:     str = ConfigExtractor('config.args.py_btn', prop='py_name')
    args_py_btn_SANS:        str = ConfigExtractor('config.args.py_btn', prop='SANS')
    args_py_btn_WHITE:       str = ConfigExtractor('config.args.py_btn', prop='WHITE')
    args_py_btn_REC_LIMIT:   int = ConfigExtractor('config.args.py_btn', prop='REC_LIMIT')
    args_py_btn_ICON:        str = ConfigExtractor('config.args.py_btn', prop='ICON')
    args_py_btn_HEIGHT:      int = ConfigExtractor('config.args.py_btn', prop='HEIGHT')
    args_py_btn_WIDTH:       int = ConfigExtractor('config.args.py_btn', prop='WIDTH')
    args_py_btn_SIZE:        int = ConfigExtractor('config.args.py_btn', prop='SIZE')
    args_py_btn_TIP:         str = ConfigExtractor('config.args.py_btn', prop='TIP')
    args_py_btn_TIP_SHIFT:   int = ConfigExtractor('config.args.py_btn', prop='TIP_SHIFT')
    args_py_btn_TIP_WIDTH: float = ConfigExtractor('config.args.py_btn', prop='TIP_WIDTH')
    args_py_btn_WRAPPER:     str = ConfigExtractor('config.args.py_btn', prop='WRAPPER')
    args_py_btn_MERMAID:    bool = ConfigExtractor('config.args.py_btn', prop='MERMAID')

    args_section_py_name: str = ConfigExtractor('config.args.section', prop='py_name')
    args_section_section: str = ConfigExtractor('config.args.section', prop='section')

    args_multi_qcm_description:        str = ConfigExtractor('config.args.multi_qcm', prop='description')
    args_multi_qcm_hide:              bool = ConfigExtractor('config.args.multi_qcm', prop='hide')
    args_multi_qcm_multi:             bool = ConfigExtractor('config.args.multi_qcm', prop='multi')
    args_multi_qcm_shuffle:           bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle')
    args_multi_qcm_shuffle_questions: bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle_questions')
    args_multi_qcm_shuffle_items:     bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle_items')
    args_multi_qcm_admo_kind:          str = ConfigExtractor('config.args.multi_qcm', prop='admo_kind')
    args_multi_qcm_admo_class:         str = ConfigExtractor('config.args.multi_qcm', prop='admo_class')
    args_multi_qcm_qcm_title:          str = ConfigExtractor('config.args.multi_qcm', prop='qcm_title')
    args_multi_qcm_DEBUG:             bool = ConfigExtractor('config.args.multi_qcm', prop='DEBUG')

    args_py_py_name: str = ConfigExtractor('config.args.py', prop='py_name')

    args_figure_div_id:     str = ConfigExtractor('config.args.figure', prop='div_id')
    args_figure_div_class:  str = ConfigExtractor('config.args.figure', prop='div_class')
    args_figure_inner_text: str = ConfigExtractor('config.args.figure', prop='inner_text')
    args_figure_admo_kind:  str = ConfigExtractor('config.args.figure', prop='admo_kind')
    args_figure_admo_class: str = ConfigExtractor('config.args.figure', prop='admo_class')
    args_figure_admo_title: str = ConfigExtractor('config.args.figure', prop='admo_title')

    _pmt_meta_filename:                            str = ConfigExtractor('config.build')
    deprecation_level:                             str = ConfigExtractor('config.build')
    encrypted_js_data:                            bool = ConfigExtractor('config.build')
    forbid_macros_override:                       bool = ConfigExtractor('config.build')
    ignore_macros_plugin_diffs:                   bool = ConfigExtractor('config.build')
    load_yaml_encoding:                            str = ConfigExtractor('config.build')
    macros_with_indents:                     List[str] = ConfigExtractor('config.build')
    meta_yaml_encoding:                            str = ConfigExtractor('config.build')
    python_libs:                             List[str] = ConfigExtractor('config.build')
    skip_py_md_paths_names_validation:            bool = ConfigExtractor('config.build')
    tab_to_spaces:                                 int = ConfigExtractor('config.build')
    _bypass_indent_errors:                        bool = ConfigExtractor('config.build', deprecated=True)
    _encrypt_corrections_and_rems:                bool = ConfigExtractor('config.build', deprecated=True)
    _forbid_corr_and_REMs_with_infinite_attempts: bool = ConfigExtractor('config.build', deprecated=True)
    _forbid_hidden_corr_and_REMs_without_secrets: bool = ConfigExtractor('config.build', deprecated=True)
    _forbid_secrets_without_corr_or_REMs:         bool = ConfigExtractor('config.build', deprecated=True)

    deactivate_stdout_for_secrets:               bool = ConfigExtractor('config.ides')
    decrease_attempts_on_user_code_failure:      bool = ConfigExtractor('config.ides')
    encrypt_alpha_mode:                           str = ConfigExtractor('config.ides')
    encrypt_corrections_and_rems:                bool = ConfigExtractor('config.ides')
    forbid_corr_and_REMs_with_infinite_attempts: bool = ConfigExtractor('config.ides')
    forbid_hidden_corr_and_REMs_without_secrets: bool = ConfigExtractor('config.ides')
    forbid_secrets_without_corr_or_REMs:         bool = ConfigExtractor('config.ides')
    show_only_assertion_errors_for_secrets:      bool = ConfigExtractor('config.ides')
    _default_ide_height_lines:                    int = ConfigExtractor('config.ides', deprecated=True)
    _max_attempts_before_corr_available:          int = ConfigExtractor('config.ides', deprecated=True)
    _show_assertion_code_on_failed_test:         bool = ConfigExtractor('config.ides', deprecated=True)

    forbid_no_correct_answers_with_multi: bool = ConfigExtractor('config.qcms')
    _hide:                                bool = ConfigExtractor('config.qcms', deprecated=True)
    _multi:                               bool = ConfigExtractor('config.qcms', deprecated=True)
    _shuffle:                             bool = ConfigExtractor('config.qcms', deprecated=True)

    cut_feedback:                 bool = ConfigExtractor('config.terms')
    stdout_cut_off:                int = ConfigExtractor('config.terms')
    _default_height_ide_term:      int = ConfigExtractor('config.terms', deprecated=True)
    _default_height_isolated_term: int = ConfigExtractor('config.terms', deprecated=True)

    _scripts_url: str = ConfigExtractor('config._others', deprecated=True)
    _site_root:   str = ConfigExtractor('config._others', deprecated=True)

    _dev_mode:               bool = ConfigExtractor('config')
    include_dir:              str = ConfigExtractor('config')
    include_yaml:       List[str] = ConfigExtractor('config')
    j2_block_end_string:      str = ConfigExtractor('config')
    j2_block_start_string:    str = ConfigExtractor('config')
    j2_variable_end_string:   str = ConfigExtractor('config')
    j2_variable_start_string: str = ConfigExtractor('config')
    module_name:              str = ConfigExtractor('config')
    modules:            List[str] = ConfigExtractor('config')
    on_error_fail:           bool = ConfigExtractor('config')
    on_undefined:             str = ConfigExtractor('config')
    render_by_default:       bool = ConfigExtractor('config')
    verbose:                 bool = ConfigExtractor('config')
    # ARGS EXTRACTOR TOKEN



    #----------------------------------------------------------------------------
    # WARNING: the following properties are assigned from "other places":
    #   - page:   from the original MacrosPlugin
    #   - _conf: from PyodideMacrosPlugin.on_config

    page: Page  # just as a reminder: defined by MacrosPlugin

    _conf: MkDocsConfig

    docs_dir_path: Path
    """ Current docs_dir of the project as a Path object (ABSOLUTE path) """

    docs_dir_cwd_rel: Path
    """ docs_dir Path object, but relative to the CWD, at runtime """

    _macro_with_indent_pattern:re.Pattern = None
    """
    Pattern to re.match macro calls that will need to handle indentation levels.
    Built at runtime (depends on `macro_with_indents`)
    """

    #----------------------------------------------------------------------------
    # Also transferred to JS CONFIG:

    base_url:str = ""
    button_icons_directory:str = ""
    pmt_url:str = 'https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme'
    version:str = __version__
    in_serve:bool = False
    lang:Lang = None
    language:str = 'fr'



    @property
    def directory_urls_is_false(self):
        """ Return True if config.use_directory_urls is false. """
        return not self._conf.use_directory_urls



    # Override MacroPlugin
    def on_config(self, config:MkDocsConfig):       # pylint: disable=missing-function-docstring

        dct       = LangBase.get_langs_dct()
        self.lang = dct[self.language]
        PLUGIN_CONFIG_SRC.update_lang_defaults_with_current_lang(self)
        JsDumper.register_env_with_lang(self)

        super().on_config(config)   # pylint: disable-next=no-member
                                    # MacrosPlugin is actually "next in line" and has the method


    # Override MacroPlugin
    def macro(self, func, name=""):     # pylint: disable=arguments-renamed
        """
        Add an extra wrapper around the macro, so that the different classes can inject
        their logic around the macros calls themselves, when needed.
        """
        name = name or func.__name__

        @wraps(func)
        def wrapper(*a,**kw):
            """ Delegate the macro execution to the instance method : allow each Maestro level to
                apply its own/dedicated logic, keeping everything perfectly self contained and
                consistent.
                (This is complex, but this is a beautiful piece of logic... XD )
            """
            return self.apply_macro(name, func, *a, **kw)


        # Raise if different macros are registered with the same name (unless allowed).
        # Note: the macro plugin creates a fresh dict on each on_config hook.
        if self.forbid_macros_override and name in self.macros:
            raise PyodideMacrosError(
                f'A macro named "{name}" has already been registered, possibly by the theme '
                f'itself.\nPlease remove or rename the { name } macro is in the module: '
                f'{ func.__module__ }'
            )

        wrapper.__name__ = wrapper.__qualname__ = name
        return super().macro(wrapper, name)



    def apply_macro(self, name, func, *a, **kw):            # pylint: disable=unused-argument
        """ Root method: just call the macro... """
        return func(*a, **kw)



    #----------------------------------------------------------------------------



    def file_location(self, page:Optional[Page]=None):
        """
        Path to the current file, relative to the cwd.
        """
        page = page or getattr(self, 'page', None)
        if not page:
            raise BuildError("No page defined yet")
        return f"{ self.docs_dir_cwd_rel }/{ page.file.src_uri }"



    def level_up_from_current_page(self, url:str=None) -> str:
        """
        Return the appropriate number of ".." steps needed to build a relative url to go from the
        current page url back to the root directory.

        Note there are no trailing backslash.

        @url: relative to the docs_dir (ex: "exercices/ ..."). If None, use self.page.url instead.
        """
        url           = self.page.url if url is None else url
        page_loc:Path = self.docs_dir_path / url
        segments      = page_loc.relative_to(self.docs_dir_path).parts
        out           = ['..'] * ( len(segments) - self.directory_urls_is_false )
        return '/'.join(out) or '.'



    #----------------------------------------------------------------------------



    def rebase(self, base_url:str):
        """
        Necessary for development only (to replace the wrong base_url value during a serve in the
        theme project)
        NOTE:
            - Keep in mind the base_url SOMETIMES ends with a slash...
            - Also called for main.html through jinja context (but not only)
        """
        return base_url if base_url!='/' else '.'



    def dump_to_js_config(self, base_url):
        """
        Create the <script> tag that will add all the CONFIG properties needed in the
        JS global config file, and also applies the post conversion where needed.

        !!! WARNING !!!
            1. This method is called from the main.html template, through jinja logistic, so
               self.page HAS NO MEANING here!
            2. It is also called from devops hooks to generate the placeholders in the
               `0_config-libs.js` file, hacking the call directly on the class, with
               None in place of self.
        """

        # The Lang dump requires a slightly different logic, so it is handled separately.
        # WARNING: the below call HAS to be a static method, because self _may_ be None, here...
        with BaseMaestro._to_dumpable_state(self, base_url):
            dump_dct         = dump_and_dumper(TO_DUMP_TO_CONFIG, self, json.dumps)
            dump_dct['lang'] = Lang.dump_as_str(self and self.lang)


        if self:
            dumped = BaseMaestro._dump_script_config_for_page(dump_dct)
        else:
            dumped = BaseMaestro._dump_config_partial_json_obj_placeholders(dump_dct)

        return dumped


    @staticmethod
    def _dump_script_config_for_page(dump_dct: Dict[str,Any]):
        dumping = [
            f"\n  CONFIG.{ prop } = { val }" for prop,val in dump_dct.items()
        ]
        return f'<script type="application/javascript">{ "".join(dumping) }</script>'


    @staticmethod
    def _dump_config_partial_json_obj_placeholders(dump_dct: Dict[str,Any]):
        dumping = [ f"\n    { prop }: { val }," for prop,val in dump_dct.items() ]
        return ''.join(dumping)



    @staticmethod
    @contextmanager
    def _to_dumpable_state(maestro: Optional['BaseMaestro'], base_url:str):
        """
        If maestro is None, the dump is done tu update the placeholders in 0_config-libs.js and
        nothing special needs to be done.
        Otherwise, some data of the BaseMaestro instance need to be updated to prepare the actual
        dump, with setup + teardown logic (teardown enforced in a finally clause).
        """
        if maestro:
            if maestro._dev_mode:
                TO_DUMP_TO_CONFIG.append('_dev_mode')

            base_url = maestro.rebase(base_url).rstrip('/')
            maestro.base_url = base_url
            maestro.button_icons_directory = f"{base_url}/{ICONS_IN_TEMPLATES_DIR}"

            # Handling of python_libs is ugly AF, but I need to convert the python_libs relative
            # paths to strings for JS dump purpose, then back to python_libs...
            # And because of the ConfigExtractor descriptor, I cannot reassign the property,
            # so work but mutation:
            src_python_libs = maestro.python_libs[:]
            maestro.python_libs[:] = ( s.split('/')[-1] for s in src_python_libs )

        try:
            yield None

        finally:        # Make absolutely sure the original state of python_libs will be restored
            if maestro:
                if maestro._dev_mode:
                    TO_DUMP_TO_CONFIG.pop()
                maestro.python_libs[:] = src_python_libs



    #----------------------------------------------------------------------------



    def _omg_they_killed_keanu(self,page_name:str, page_on_context:Page=None):
        """ Debugging purpose only. Use as breakpoint utility.
            @page_on_context argument used when called "outside" of the macro logic (fro example,
            in external hooks)
        """
        page = page_on_context or self.page
        if page_name == page.url:
            logger.error("Breakpoint! (the CALL to this method should be removed)")



    def warn_unmaintained(self, that:str=None, *, msg:str=None):
        """
        Generic warning message for people trying to used untested/unmaintained macros.
        """
        msg = msg or (
            f"{ that.capitalize() } has not been maintained since the original pyodide-mkdocs "
            "project, may not currently work, and will be removed in the future.\n"
            "Please open an issue on the pyodide-mkdocs-theme repository, if you need it.\n\n"
            f"\t{ self.pmt_url }.\n"
            "If you absolutely need to pass the build right now, you can change the plugin option "
            "build.deprecation_level to 'warn'."
        )

        if self.deprecation_level == 'error':
            raise PyodideMacrosDeprecationError(msg)

        logger.error(msg)
