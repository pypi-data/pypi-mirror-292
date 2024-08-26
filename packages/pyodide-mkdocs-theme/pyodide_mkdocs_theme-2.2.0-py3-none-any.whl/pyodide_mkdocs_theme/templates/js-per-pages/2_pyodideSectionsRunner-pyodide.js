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



const isExclusionOrAssertionError=(runtime)=>{
  return runtime.stdErr.startsWith(CONFIG.MSG.exclusionMarker) || runtime.isAssertErr
}




class PyodideSectionsRunner {

  no_undefined = prop =>{
      const getter = v => {
        if(v!==undefined) return v
        throw new Error(`Undefined is not allow: ${this.constructor.name}.${prop}.`)
      }
      return getter
  }

  //JS_CONFIG_DUMP
  get attemptsLeft()      { return this.no_undefined('attemptsLeft')(this.data.attempts_left) }
  get autoLogAssert()     { return this.no_undefined('autoLogAssert')(this.data.auto_log_assert) }
  get corrContent()       { return this.no_undefined('corrContent')(this.data.corr_content) }
  get corrRemsMask()      { return this.no_undefined('corrRemsMask')(this.data.corr_rems_mask) }
  get deactivateStdoutForSecrets(){ return this.no_undefined('deactivateStdoutForSecrets')(this.data.deactivate_stdout_for_secrets) }
  get decreaseAttemptsOnCodeError(){ return this.no_undefined('decreaseAttemptsOnCodeError')(this.data.decrease_attempts_on_code_error) }
  get envContent()        { return this.no_undefined('envContent')(this.data.env_content) }
  get envTermContent()    { return this.no_undefined('envTermContent')(this.data.env_term_content) }
  get excluded()          { return this.no_undefined('excluded')(this.data.excluded) }
  get excludedMethods()   { return this.no_undefined('excludedMethods')(this.data.excluded_methods) }
  get hasCheckBtn()       { return this.no_undefined('hasCheckBtn')(this.data.has_check_btn) }
  get isEncrypted()       { return this.no_undefined('isEncrypted')(this.data.is_encrypted) }
  get isVert()            { return this.no_undefined('isVert')(this.data.is_vert) }
  get maxIdeLines()       { return this.no_undefined('maxIdeLines')(this.data.max_ide_lines) }
  get minIdeLines()       { return this.no_undefined('minIdeLines')(this.data.min_ide_lines) }
  get postContent()       { return this.no_undefined('postContent')(this.data.post_content) }
  get postTermContent()   { return this.no_undefined('postTermContent')(this.data.post_term_content) }
  get prefillTerm()       { return this.no_undefined('prefillTerm')(this.data.prefill_term) }
  get profile()           { return this.no_undefined('profile')(this.data.profile) }
  get publicTests()       { return this.no_undefined('publicTests')(this.data.public_tests) }
  get pyName()            { return this.no_undefined('pyName')(this.data.py_name) }
  get pythonLibs()        { return this.no_undefined('pythonLibs')(this.data.python_libs) }
  get recLimit()          { return this.no_undefined('recLimit')(this.data.rec_limit) }
  get secretTests()       { return this.no_undefined('secretTests')(this.data.secret_tests) }
  get showOnlyAssertionErrorsForSecrets(){ return this.no_undefined('showOnlyAssertionErrorsForSecrets')(this.data.show_only_assertion_errors_for_secrets) }
  get stdoutCutOff()      { return this.no_undefined('stdoutCutOff')(this.data.stdout_cut_off) }
  get userContent()       { return this.no_undefined('userContent')(this.data.user_content) }
  get whiteList()         { return this.no_undefined('whiteList')(this.data.white_list) }
  //JS_CONFIG_DUMP





  constructor(id){
    jsLogger('[checkPoint] - Constructor for', this.constructor.name, id)

    decompressPagesIfNeeded()

    this.id = id
    this.data = PAGE_IDES_CONFIG[id]
    if(CONFIG._devMode)
      CONFIG.objs[this.id] = this
    else{
      delete PAGE_IDES_CONFIG[id]
    }
    this.data.python_libs = new Set(this.data.python_libs)
    this.alreadyRanEnv = false    // Specific to terminals, but defined "for everyone"
    this.pythonCodeRunnerWithCtx = async (ctx)=>{ pyodide.runPython(ctx.code) }

    this.running = undefined   // see CONFIG.running
  }


  build(){}   // For inheritance consistency

  /** Nothing to do by default (specific to IDEs) */
  testSectionEndFeedback(runtime, step){}

  /**Actions to perform when the current code in the editor has been extracted,
   * before anything is run.
   * */
  getCurrentEditorCode(){ return ""}


  /**Store code or command in the python runtime.
   * */
  storeUserCodeInPython(varName, code){
    const showOff = JSON.stringify(code.length>50 ? code.slice(0,50)+' ...' : code)
    jsLogger('[checkPoint] - Store ', varName, showOff)

    // The double quotes are all escaped to make sure no multiline string will cause troubles
    const escapedCode = code.replace(/"/g, '\\"')
    pyodide.runPython(`__builtins__.${ varName } = """${ escapedCode }"""`)
  }


  /**Runners without any terminal won't ever give feedback, unless it's a critical error.
   * In that case, a window alert will be used, so that it doesn't go unnoticed
   * */
  giveFeedback(_, stdErr=""){
    if(stdErr){
      // Format back any escaped square brackets, because window.alert is not the terminal...
      window.alert( unEscapeSqBrackets(stdErr) )
    }
  }





  /**Given an editorName, automatically build the default runtime to pass as argument to the
   * runPythonCodeWithOptionsIfNoStdErr function.
   *
   * This objects is the "per run" state tracker for the executions.
   *
   * The content of the config optional argument will override any basic option, except for
   * the packagesAliases object, where the config.packagesAliases entries will be added.
   *
   * @returns: a RuntimeManager object
   *     @runtime :
   *          .autoLogAssert:   (boolean) If true, will automatically add the code of a failing
   *                            assertion as its message if it doesn't have one already.
   *          .excluded:        (String[]) Instructions to exclude at runtime.
   *          .excludedMethods: (String[]) Methods calls to exclude at runtime (string containment).
   *          .purgeStackTrace: (boolean) Define if the error stacktraces must be removed from messages or not.
   *          .packagesAliases: (Record<string,string>) mapping of imports that should be aliased
   *                            automatically for the user, if they try to import them.
   *          .recLimit:        (number) recursion depth (or -1 if not used)
   *          .runCodeAsync:    async python code runner.
   *          .withStdOut:      (boolean) Display the content of the stdOut or not.
   *          .whiteList:       (Array of strings) list of modules to import before the code
   *                            restrictions are put in place for the user's code.
   * */
  buildRunConfig(){
    jsLogger('[checkPoint] - buildConfig (runtime)')
    return new RuntimeManager(this)
  }









  /**Explore the user's code to find missing modules to install. If some are found, load
   * micropip (if not done yet), then install all the missing modules.
   * Also import all the packages present in runtime.whiteList.
   *
   * NOTE: python libs are identified peeking into the global config, but are actually
   * loaded only if they are available in the instance property (this is to limit the
   * _SAVAGE_ unexpected installations of random packages from PyPI).
   *
   * @code : the python code to run.
   * @runtime :Same as `buildRunConfig`.
   * */
  async installAndImportMissingModules(code, runtime, isFromEnv=false){
    await installPythonPackages(this, code, runtime, isFromEnv)
  }



  /**Creates a generic "action runner", handling the overall security logic, catching exceptions
   * that are thrown up to this point and displaying them in a BigFail-fashion-way in the terminal.
   *
   * Contracts:
   *    - @setup takes the `e` (event) argument only and returns a RuntimeManager instance.
   *      The argument may be:
   *          * either an `Event`: then it has no use.
   *          * or the terminal current command (as `string`) that just got validated in the console.
   *    - @action takes the runtime argument and returns nothing
   *    - @finallyTeardown takes the runtime argument and returns nothing
   *
   * About executions:
   *    - @setup is always run
   *    - @action is always called, and it's its job to decide if it has to actually run its
   *       logic or not, depending on the `runtime` state.
   *    - @finallyTeardown is always called, and should contain all the operations that HAVE
   *       to be run whatever happened before (success/error).
   * */
  lockedRunnerWithBigFailWarningFactory(
    actionName, setup, action, finallyTeardown
  ){
    const loggerName=`[${actionName}]`

    return withPyodideAsyncLock(actionName, async(eventOrCmd)=>{
      if(eventOrCmd && eventOrCmd.preventDefault) eventOrCmd.preventDefault()
      jsLogger(loggerName)

      this.running = actionName
      let runtime
      try{
        runtime = await setup.call(this, eventOrCmd)
        await action.call(this, runtime)

      }catch(e){
        jsLogger("[checkPoint] - BIG FAIL", actionName)

        // If something didn't get caught, it's very wrong... so dump everything to the console
        const stdErr = youAreInTroubles(e)
        this.terminal.error(stdErr)

        if(runtime){                  // (`runtime` may be undefined if the error was in setup...)
          runtime.gotBigFail = true
          runtime.stdErr = stdErr
        }
        throw e

      }finally{
        if(runtime){
          await finallyTeardown.call(this, runtime)
        }
        this.running = "???"
      }
    })
  }





  /**Generic main "action" runner for environment code.
   * */
  async installImportsAndRunEnvCode(ctx, runtime){
    if(!ctx.code) return;
    await installPythonPackages(this, ctx.code, runtime, ctx.isEnvSection)
    await pyodide.runPythonAsync(ctx.code, {filename: `<${ toSnake(ctx.section) }>`})
  }





  /** 1. Refresh the features defined in pyodide environment, in case the user messed with them
   *     (accidentally or not).
   *  2. Then run the content of the `env` section.
   *
   * @returns: [runtime, isOk].
   *     If isOk is false, an error has been raised: this is a CRITICAL ERROR and executions at
   *     upper level must be stopped.
   * */
  async setupRuntime(){
    jsLogger('[checkPoint] - setupRuntime PyodideSectionsRunner')

    // Build the default configuration runtime to use to run the user's code:
    const runtime = this.buildRunConfig()

    let ctx = await runtime.runWithCtx({section:'env', method: this.refreshPyodideFeatures})

    if(ctx.success){
      ctx = await runtime.runWithCtx('env')
      this.alreadyRanEnv = ctx.success
    }
    return runtime
  }


  refreshPyodideFeatures(){
    const features = `
      autoRun
      version
      copyFromServer
      exclusionsTools
      inputPrompt
      mermaidDrawer
      refresher
      upDownLoader
    `.trim().split(/\s+/)
    for(const feature of features){
      const code = pyodideFeatureCode(feature)
      pyodide.runPython( code )
    }
  }







  /**Takes a user code as argument, and run it in the pyodide environment, using various runtime
   * logics. It mutates the RuntimeManager objects on the way, keeping track of the current state
   * of the executions (error or not, keep running or not, ...).
   *
   * @throws: Any JS runtime Error if something went very wrong... (python errors are swallowed
   *          and just printed to the jQuery.terminal)
   * */
  async runPythonCodeWithOptionsIfNoStdErr(code, runtime, testsStep=null){
      jsLogger('[checkPoint] - Enter generic running function')

      // Do nothing if nothing to do...!
      if(runtime.stopped) return;

      const someCodeToRun = code.trim()
      if(someCodeToRun){

        const baseCtx = {
          code, section: 'code', isEnvSection: false,
          logConfig: {code, autoAssertExtraction: false, purgeTrace: runtime.purgeStackTrace},
        }

        // Do first the methods exclusions check, to gain some time (avoids loading modules if
        // the error would show up anyway afterward...)
        await runtime.runWithCtx({...baseCtx, method: this.throwIfExcludedMethodsFound})

        // Detect possible user imports and install the packages to allow their imports:
        await runtime.runWithCtx({...baseCtx, method: this.installAndImportMissingModules,
                                              methodArgs: [code, runtime]})
        if(runtime.stopped) return;

        baseCtx.logConfig.autoAssertExtraction = runtime.autoLogAssert
        await runtime.runWithCtx({...baseCtx, applyExclusionsIfAny: true, method: this.pythonCodeRunnerWithCtx})
      }
      this.testSectionEndFeedback(runtime, testsStep)
    }



    throwIfExcludedMethodsFound(ctx, runtime){
      const nope = runtime.excludedMethods.filter(methodCall=>ctx.code.includes(methodCall))
      if(nope.length){
        const plural = nope.length>1 ? "s":""
        const nopes = nope.map( s=>s.slice(1) ).join(', ')
        const msg = `${ CONFIG.MSG.exclusionMarker } method${plural}: ${ nopes }`
        throw new PythonError(msg)
      }
    }





  async teardownRuntime(runtime){
    jsLogger("[checkPoint] - PyodideSectionsRunner teardownRuntime")

    await runtime.runWithCtx('post')
    await this.handleMermaids(runtime)
    jsLogger("[checkPoint] - teardown pyodide cleaner")
    pyodideCleaner()
    runtime.cleanup()
  }



  async handleMermaids(runtime){
    jsLogger("[checkPoint] - teardown mermaid")
    if(CONFIG.needMermaid && !runtime.stopped){
      if(!globalThis.mermaid){
        this.giveFeedback('', 'Cannot convert to mermaid graph: mermaid is not available.\n'
                              +'Please contact the author of the exercice.', true)
      }
      try{
        await mermaid.run()
        // mermaid.run systematically throws an error, even on valid graphs...
        // Worse: If mermaid.run({suppressErrors:true}) is used, nothing is rendered at all...
        //        I love JS...
      }catch(e){}
    }
  }
}
