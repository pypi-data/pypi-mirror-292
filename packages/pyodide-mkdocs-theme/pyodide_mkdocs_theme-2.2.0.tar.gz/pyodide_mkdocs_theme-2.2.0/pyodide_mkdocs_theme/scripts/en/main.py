
from pyodide_mkdocs_theme.pyodide_macros import (
    PyodideMacrosPlugin,
    Msg, MsgPlural, TestsToken, Tip,
)


def define_env(env:PyodideMacrosPlugin):
    """ The customization has to be done at macro definition time.
        You could paste the code inside this function into your own main.py (or the
        equivalent package if you use a package instead of a single file). If you don't
        use personal macros so far, copy the full code into a `main.py` file at the root
        of your project (note: NOT in the docs_dir!).

        NOTE: you can also completely remove this file if you don't want to use personal
              macros or customize the messages in the built documentation.

        * Change whatever string you want.
        * Remove the entries you don't want to modify
        * Do not change the keyboard shortcuts for the Tip objects: the values are for
          informational purpose only.
        * See the documentation for more details about which string is used for what
          purpose, and any constraints on the arguments:
          https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/custom/messages/#messages-details

        ---

        The signatures for the various objects defined below are the following:

        ```python
        Msg(msg:str)

        MsgPlural(msg:str, plural:str="")

        Tip(width_in_em:int, msg:str, kbd:str=None)

        TestsToken(token_str:str)
        ```
    """

    env.lang.overload({

    # Editors:
        "tests":      TestsToken("\n# Tests\n"),
        "comments":   Tip(16, "(De-)Activate the code after the line <code>{tests}</code> "
                             "(case insensitive)", "Ctrl+I"),


    # Terminals
        "feedback":      Tip(19, "Truncate or not the feedback in the terminals (standard output "
                                "& stacktrace / run the code again to apply)"),
        "wrap_term":     Tip(18, "If enabled, text copied from the terminal is joined into a single "
                                "line before being copied to the clipboard"),


    # Runtime feedback
        "run_script":    Msg("Script started..."),
        "install_start": Msg("Installing Python packages. This may take some time..."),
        "install_done":  Msg("Installations completed!"),

        "validation":    Msg("Validation - "),
        "editor_code":   Msg("Editor"),
        "public_tests":  Msg("Public tests"),
        "secret_tests":  Msg("Secret tests"),
        "success_msg":   Msg("OK"),
        "unforgettable": Msg("Don't forget to validate the code!"),


    # Terminals: validation success/failure messages
        "success_head":  Msg("Bravo !"),
        "success_tail":  Msg("Don't forget to read"),
        "fail_head":     Msg("Oops!"),
        "reveal_corr":   Msg("the solution"),
        "reveal_join":   Msg("and"),
        "reveal_rem":    Msg("comments"),
        "success_head_extra":  Msg("You have passed all the tests!"),
        "fail_tail":     MsgPlural("is now available", "are now available"),


    # Corr  rems admonition:
        "title_corr": Msg('Solution'),
        "title_rem":  Msg('Comments'),
        "corr":       Msg('🐍 Suggested solution'),
        "rem":        Msg('Comments'),


    # Buttons, IDEs buttons & counter:
        "py_btn":        Tip(8,  "Run the code"),
        "play":          Tip(9,  "Run the code", "Ctrl+S"),
        "check":         Tip(9,  "Validate", "Ctrl+Enter"),
        "download":      Tip(0,  "Download"),
        "upload":        Tip(0,  "Upload"),
        "restart":       Tip(6,  "Reset the editor"),
        "save":          Tip(7,  "Save in the browser"),
        "corr_btn":      Tip(9,  "Test the solution (serve)"),
        "show":          Tip(10, "Show corr & REMs"),
        "attempts_left": Msg("Attempts left"),


    # QCMS
        "qcm_title":     MsgPlural("Question"),
        "qcm_mask_tip":  Tip(13, "Answers will stay hidden..."),
        "qcm_check_tip": Tip(8,  "Check answers"),
        "qcm_redo_tip":  Tip(8,  "Restart"),


    # Others
        "tip_trash": Tip(15, "Remove the saved codes for {site_name} from the browser"),

        "figure_admo_title": Msg("Your figure"),
        "figure_text":       Msg("Your figure will appear here"),

        "picker_failure":    Msg(
            "Please, click somewhere on the page in between keyboard shortcuts or use a "
            "button to be able to upload a file."
        )
    })
