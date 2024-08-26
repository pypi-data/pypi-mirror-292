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





/**Explore the user's code to find missing modules to install. If some are found, load
 * micropip (if not done yet), then install all the missing modules.
 * Also import all the packages present in runner.whiteList.
 *
 * NOTE: python libs are identified peeking into the global config, but are actually
 * loaded only if they are available in the instance property (this is to limit the
 * _SAVAGE_ unexpected installations of random packages from PyPI).
 * */
const installPythonPackages=(function(){

  /*Things are complicated, here...:
   *
   *    * Installing packages via micropip doesn't actually import them in the environment (it
   *      works the same for custom python libs).
   *    * The theme needs to know up front what packages are missing or not, to decide when to
   *      display installation messages or not.
   *    * _Installed_ packages can be found through micropip, but not _loaded_ pythonLibs.
   *
   *    So, spotting missing packages relies on picking in sys.modules, BUT they actually end
   *    up there _ONLY_ if a python code actually imported them, going through `import xxx`.
   *
   *    So far, so good. Problems arise with additional features:
   *
   *    * White lists:
   *        - their content has to be actually imported in the global scope, so that they are
   *          actually available to the user.
   *
   *    * Custom libs:
   *        - They have to be imported in pyodide _right now_, so that they end up listed in
   *          `sys.modules`.
   *        - This makes them visible as "installed" on a next import/installation attempt...
   *        - ...which may occur right after the current call because imports in terminals commands
   *          may go through env, then envTerm, and BOTH will check if an import has to be done in
   *          the terminal command.
   *
   *    * Packages with different installation and import names (ex: Pillow vs PIL):
   *        Packages whose the installation name differs from the import name have to be
   *        automatically imported for the user, so that they are usable in the "triggering" code.
   *
   *    * Exclusions:
   *        - They are not applied on env sections, so modules _can_ be installed/loaded here
   *          so they _have_ to be actually imported...
   *        - ..._BUT_ hidden inside a function, so that they do not leak in the global scope.
   *        - Then the redactor's import (from the `env` or `env_term` code itself) will determine
   *          if the module ends up in the global scope or not.
   *
   *    For those reasons, all packages that are "installed" will always be imported in a hidden
   *    scope, so that they get registered in sys.modules.
   *
   *    Since the "triggering code" (env code, user code, cmd, ...) still has to be executed, the
   *    actual visibility of the imported module is left to the redactor/user, and:
   *        - All automatic installs/imports are done in a hidden scope.
   *        - Packages of the whiteList are all imported in the global scope, whatever happens/the
   *          configuration of exclusions/sections, ...
   **/


  const featureRunner=(feature, convertOutput)=>(...args)=>{
    let code = pyodideFeatureCode(feature, ...args)
    let out  = pyodide.runPython(code)
    if(convertOutput) out = convertOutput(out)
    return out
  }

  /**IMPORTS_CONFIG type:
   *
   *      Record<string, {
   *          toImport: string,       // Automatic import name (in hidden scope)
   *          toInstall: string,      // Micropip installation name
   *          post: Cbk,              // Callback to run to apply any kind of extra logic
   *      }>
   * */
  const IMPORTS_CONFIG = {
    PIL:        {toInstall: "Pillow"},
    matplotlib: {post: featureRunner('pyodidePlot')}
  }

  const installConfigFor=(libName)=>({
    toImport:  libName,
    toInstall: libName,
    post:      ()=>undefined,
    ...IMPORTS_CONFIG[libName] || {}
  })


  /**Extract all the packages names currently available in pyodide. */
  const getAlreadyImportedPackages = featureRunner("alreadyImported", out=>new Set(out.split(' ')) )

  /**Rely on pyodide to analyze the code content and find the imports the user is trying to use. */
  const getWantedImports = featureRunner("wantedImports")

  // Predicate factories...:
  const isAvailablePythonLib = (runner) => (name) => runner.pythonLibs.has(name)
  const isNotKnownPythonLib  = (name) => !CONFIG.pythonLibs.has(name)
  const isNeededAndAllowedInstall = (installedModules, runtime, isFromEnv) => (
    isFromEnv ? name => !installedModules.has(name)
              : name => !installedModules.has(name) && !runtime.excluded.includes(name)
  )



  let micropip, runtime;
  const enforceImports = []   // python imports to make sure python_libs are showing up in sys.modules

  /**Routine managing the actual import logic, storing the name of the module/package
   * to import later (hidden scope).
   *
   * @returns: the actual config object.
   * */
  const importFinalizer = (name) =>{
    const conf = installConfigFor(name)
    const importCode = `import ${ conf.toImport }`
    enforceImports.push( importCode )
    return conf
  }


  /**Install an available custom python lib.
   * */
  const installCustomPythonLib = async (libName) => {
    jsLogger("[PythonLibs] - Install", libName)

    const archive     = `${ CONFIG.baseUrl }/${ libName }.zip`
    const zipResponse = await fetch(archive)
    const zipBinary   = await zipResponse.arrayBuffer()
    pyodide.unpackArchive(zipBinary, "zip", {extractDir: libName})
    const conf = importFinalizer(libName)
    conf.post()
  }


  /**Install an external python package (through pyodide's default behaviors: micropip+PyPI).
   * */
  const installExternalPackage = async (libName) => {
    jsLogger("[Micropip] - Install", libName)

    if(!micropip){
      await pyodide.loadPackage("micropip");
      micropip = pyodide.pyimport("micropip");
    }
    const conf = importFinalizer(libName)
    await micropip.install(conf.toInstall)
    conf.post()
  }


  // ------------------------------------------------------------------------------


  return async (runner, code, _runtime, _isFromEnv)=>{
    jsLogger('[checkPoint] - installPythonPackages', _isFromEnv?'isFromEnv':'')

    // Refresh globals:
    runtime   = _runtime
    isFromEnv = _isFromEnv
    enforceImports.length = 0

    // Analyze what's supposed to be done, depending on the code du execute later and
    // various config flags:
    const importedModules  = getAlreadyImportedPackages()
    const installPredicate = isNeededAndAllowedInstall(importedModules, runtime, isFromEnv)
    const missingWhiteList = runner.whiteList.filter(name=>!importedModules.has(name))
    const installNeeded    = getWantedImports(code).filter(installPredicate).concat(missingWhiteList)
    const externalsMissing = installNeeded.filter(isNotKnownPythonLib)
    const pyLibsMissing    = installNeeded.filter(isAvailablePythonLib(runner))

    /*
    externalsMissing:
          Imports names that will attempt installation from PyPI.
          Using CONFIG.pythonLibs so that an unavailable custom lib doesn't trigger a "savage
          install" from PyPI.

    pyLibsMissing:
          Import names matching an available python_lib.
          Using this.pythonLibs because only the available ones can be downloaded.
    */

    // Actual installations:
    if(pyLibsMissing.length || externalsMissing.length){
      runner.giveFeedback(CONFIG.lang.installStart.msg)

      for(const lib of pyLibsMissing)    await installCustomPythonLib(lib)
      for(const lib of externalsMissing) await installExternalPackage(lib)

      runner.giveFeedback(CONFIG.lang.installDone.msg)
    }

    // Enforce imports of all installed modules in hidden scope
    // (not using the auto_run decorator because it might not be already in place):
    if(enforceImports.length){
      pyodide.runPython(`
def _hack_imports():
    ${ enforceImports.join('\n    ') }
_hack_imports()
del _hack_imports`)
    }

    // Make sure white listed packages are always visible in the user's scope:
    if(runner.whiteList.length){
      pyodide.runPython( runner.whiteList.map(lib=>'import '+lib).join('\n') )
    }
  }
})()
