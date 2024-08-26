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
from pathlib import Path
from typing import ClassVar, Dict, Tuple, Type, Union

from mkdocs.config import config_options as C

from ..maestro_tools import CopyableConfig
from .common_tree_src import CommonTreeSrc, YamlSchema
from .config_option_src import ConfigOptionSrc








@dataclass
class SubConfigSrcBase(CommonTreeSrc):
    """
    Class making the link between:
        - The actual python implementation
        - The docs content (avoiding out of synch docs)
        - The Config used for the .meta.pmt.yml features. Note that optional stuff "there" is
          different from an optionality (or it's absence) in the running macro/python layer.

    Those instances represent the config "starting point", so all defaults are applied here,
    for the Config implementation.
    When extracting meta files or meta headers, the CopyableConfig instances will receive dicts
    from the yaml content, and those will be merged in the current config. This means the dict
    itself can contain only partial configs, it's not a problem.
    The corollary of this, is that _only_ values that could be None at runtime as an actual/useful
    value should be declared as `C.Optional`.
    """

    subs_dct: Dict[str,'ConfOrOptSrc'] = field(default_factory=dict)
    """ Children elements (stays empty for ConfigOptionSrc instances). """

    is_config: bool = True
    """ Override parent value. """


    BASES: ClassVar[Tuple[Type]] = (CopyableConfig,)
    """ Extensions for the Mkdcos Config object to create from the current instance. """


    def __post_init__(self):
        super().__post_init__()
        self.subs_dct = {arg.name: arg for arg in self.elements}

        if len(self.subs_dct) != len(self.elements):
            raise ValueError(
                f"{ self }: duplicated name for sub config elements." + ''.join(
                    f"\n    {elt}" for elt in self.elements
                )
            )


    def __getattr__(self, prop):
        if prop not in self.subs_dct:
            raise AttributeError(f"{ self }: no { prop } attribute")
        return self.subs_dct[prop]


    def to_config(self):
        """ Convert recursively to the equivalent CopyableConfig object. """

        class_name = self.get_base_config_option_classname()
        body = {
            name: below.to_config()
                for name,below in self.subs_dct.items()
                if below.in_config
        }
        body['__docs__'] = self.docs

        kls = type(class_name, self.BASES, body)
        return kls if self.is_plugin_config else C.SubConfig(kls)




class SubConfigSrcWithDocsOrYaml(SubConfigSrcBase):

    def to_docs_page_header(self):
        config_name = self.get_base_config_option_classname()
        return (
            f"{'{{'} anchor_redirect(id={ self.mkdocstrings_id !r}) {'}}'}"
            f"`#!py { config_name }`"
        )


    def to_docs_page_content(self):
        bases = ', '.join(kls.__name__ for kls in self.BASES)
        if len(self.BASES) > 1:
            bases = f"({ bases })"
        return f"Bases: `#!py { bases }`\n\n{ self.docs }"


    #----------------------------------------------------------------------------


    def as_mkdocs_yml_line(self):
        return f"{ self.indent }{ self.name }:"



    def build_yaml_schema(self, site_url:Path) -> YamlSchema :
        props = {}
        for elt in self.elements:
            if elt.in_yaml_docs or elt.name == '_dev_mode':
                schema = elt.build_yaml_schema(site_url)
                if schema:
                    props[elt.name] = schema

        return  {
            "markdownDescription": self.get_yaml_md_infos(site_url),
            "title": self.name,
            "type": "object",
            "properties": props,
            "additionalProperties": False,
        } if props else {}













class SubConfigSrc(
    SubConfigSrcWithDocsOrYaml,
    SubConfigSrcBase,
):
    pass




ConfOrOptSrc = Union[ConfigOptionSrc, SubConfigSrc]
"""
Union type: regroup instances of ConfigOptionSrc and SubConfigSrc (basically,
revolves around the behaviors of CommonTreeSrc).
"""
