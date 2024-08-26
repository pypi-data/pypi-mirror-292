
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
        "comments":   Tip(19, "(De-)Aktiviert den Code nach der Zeile <code>{tests}</code> "
                             "(Groß-/Kleinschreibung wird nicht beachtet)", "Ctrl+I"),


    # Terminals
        "feedback":      Tip(19, "Kürzen/nicht kürzen der Rückmeldungen im Terminal (Standardausgabe & Stacktrace"
                                "/ Starte das Programm erneut zum Anwenden)"),
        "wrap_term":     Tip(17, "Wenn aktiviert, wird der aus dem Terminal kopierte Text in eine Zeile umgewandelt, "
                                "bevor er in die Zwischenablage kopiert wird."),


    # Runtime feedback
        "run_script":    Msg("Programm gestartet..."),
        "install_start": Msg("Installation von Python-Paketen. Dies kann eine Weile dauern..."),
        "install_done":  Msg("Installationen abgeschlossen!"),

        "validation":    Msg("Validierung - "),
        "editor_code":   Msg("Editor"),
        "public_tests":  Msg("Öffentliche tests"),
        "secret_tests":  Msg("Geheime tests"),
        "success_msg":   Msg("OK"),
        "unforgettable": Msg("Vergiss nicht, den Code zu validieren!"),


    # Terminals: validation success/failure messages
        "success_head":  Msg("Gut gemacht!"),
        "success_tail":  Msg("Vergiss nicht das folgende zu lesen:"),
        "fail_head":     Msg("Schade!"),
        "reveal_corr":   Msg("die lösung"),
        "reveal_join":   Msg("und"),
        "reveal_rem":    Msg("die kommentare"),
        "success_head_extra":  Msg("Du hast alle Tests bestanden!"),
        "fail_tail":     MsgPlural("ist jetzt verfügbar", "sind jetzt verfügbar"),


    # Corr  rems admonition:
        "title_corr": Msg('Lösung'),
        "title_rem":  Msg('Bemerkungen'),
        "corr":       Msg('🐍 Lösungsvorschlag'),
        "rem":        Msg('Bemerkungen'),


    # Buttons, IDEs buttons & counter:
        "py_btn":     Tip(9, "Code ausführen"),
        "play":       Tip(9,  "Code ausführen", "Ctrl+S"),
        "check":      Tip(9,  "Überprüfen", "Ctrl+Enter"),
        "download":   Tip(0,  "Herunterladen"),
        "upload":     Tip(0,  "Hochladen"),
        "restart":    Tip(0,  "Editor zurücksetzen"),
        "save":       Tip(9,  "Im Webbrowser speichern"),
        "corr_btn":   Tip(10, "Lösung überprüfen (serve)"),
        "show":       Tip(12, "Lösung und Bemerkungen anzeigen"),
        "attempts_left": Msg("Verbleibende Versuche"),


    # QCMS
        "qcm_title":     MsgPlural("Frage"),
        "qcm_mask_tip":  Tip(11, "Die Antworten bleiben versteckt..."),
        "qcm_check_tip": Tip(11, "Antworten überprüfen"),
        "qcm_redo_tip":  Tip(11, "Neu anfangen"),


    # Others
        "tip_trash": Tip(15, "Lösche die gespeicherten Codes im Webbrowser für {site_name}"),

        "figure_admo_title": Msg("Deine Abbildung"),
        "figure_text": Msg("Deine Abbildung wird hier erscheinen"),

        "picker_failure": Msg(
        "Bitte klicke irgendwo auf der Seite zwischen der Verwendung von Tastenkombinationen oder "
        "klicke auf eine Schaltfläche, um eine Datei hochzuladen."
    )
    })
