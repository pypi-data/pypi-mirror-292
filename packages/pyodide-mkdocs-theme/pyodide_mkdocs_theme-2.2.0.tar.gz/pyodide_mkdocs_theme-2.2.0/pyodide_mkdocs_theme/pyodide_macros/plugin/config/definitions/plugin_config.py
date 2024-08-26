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


from typing import List
from mkdocs.config import config_options as C



from .._macros_plugin_check_data import _SRC_MACROS_CONF
from ..common_tree_src import CommonTreeSrc
from ..config_option_src import ConfigOptionSrc
from ..plugin_config_src import PluginConfigSrc
from .docs_dirs_config import DOCS_CONFIG, to_page
from .macros_configs import ARGS_MACRO_CONFIG
from .sub_configs import (
    BUILD_CONFIG,
    IDES_CONFIG,
    TERMS_CONFIG,
    QCMS_CONFIG,
    OTHERS_CONFIG,
)




DEFAULT_J2_STRING          = _SRC_MACROS_CONF['include_dir'].default
DEFAULT_MODULE_NAME        = _SRC_MACROS_CONF['module_name'].default
DEFAULT_UNDEFINED_BEHAVIOR = _SRC_MACROS_CONF['on_undefined'].default
MKDOCS_MACRO_CONFIG_URL    = "https://mkdocs-macros-plugin.readthedocs.io/en/latest/#configuration-of-the-plugin"




CommonTreeSrc.DEFAULT_DOCS_URL_TEMPLATE = to_page(DOCS_CONFIG) / '#{py_macros_path}'


PLUGIN_CONFIG_SRC = PluginConfigSrc(
    docs = """
        La configuration du plugin, `PyodideMacrosConfig`, reprend également toutes les options du
        plugin original `MacrosPlugin`, ce qui permet d'en réutiliser toutes les fonctionnalités.
        <br>Ces options, décrites succinctement ci-dessous, sont disponibles à la racine de la
        configuration du plugin, dans `mkdocs.yml:plugins.pyodide_macros` (voir [en haut de cette
        page](--global-architecture)).

        Pour plus d'informations à leur sujet ou concernant le fonctionnement general des macros :

        - [GitHub repository][mkdocs-macros]{: target=_blank }
        - [Help page](https://mkdocs-macros-plugin.readthedocs.io/en/latest/){: target=_blank }
        - [Configuration information](https://mkdocs-macros-plugin.readthedocs.io/en/latest/#
        configuration-of-the-plugin){: target=_blank }
    """,
    yaml_desc = "PMT's plugin configuration : `PyodideMacrosPlugin`.",
    # yaml_desc = "Configuration du plugin du thème PMT : `PyodideMacrosPlugin`.",
    elements = (

    ARGS_MACRO_CONFIG,
    BUILD_CONFIG,
    IDES_CONFIG,
    TERMS_CONFIG,
    QCMS_CONFIG,
    OTHERS_CONFIG,

    ConfigOptionSrc(
        '_dev_mode', bool, default=False, in_yaml_docs=False,
        docs = "Lance le plugin en mode de développement (...ne pas utiliser ceci).",
        yaml_desc="Run the plugin in development mode (...don't use that).",
    ),


    # ---------------------------------------------------------------------------------------
    # Replication of MacrosPlugin options (merging the config_scheme properties programmatically
    # is not enough, unfortunately...)


    ConfigOptionSrc(
        'include_dir', str, default=DEFAULT_J2_STRING,
        docs = """
            Répertoire de [fichiers externes à inclure][macros-include_dir]{: target=_blank }.
        """,
        yaml_desc = "Directory for including external files.",
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'include_yaml', List[str], conf_type=C.ListOfItems(C.Type(str), default=[]),
        docs = """
            Pour inclure des [fichiers de données externes][macros-include_yaml]{: target=_blank }.
        """,
        yaml_desc = "To include external data files.",
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'j2_block_start_string', str, default=DEFAULT_J2_STRING,
        docs = """
            Pour changer la syntaxe par défaut des ouvertures de blocs Jinja2 (défaut:
            {% raw %}`{%`{% endraw %}).
        """,
        yaml_desc="""
            Non-standard Jinja2 marker for start of block (default: `{%`).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'j2_block_end_string', str, default=DEFAULT_J2_STRING,
        docs = """
            Pour changer la syntaxe par défaut des fermetures de blocs Jinja2 (défaut:
            {% raw %}`%}`{% endraw %}).
        """,
        yaml_desc="""
            Non-standard Jinja2 marker for end of block (default: `%}`).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'j2_variable_start_string', str, default=DEFAULT_J2_STRING,
        docs = """
            Pour changer la syntaxe par défaut des ouvertures de variables Jinja2 (défaut:
            {% raw %}`{{`{% endraw %}).
        """,
        yaml_desc="""
            Non-standard Jinja2 marker for start of variables (default: `{{`).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'j2_variable_end_string', str, default=DEFAULT_J2_STRING,
        docs = """
            Pour changer la syntaxe par défaut des fermetures de variables Jinja2 (défaut:
            {% raw %}`}}`{% endraw %}).
        """,
        yaml_desc="""
            Non-standard Jinja2 marker for end of variables (default: `}}`).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'module_name', str, default=DEFAULT_MODULE_NAME,
        docs = """
            Nom du module/package python contenant vos macros personnalisées, filtres et variables.
            Utiliser nom de fichier (sans extension), un nom de dossier, ou un chemin relatif
            (dossiers séparés par des slashes: `dossier/module`).
        """,
        yaml_desc="""
            Name of the Python module containing custom macros, filters and variables (file without
            extension or directory).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
        # yaml_desc="Nom du module/dossier contenant les macros personnalisées, filtres et variables (pas d'extension).",
        # """
        # Name of the Python module containing custom macros, filters and variables. Indicate the file or
        # directory, without extension; you may specify a path (e.g. include/module). If no main
        # module is available, it is ignored.
        # """
    ),

    ConfigOptionSrc(
        'modules', List[str], conf_type=C.ListOfItems(C.Type(str), default=[]),
        docs = """
            Liste de [pluglets][macros-pluglets]{ target=_blank } à ajouter aux macros
            (= modules de macros qui peuvent être installés puis listés  avec `pip list`).
        """,
        yaml_desc="""
            List of pluglets to be added to mkdocs-macros (preinstalled Python modules that
            can be listed by pip list).
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'on_error_fail', bool, default=False,
        docs = "Interrompt le `build` si une erreur est levée durant l'exécution d'une macro.",
        yaml_desc="Make the building process fail in case of an error during macro rendering.",
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'on_undefined', str, default=DEFAULT_UNDEFINED_BEHAVIOR,
        docs = "Comportement à adopter quand une macro rencontre une variable non définie lors des "
               "rendus. Par défaut, les expressions Jinja ne sont alors pas modifiées dans la page "
               "markdown. Utiliser `'strict'` pour provoquer une erreur.",
        yaml_desc = """
            Behavior of the macros renderer in case of undefined variables in a page.
        """,
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),

    ConfigOptionSrc(
        'render_by_default', bool, default=True,
        docs           = "Exécute les macros dans toutes les pages ou non.",
        yaml_desc      = "Execute all the macros in the pages or not.",
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
        # yaml_desc="`True`: les macros sont exécutées par défaut. `False`: stratégie \"opt-in\"",
        # """
        # Render macros on all pages by default. If set to false, sets an opt-in mode where only
        # pages marked with render_macros: true in header will be displayed.
        # """
    ),

    ConfigOptionSrc(
        'verbose', bool, default=False,
        docs = """
            Affiche plus d'informations dna le terminal sur les étapes de rendu des macros si
            passé à `True` lors d'un build/serve.
        """,
        yaml_desc = "Print debug (more detailed) statements in the console.",
        schema_md_link = MKDOCS_MACRO_CONFIG_URL,
    ),
    )
)
