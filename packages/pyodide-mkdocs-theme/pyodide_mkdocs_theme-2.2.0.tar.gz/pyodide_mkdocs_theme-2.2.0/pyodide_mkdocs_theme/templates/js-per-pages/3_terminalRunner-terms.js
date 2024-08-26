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




class _TerminalHandler extends PyodideSectionsRunner {

  constructor(id){
    super(id)
    this.terminal    = null
    this.topDiv      = null
    this.termEnabled = false
    this.isIsolated  = id.startsWith("term_only")
    this.cmdChunk        = ""
    this.cmdOnTheRun     = ""
  }


  /**Build a jQuery terminal and bind it to the underlying pyodide runtime.
   *
   * WARNING:  If this is an IdeEditorHandler, this.id is the id of the editor div, not
   *           the id of the terminal div ! (hence the use of the termId argument)
   * */
  build(termId=null){
    if(!termId) termId = this.id
    const jqTermId = '#' + termId

    jsLogger("[Terminal] - build " + jqTermId)

    const commandsCbk = this.getAsyncPythonExecutor()
    const termOptions = {
      greetings: "",                    // cancel terminal banner (welcome message),
      completionEscape: false,
      prompt: CONFIG.MSG.promptStart,
      outputLimit: this.stdoutCutOff,
      enabled: false,                   // GET RID OF THE DAMN AUTO-SCROLL!!!!!!
      // wrap: getWrapTerms(),          // Also deactivate colors... FUCK THIS!
      keymap: this.getTerminalBindings(),
      completion: function (command, callback) {
        callback(pyFuncs.pyconsole.complete(command).toJs()[0]);    // autocompletion
      },
      onBlur: function(){}, // Allow to leave the textarea, focus-wise.
                            // DO NOT PUT ANY CODE INSIDE THIS !!
    }

    this.terminal = $(jqTermId).terminal(commandsCbk, termOptions)
    this.topDiv   = this.terminal.closest(".py_mk_wrapper")

    if(CONFIG._devMode) CONFIG.terms[termId]=this.terminal

    // Since terminal are created deactivated, add an EventListener for click to reactivate
    // them (once only: unsubscribe the listener on click. Note: no original click event)
    // Using the async lock so that the user cannot resume a terminal while it's running
    // (could occur on first click/run).
    this.addEventToRunOnce(this.terminal, 'click',  _=>{
      if(this.termEnabled) return;
      this.terminal.focus(true).enable()
      this.termEnabled = true
    }, true)
    this.prefillTermIfAny()

    /* Try to fix:
        - The "terminal with 0px with in tabbed IDEs/terminals":
        - The FILL content lost when the user changed of tab somewhere in the page...
    */
    const wrapper = this.terminal.parent()
    wrapper.on('click', _=>{
      const w = wrapper.css('width'), h = wrapper.css('height')
      if(w != this.terminal.css('width') || h != this.terminal.css('height')){
        this.terminal.css('width', w)
        this.terminal.css('height', h)
      }

      if(this.isIsolated && !this.terminal.get_command()){
        this.prefillTermIfAny()
      }
    })

    super.build()   // nothing done so far, but for consistency...
  }




  handleTerminalWidthTroubles(){
    const wWrapper = this.topDiv.width()
    if(wWrapper != this.terminal.width()){
      this.terminal.width(wWrapper)
    }
  }

  addEventToRunOnce(target, event, cbk, withLock=false){
    let clickHandler = async _=>{
      target.off(event, clickHandler)
      cbk()
    }
    if(withLock){
      clickHandler = withPyodideAsyncLock('term_'+event, clickHandler)
    }
    target.on('click', clickHandler)
  }



  /**Hook returning the configuration for terminal keyboard shortcuts bindings.
   * To override in child classes when needed.
   *
   * Handled here: transfer KeyInterrupt from DOM to python runtime (note: actually
   * useless as long as no worker used!).
   * */
  getTerminalBindings(){
    return ({
      "CTRL+C": async (e) => {
        let txt = getSelectionText()

        // Skip if some text is selected (=copy!)
        if (!txt) {
          let currentCmd = this.terminal.get_command();
          pyFuncs.clear_console();    // Looks like it does nothing...? :/
          this.terminal.echo(CONFIG.MSG.promptStart + currentCmd);
          this.terminal.echo(error("KeyboardInterrupt"));
          this.terminal.set_command("");
          this.terminal.set_prompt(CONFIG.MSG.promptStart);
          return
        }
        e.preventDefault()
        e.stopPropagation()
        if(CONFIG.joinTerminalLines){
          txt = txt.replace(/\n/g, '')
        }
        await navigator.clipboard.writeText(txt)
      }
    })
  }

  getAsyncPythonExecutor(){
    throw new Error('Should be overridden in the child class.')
  }


  prefillTermIfAny(){
    if(this.prefillTerm) this.terminal.set_command(this.prefillTerm)
  }


  /**When a terminal is available, display stdout and errors in it, if any.
   * */
  giveFeedback(stdout, stdErr="", _){
    if(stdErr){
      stdErr = error(stdErr)
    }else if(stdout.endsWith('\n')){
      stdout = stdout.slice(0,-1)       // useful when printing from terminal and no error
    }
    const msg = stdout + stdErr
    if(msg) this.terminal.echo(msg)
  }


  /**Has to be on the TerminalHandler, because TerminalRunner will call this through super call,
   * to avoid a command run in the terminal of an IDE calls the IdeRunner.teardownRuntime method.
   * */
  async teardownRuntime(runtime) {
    jsLogger("[checkPoint] - TerminalRunner teardownRuntime")
    this.terminal.resume()
    this.storeUserCodeInPython('__USER_CMD__', "")
    await super.teardownRuntime(runtime)
  }
}












class TerminalRunner extends _TerminalHandler {


  /**Generate the async-locked callback used to run commands typed into the terminal.
   *
   * WARNING: USE OF `super.method` in setupRuntimeTerminalCmd and teardownRuntimeTerminalCmd
   *
   * Using super calls, because one only wants the setup specific to terminal here, while "this"
   * could be an IdeRunner object. Ine that case, this.setupRuntime would run the setup for the
   * code in the editor, and not the command typed in the terminal.
   * This also way work with TerminalRunners, because the generic setupRuntime is _NOT_ on the
   * TerminalRunner class, but actually on the PythonSectionRunner one.
   * */
  getAsyncPythonExecutor(){
    return this.lockedRunnerWithBigFailWarningFactory(
      CONFIG.running.cmd,
      this.setupRuntimeTerminalCmd,
      this.runTermCommand,
      this.teardownRuntimeTerminalCmd,
    )
  }


  /**Definitions of `command`, `cmdOnThRun` and general context about `PyodideConsole`:
   * ----------------------------------------------------------------------------------
   *
   *
   * All those properties, but especially `cmdChunk`, are trickier than they seem.
   * This is essentially because the hidden/inner PyodideConsole is actually running totally
   * independently of the jQuery.terminal object itself.
   *
   * 1. Concretely, the PyodideConsole is handling the code itself without troubles, but anything
   * other than "just run that code" (aka, installations/imports, exclusions, ...) still has to
   * be done around the console.
   *
   * Problems arise when  you need to know on JS/Theme side if the cmdChunk is complete or not,
   * and to do so, you need to send the current @cmdChunk to the PyodideConsole, and that little
   * fucker wile automatically schedule the async execution of any complete cmdChunk as soon as
   * you call `pyconsole.push(chunk)` before you can even know it is complete on JS/Theme side.
   *
   *
   * On top of this, what is a cmdChunk, brain-wise, might sometimes be quite different of what
   * a terminal might actually be sending here as argument:
   *
   * @cmdChunk: This is the string content in the terminal that is passed through _WHEN THE USER
   *           HITS `Enter` (without holding Shift key). This implies commands could concretely
   *           be a lot of different things:
   *                - A single line command, just like you'd expect:
   *                      `a = 45+6`
   *                - A multiline command, potentially with several "commands" in it (two, here):
   *                      ```
   *                      globs = {}
   *                      def func(k):
   *                          return globs.get(k, 42)
   *                      ```
   *                - The CONTINUATION of a multiline command started earlier (here it gets messy):
   *                      Previously:   `>>> """ Starting the multi thing`
   *                      Previously:   `... continue it`
   *                      Now:          `... third line`
   *
   *                      After hitting `Enter`, @cmdChunk will be `"third line"` ONLY.
   *                - Any mix of all these (that last 2, I mean).
   *
   *
   * Now, _IF_ the exclusions are already in place before the PyodideConsole execute the complete
   * command, builtins or imports exclusions are already handled because the console uses the
   * global scope.
   *
   * BUT, methods exclusions have to be checked, and missing packages might need to be installed.
   *
   * Considering the UX, it seems highly questionnable to drop exclusions related errors right in
   * the middle of an incomplete command. Even worse: to start installing a package right in the
   * middle of a multiline command... :roll-eyes:
   *
   *
   * Summarizing:
   *
   * 1. Exclusions (builtins & imports), if any, have to be put in place before the current
   *    `cmdChunk` is passed to the PyodideConsole, even if the current "command" is not complete.
   *
   * 2. Methods exclusions and missing packages installation has to be done only when the "current
   *    command" is complete, so the TerminalRunner must keep track of previously entered cmdChunks
   *    and track properly when it is "fully complete", syntax error, ...
   *    This is where `cmdOnTheRun` enters the game.
   *
   *        --------------------------------------------------------------------------------------
   *        TODO: the implementation about imports actually do not match this description... => ??
   *        --------------------------------------------------------------------------------------
   *
   * 3. When the `PyodideConsole` announce a complete command:
   *      - It's execution in pyodide is already scheduled, but the result stills need to be run
   *        with an async call.
   *      - Before that, excluded methods and missing packages have to be handled, so pass the
   *        `cmdOnTheRun` content to `runPythonCodeWithOptionsIfNoStdErr`, replacing the code
   *        executor method with an async callback that will actually just  await the result
   *        from the internal `PyodideConsole`.
   *
   *
   * IMPLICATIONS:
   *
   * Because of all this, a lot of operations have to be applied each time the user strikes `Enter`
   * in the terminal, even if the command is not complete yet (since, you cannot know upfront...).
   * This is the reason for env_term and post_term executions, for example.
   *
   * */
  async setupRuntimeTerminalCmd(cmdChunk){
    /* !!! WARNING !!!

        Any ASYNC potential calls to setupRuntime HAVE to be done before the pyconsole.push,
        otherwise, because of async loop scheduling, the environment is setup from JS AFTER
        the user command has been run indie pyodide...
        Because of this, need the commandBuffer to update the __USER_CMD__ variable, and
        _also_ because of this, the env section will also run on incomplete commands, and
        _also_ because of this, any import done through the console must be checked now...
    */
    this.cmdChunk     = cmdChunk
    this.cmdOnTheRun += this.cmdOnTheRun ? '\n'+cmdChunk : cmdChunk
    this.storeUserCodeInPython('__USER_CMD__', this.cmdOnTheRun)
    this.terminal.pause()

    // If an IDE-terminal is run before the IDE itself, it must run the env/post sections.
    // If env already run before, envTerm HAS to run independently, so remove the dependency.
    let runtime
    if(!this.alreadyRanEnv){
      runtime = await super.setupRuntime()
      // Using super, because a command ran in the terminal of an IDE MUST NOT run the setupRuntime
      // logic of the IDE but only the one related to the PyodideSectionsRunner logic.
      // This works because there is an intermediate parent class between the TerminalRunner one
      // and the PyodideSectionsRunner setupRuntime method.

    }else{
      runtime = this.buildRunConfig()
      runtime.changeDependency('envTerm', 'start')  // Make envTerm runnable on its own!
    }

    await runtime.runWithCtx('envTerm')
    return runtime
  }



  async teardownRuntimeTerminalCmd(runtime){
    try{
      await runtime.runWithCtx('postTerm')
    }finally{
      // If ever postTerm failed, post might still have to run:
      super.teardownRuntime(runtime)
    }
  }



  async runTermCommand(runtime){
    jsLogger("[checkPoint] - Terminal - start running command")

    if(runtime.stopped){
      jsLogger("[checkPoint] - Terminal - Skipped!")
      return
    }

    // Must be done BEFORE creating the future, otherwise, async scheduling troubles, and the
    // exclusions end up being applied AFTER the user's command has been run...
    await runtime.runWithCtx({
      code:          this.cmdChunk,
      section:      'cmd',
      isEnvSection:  false,
      logConfig:    {code:this.cmdChunk, autoAssertExtraction: false, purgeTrace: runtime.purgeStackTrace},
      method:        this.installAndImportMissingModules,
      methodArgs:   [this.cmdOnTheRun, runtime],
    })
    if(runtime.stopped){
      this.cmdOnTheRun = ""
      return
    }

    const done = async (future)=>{
      jsLogger("[checkPoint] - Terminal - done step. Awaited:", futureAwaited)
      this.cmdOnTheRun = ""
      if(!futureAwaited){
        try{ await future }catch(e){
          // console.warn(e)    // Might fail but result is useless => sink.
        }
      }
      future.destroy()    // to destroy only if it got awaited first
      await sleep()       // Enforce GUI update, going through the next tick
    }

    let futureAwaited

    // Multiline commands should be split (useful when pasting)
    for (let line of this.cmdChunk.split("\n")) {

      let [future] = [pyFuncs.pyconsole.push(line)]
      /* NOTE: putting those inside the array slightly changes the behaviors about
         "PyodideConsole future exception was never retrieved" stuff... => might be better.

         BUT... this doesn't resolve the troubles about async scheduling in any way (I checked),
         so the overall "mostly broken" setup must be kept...
      */

      futureAwaited = false

      // set the beginning of the next line in the terminal:
      const isIncompleteExpr = future.syntax_check=="incomplete"
      const headLine = isIncompleteExpr ? CONFIG.MSG.promptWait : CONFIG.MSG.promptStart
      this.terminal.set_prompt(headLine)

      jsLogger("[checkPoint] - Terminal - current cmd line:", line)

      switch (future.syntax_check) {
        case "complete":
          jsLogger("[checkPoint] - Terminal - future complete")

          const oldRunner = this.pythonCodeRunnerWithCtx
          try{
            /*NOTE: nothing can be awaited in between the future "creation" and the execution of
              runtime.runCodeAsync, otherwise the event loop will actually compute the result of
              the python command (which is now stored in the event loop) before the restrictions
              are put in place in the environment (everything is synch up to this point!).
            */
              this.pythonCodeRunnerWithCtx = async _=>{
              jsLogger("[checkPoint] - Terminal - awaiting future")
              futureAwaited = true
              await pyFuncs.await_fut(future)
            }
            await this.runPythonCodeWithOptionsIfNoStdErr(this.cmdOnTheRun, runtime)
              // NOTE: the code argument has actually no other use than to check against exclusions
              //      (imports are checked again, but with no result, since already done if needed)

          }finally{
            this.pythonCodeRunnerWithCtx = oldRunner
            await done(future)
          }
          continue

        case "incomplete":
          jsLogger("[checkPoint] - Terminal - future incomplete")
          continue

        case "syntax-error":
          jsLogger("[checkPoint] - Terminal - future syntax error")
          this.terminal.error(future.formatted_error.trimEnd());
          await done(future)
          return

        default:
          await done(future)
          throw new Error(`Unexpected state ${future.syntax_check}`);
      }
    }
  }
}







// SANITY CHECK:
;(function(){
  const somethingWrong = 'setupRuntime teardownRuntime'
                              .split(' ').some(k=>TerminalRunner.prototype.hasOwnProperty(k))
  if(somethingWrong){
    throw new Error(
      "The TerminalRunner class should define neither setupRuntime nor teardownRuntime methods: "
     +"they should be on the parent class (TerminalHandler / see comments about the user of super "
     +"in getAsyncPythonExecutor)"
    )
  }
})()
