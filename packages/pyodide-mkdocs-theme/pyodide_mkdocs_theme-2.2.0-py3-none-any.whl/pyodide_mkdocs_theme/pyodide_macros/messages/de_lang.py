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


from .classes import (
    Tr,
    TestsToken,
    Msg,
    MsgPlural,
    Tip,
)
from .fr_lang import Lang


class LangDe(Lang):

    # LANG_TOKEN
    # Editors:
    tests:      Tr = TestsToken("\n# Tests\n")  ###
    """
    Separator placed between the user code and public tests.

    * Line breaks at the beginning or end indicate the number of empty lines before or after the text itself.
    * The separator itself must start with `#` and have at least 6 characters (excluding spaces).
    """###
    comments:   Tr = Tip(19, "(De-)Aktiviert den Code nach der Zeile <code>{tests}</code> "
                             "(Groß-/Kleinschreibung wird nicht beachtet)", "Ctrl+I")    ###
    """
    Tooltip for the button to enable or disable public tests.
    The string used must contain {tests} because the content of TestsToken.msg will be inserted there.
    """###


    # Terminals
    feedback:      Tr = Tip(19, "Kürzen/nicht kürzen der Rückmeldungen im Terminal (Standardausgabe & Stacktrace"
                                "/ Starte das Programm erneut zum Anwenden)")    ###
    """
    Tooltip for the button controlling the "feedback level" displayed in the terminal.
    """###
    wrap_term:     Tr = Tip(17, "Wenn aktiviert, wird der aus dem Terminal kopierte Text in eine Zeile umgewandelt, "
                                "bevor er in die Zwischenablage kopiert wird.")    ###
    """
    Tooltip for the button indicating whether the text copied from the terminal is joined before being copied or not.
    """###


    # Runtime feedback
    run_script:    Tr = Msg("Programm gestartet...")    ###
    """
    Message announcing the start of executions (pyodide).
    """###
    install_start: Tr = Msg("Installation von Python-Paketen. Dies kann eine Weile dauern...")    ###
    """
    Message displayed in the terminal before loading micropip, in order to install missing packages.
    """###
    install_done:  Tr = Msg("Installationen abgeschlossen!")    ###
    """
    Message displayed when micropip package installations are finished.
    """###

    validation:    Tr = Msg("Validierung - ")    ###
    """
    Name starting the lines of the feedback in the terminal, for the validation steps
    """###
    editor_code:   Tr = Msg("Editor")    ###
    """
    Name associated to the content of the editor
    """###
    public_tests:  Tr = Msg("Öffentliche tests")    ###
    """
    Name given to the original public tests (step 2 during validations)
    """###
    secret_tests:  Tr = Msg("Geheime tests")    ###
    """
    Name given to the secret tests (step 3 during validations)
    """###
    success_msg:   Tr = Msg("OK")    ###
    """
    Message when one step of the tests is successful.
    """###
    unforgettable: Tr = Msg("Vergiss nicht, den Code zu validieren!")    ###
    """
    Message displayed at the end of the public tests if no errors were encountered and secret tests exist.
    """###


    # Terminals: validation success/failure messages
    success_head:  Tr = Msg("Gut gemacht!")    ###
    """
    Header of the success message (bold, italic, green)
    """###
    success_tail:  Tr = Msg("Vergiss nicht das folgende zu lesen:")    ###
    """
    End of the success message.
    """###
    fail_head:     Tr = Msg("Schade!")    ###
    """
    Header of the failure message (bold, italic, orange)
    """###
    reveal_corr:   Tr = Msg("die lösung")    ###
    """
    Chunk of sentence indicating a solution code exists.
    """###
    reveal_join:   Tr = Msg("und")    ###
    """
    Coordinating conjunction joining `reveal_corr` and `reveal_rem` when correction and
    comments are present.
    """###
    reveal_rem:    Tr = Msg("die kommentare")    ###
    """
    Chunk of sentence indicating the existence of remarks.
    """###
    success_head_extra:  Tr = Msg("Du hast alle Tests bestanden!")    ###
    """
    End of the message indicating a success.
    """###
    fail_tail:     Tr = MsgPlural("ist jetzt verfügbar", "sind jetzt verfügbar") ###
    """
    End of the message indicating a failure.
    """###


    # Corr  rems admonition:
    title_corr: Tr = Msg('Lösung')    ###
    """
    Used to build the title of the admonition holding solution and/or comments, below IDEs.
    """###
    title_rem:  Tr = Msg('Bemerkungen')   ###
    """
    Used to build the title of the admonition holding solution and/or comments, below IDEs.
    """###
    corr:       Tr = Msg('🐍 Lösungsvorschlag')    ###
    """
    Title of the code block containing the solution for an IDE, in the "solution & comments"
    admonition.
    """###
    rem:        Tr = Msg('Bemerkungen')    ###
    """
    Title (&lt;h3&gt; equivalent) announcing the comments, in the "solution & comments" admonition.
    """###


    # Buttons, IDEs buttons & counter:
    py_btn:     Tr = Tip(9, "Code ausführen")    ###
    """
    Tooltip for a standalone button that allows running python code.
    """###
    play:       Tr = Tip(9,  "Code ausführen", "Ctrl+S")    ###
    """
    Tooltip for the button to run public tests.
    """###
    check:      Tr = Tip(9,  "Überprüfen", "Ctrl+Enter")    ###
    """
    Tooltip for the button to run validation tests.
    """###
    download:   Tr = Tip(0,  "Herunterladen")    ###
    """
    Tooltip for the button to download the content of a code editor.
    """###
    upload:     Tr = Tip(0,  "Hochladen")    ###
    """
    Tooltip for the button to replace the content of a code editor with the content of a local file.
    """###
    restart:    Tr = Tip(0,  "Editor zurücksetzen")    ###
    """
    Tooltip for the button resetting the content of a code editor.
    """###
    save:       Tr = Tip(9,  "Im Webbrowser speichern")    ###
    """
    Tooltip for the button to save the content of a code editor to the browser's localStorage.
    """###
    corr_btn:   Tr = Tip(10, "Lösung überprüfen (serve)")    ###
    """
    Tooltip for the button to test the solution code (`corr` section / only during mkdocs serve).
    """###
    show:       Tr = Tip(12, "Lösung und Bemerkungen anzeigen")    ###
    """
    Tooltip for the button to reveal the solution and the comments (only during mkdocs serve).
    """###
    attempts_left: Tr = Msg("Verbleibende Versuche")    ###
    """
    Texte indicating the number of remaining validation attempts.
    """###


    # QCMS
    qcm_title:     Tr = MsgPlural("Frage")    ###
    """
    Default title used for admonitions containing the MCQs (when no argument is provided with the
    `multi_qcm` macro call).
    """###
    qcm_mask_tip:  Tr = Tip(11, "Die Antworten bleiben versteckt...")    ###
    """
    Tooltip displayed on hover over the mask, for MCQs whose answers are not revealed.
    """###
    qcm_check_tip: Tr = Tip(11, "Antworten überprüfen")    ###
    """
    Tooltip for the button to validate MCQ answers.
    """###
    qcm_redo_tip:  Tr = Tip(11, "Neu anfangen")    ###
    """
    Tooltip for the button to restart the MCQ.
    """###


    # Others
    tip_trash: Tr = Tip(15, "Lösche die gespeicherten Codes im Webbrowser für {site_name}") ###
    """
    Tooltip for the button to delete the data stored in the browser's localStorage
    (the trash can at the top next to the search bar).
    The actual site name (`site_name` in `mkdocs.yml`) is automatically inserted into the
    sentence with "{site_name}".
    """###

    figure_admo_title: Tr = Msg("Deine Abbildung") ###
    """
    Title given to admonitions containing "figures" (see about drawings made with `matplotlib`
    and the `figure(...)` macro).
    """###
    figure_text: Tr = Msg("Deine Abbildung wird hier erscheinen") ###
    """
    Text placeholder for a `figure` (see about drawings made with `matplotlib` and the
    `figure(...)` macro).
    """###

    picker_failure: Tr = Msg(
        "Bitte klicke irgendwo auf der Seite zwischen der Verwendung von Tastenkombinationen oder "
        "klicke auf eine Schaltfläche, um eine Datei hochzuladen."
    ) ###
    """
    Message displayed in the browser when the user tries to run code using `pyodide_uploader_async`
    multiple times using keyboard shortcuts, without other interaction with the page in between
    attempts: this is not allowed by browsers.

    Note: browsers that do not support `HTMLInputElement.showPicker` will not display this message.
    """###


    # LANG_TOKEN
    #-------------------------------------------------------------------------
