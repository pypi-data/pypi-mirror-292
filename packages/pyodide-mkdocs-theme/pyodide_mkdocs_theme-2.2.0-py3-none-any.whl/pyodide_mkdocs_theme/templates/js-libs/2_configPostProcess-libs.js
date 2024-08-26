/*
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
*/


;`
runScript
installStart
installDone
validation
editorCode
publicTests
secretTests
`.trim().split(/\s+/).forEach( prop =>{
        CONFIG.lang[prop].msg = info(CONFIG.lang[prop].msg)
})

CONFIG.lang.successMsg.msg    = success(CONFIG.lang.successMsg.msg)
CONFIG.lang.unforgettable.msg = warning(CONFIG.lang.unforgettable.msg)
CONFIG.lang.failHead.msg      = warning(CONFIG.lang.failHead.msg)
CONFIG.lang.tests.as_pattern  = new RegExp(CONFIG.lang.tests.as_pattern, 'i')

CONFIG.pythonLibs = new Set(CONFIG.pythonLibs)
