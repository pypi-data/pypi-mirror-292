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


from mkdocs_macros.plugin import MacrosPlugin

_EXPECTED_MACRO_CONF = set("""
    module_name
    modules
    render_by_default
    include_dir
    include_yaml
    j2_block_start_string
    j2_block_end_string
    j2_variable_start_string
    j2_variable_end_string
    on_undefined
    on_error_fail
    verbose
""".split())


_SRC_MACROS_CONF             = dict(MacrosPlugin.config_scheme)
_MISSING_MACROS_PLUGIN_PROPS = _EXPECTED_MACRO_CONF  - set(_SRC_MACROS_CONF)
_UNKNOWN_MACROS_PLUGIN_PROPS = set(_SRC_MACROS_CONF) - _EXPECTED_MACRO_CONF

MISSING_MACROS_PROPS = "" if not _MISSING_MACROS_PLUGIN_PROPS else (
    "\nDisappeared from MacrosPlugin:" + ''.join(f'\n\t{name}' for name in _MISSING_MACROS_PLUGIN_PROPS)
)
EXTRAS_MACROS_PROPS = "" if not _UNKNOWN_MACROS_PLUGIN_PROPS else (
    "\nNew config in MacrosPlugin:" + ''.join(f'\n\t{name}' for name in _UNKNOWN_MACROS_PLUGIN_PROPS)
)
