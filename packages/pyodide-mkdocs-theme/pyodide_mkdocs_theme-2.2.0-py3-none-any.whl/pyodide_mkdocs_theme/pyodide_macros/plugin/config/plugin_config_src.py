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


from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import ClassVar, Dict, List, TYPE_CHECKING

from mkdocs.exceptions import ConfigurationError, BuildError



from .dumpers import AccessorsDumper, BaseMaestroGettersDumper
from ..maestro_tools import ConfigExtractor
from .config_option_src import ConfigOptionSrc
from .sub_config_src import SubConfigSrc
from .macro_config_src import MacroConfigSrc


if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin







@dataclass
class PluginConfigSrc(SubConfigSrc):
    """
    Top level element defining the plugin's config.
    It also holds various data helpers, to access some ConfigOptionSrc, or trigger proper
    initializations of various sub elements.


    # Lifetime of this object/tree:


    * Created  _BEFORE_ mkdocs even starts running (because created when the modules are imported)

    * Lives throughout the entire build/serve.

    * Values depending on the serve/build should most likely be updated during `on_config` (lang
      stuff, deprecation reassignments, ...).
      NOTE: code updates are done through `mkdocs_hooks.on_config`, which is triggered before any
            other `on_config` method (priority 3000)

    * _NONE OF THE VALUES REPRESENT ANYTHING TRUSTABLE AT RUNTIME:_ the live config of the plugin
      must be used to get them :
        - either through env.ConfigExtractor getters,
        - or using ConfigOption.get_current_value(env), which will extract the live value
          automatically.
    """

    is_plugin_config: bool = True
    """ Override parent value """

    is_first_build: bool = True
    """ Used to apply some actions only on the first build (for serve operations). """

    __all_options: List[ConfigOptionSrc] = field(default_factory=list)

    __all_macros_configs: Dict[str, MacroConfigSrc] = field(default_factory=dict)


    PLUGIN_NAME: ClassVar[str] = 'pyodide_macros'


    def __post_init__(self):
        if self.name:
            raise ConfigurationError('PluginConfigSrc: no name argument should be given.')

        self.name = 'config'
        super().__post_init__()

        AccessorsDumper.apply(self, self.__all_options, self.__all_macros_configs)


    def get_plugin_path(self, option_path:str, no_deprecated:bool=False):
        """
        Validate the given `option_path` (not including "config") and return the equivalent
        `py_yaml_path`.
        """
        attrs = option_path.split('.')
        obj = self
        if no_deprecated:
            for key in attrs:
                obj = obj.subs_dct[key]
                if obj.is_deprecated:
                    raise BuildError(f"{ option_path } is deprecated")
        else:
            for key in attrs:
                obj = obj.subs_dct[key]
        return obj.py_macros_path


    def update_lang_defaults_with_current_lang(self, env:'PyodideMacrosPlugin'):
        """
        Update The default values onc env.lang has been assigned.
        """
        assert env.lang, "env.lang should already be assigned."
        for arg in self.__all_options:
            arg.assign_lang_default_if_needed(env)



    def build_base_maestro_getters(self):
        """
        Build the code declaring all the ConfigExtractor getters for the BaseMaestro class
        declaration.
        """
        return BaseMaestroGettersDumper.apply(self)



    def handle_deprecated_options(self, env:'PyodideMacrosPlugin'):
        """
        Reassign values set on deprecated
        """

        ConfigExtractor.RAISE_DEPRECATION_ACCESS = False

        used = []
        for option in self.__all_options:
            if not option.is_deprecated:
                continue

            value = option.get_current_value(env)
            if value is not None:
                msg = option.get_deprecation_message_and_reassign_if_moved(env, value)
                used.append(msg)


        if self.is_first_build and used:
            self.is_first_build = False
            env.warn_unmaintained( msg=
                "The following options should be removed or updated according to the given "
               +"information.\nIf you absolutely need to pass the build right now, you can "
               +"change the plugin option build.deprecation_level to 'warn'.\nNote these "
               +"options will be removed in near future .\n\n"
               +'\n---\n'.join(used)
            )

        # Activate PMT defensive programming against deprecated properties usage:
        ConfigExtractor.RAISE_DEPRECATION_ACCESS = True




    def assign_defaults_to_macro_call_args(
        self, name:str, args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'
    ):
        """
        If the given macro matches a macro of the theme, modify the args and/or kwargs
        to add the missing arguments, using the current global config (MaestroMeta having
        swapped the config already, if needed).
        """
        if name == 'IDEv':
            name = 'IDE'

        if name not in self.__all_macros_configs:
            return args, kwargs

        macro_src = self.__all_macros_configs[name]
        for arg_name, arg in macro_src.subs_dct.items():

            if not arg.in_config:                                   # not handled
                continue

            if arg.is_positional and arg.index >= len(args):        # Add missing varargs
                args += ( arg.get_current_value(env), )

            elif not arg.is_positional and arg_name not in kwargs:  # Add missing kwargs
                kwargs[arg_name] = arg.get_current_value(env)

        return args, kwargs



    def to_docs_page_header(self):
        old_anchor = 'pyodide_mkdocs_theme.pyodide_macros.plugin.config.PyodideMacrosConfig'

        return f"{'{{'}anchor_redirect(id='{ old_anchor }'){'}}'} `#!py PyodideMacroConfig`"


    def as_mkdocs_yml_line(self):
        return f"{ self.indent }- {self.PLUGIN_NAME }:"


    def to_yaml_schema(self, site_url:Path) -> str:
        """
        Converts the current configSrc hierarchy to the equivalent json code to validate
        the yaml schema.
        """
        inner_schema = self.build_yaml_schema(site_url)
        inner_schema['title'] = self.PLUGIN_NAME

        python_schema = {
            "$schema": "http://json-schema.org/draft-07/schema",
            "title": self.PLUGIN_NAME,
            "markdownDescription": inner_schema["markdownDescription"],
            "oneOf": [
                {"const": self.PLUGIN_NAME},
                {
                    "type": "object",
                    "properties": {self.PLUGIN_NAME: inner_schema},
                    "additionalProperties": False
                }
            ]
        }
        str_schema = json.dumps(python_schema, indent=2)
        return str_schema
