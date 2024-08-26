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


from dataclasses import dataclass
from textwrap import dedent
from typing import Tuple

from .sub_config_src import SubConfigSrc, ConfigOptionSrc












@dataclass
class MacroConfigSrc(SubConfigSrc):
    """
    Specific class dedicated to represent the config of a macro call, with it's
    arguments and specific behaviors (see pmt_macros, for example).
    """


    is_macro: bool = True
    """ Override parent value """

    kwarg_index: int = None     # Failure if not properly computed
    """
    Index of the first kwarg in the macro call (= where to insert a `*,` when
    building the signature).
    """


    def __post_init__(self):

        super().__post_init__()
        elements: Tuple['ConfigOptionSrc'] = self.elements      # linting purpose

        positionals = tuple(
            arg for arg in elements if not arg.is_config and arg.is_positional
        )
        start_args = elements[:len(positionals)]
        if start_args != positionals:
            raise ValueError(dedent(f"""
                Positional arguments in { self } definition should come first:
                    Positional args found: {', '.join(arg.name for arg in positionals)}
                    Order of declaration:  {', '.join(arg.name for arg in elements)}
            """))

        last_pos_arg_is_varargs = positionals[-1].name.startswith('*')
        self.kwarg_index        = 0 if last_pos_arg_is_varargs else len(positionals)



    def as_docs_table(self):
        """
        Converts all arguments to a 3 columns table (data rows only!):  name + type + help.
        No indentation logic is added here.
        """
        return '\n'.join(
            arg.as_table_row(False) for arg in self.subs_dct.values() if arg.in_macros_docs
        )


    def signature_for_docs(self):
        """
        Converts the SubConfigSrc to a python signature for the docs, ignoring arguments that
        are not "in_macros_docs".
        """
        args = [arg for arg in self.subs_dct.values() if arg.in_macros_docs]
        size = max( arg.doc_name_type_min_length for arg in args )
        lst  = [ arg.signature(size) for arg in args ]

        if self.kwarg_index:
            lst.insert(self.kwarg_index, "\n    *,")

        return f"""
```python
{ '{{' } { self.name }({ ''.join(lst) }
) { '}}' }
```
"""
