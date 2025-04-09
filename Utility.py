import sqlite3

from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton, QDateEdit, QCalendarWidget, QMessageBox
from PyQt5.QtGui import QIcon

def convert_all_lineedits_to_uppercase(widget):
    from PyQt5.QtWidgets import QLineEdit
    for lineedit in widget.findChildren(QLineEdit):
        # Collega il segnale textChanged al callback
        lineedit.textChanged.connect(lambda text, le=lineedit: update_lineedit_uppercase(le, text))

def update_lineedit_uppercase(lineedit, text):
    # Se il testo non è già in maiuscolo, lo converte
    if text != text.upper():
        lineedit.blockSignals(True)
        lineedit.setText(text.upper())
        lineedit.blockSignals(False)

def get_sigla_provincia(comune, db_path="gestione_armi.db"):
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        comune = comune.upper()  # Assicurati che il comune sia in maiuscolo
        cursor.execute("SELECT UPPER([Sigla automobilistica]) FROM comuni WHERE UPPER([Denominazione in italiano]) = ?", (comune,))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]
        else:
            return ""
    except Exception as e:
        print("Errore in get_sigla_provincia:", e)
        return ""
    finally:
        conn.close()

def compute_codice_fiscale(nome, cognome, data_nascita, sesso, comune_nascita, db_path="gestione_armi.db"):
    """
    Calcola il codice fiscale completo (16 caratteri) in modo semplificato.

    - Per il cognome: estrae le prime tre consonanti (aggiungendo vocali e "X" se necessario).
    - Per il nome: se ha almeno 4 consonanti, usa la prima, la terza e la quarta; altrimenti come per il cognome.
    - Per la data di nascita (formato DD/MM/YYYY):
      * Prende gli ultimi due numeri dell'anno.
      * Per il mese usa il corrispondente codice lettera (A, B, C, ...).
      * Per il giorno, se il sesso è femminile, somma 40 al giorno.
    - Recupera il codice catastale del comune dal database (dal campo [Codice Catastale del comune]).
    - Calcola il carattere di controllo (check char) basandosi su tabelle di conversione per posizioni dispari e pari.

    Restituisce il codice fiscale completo (senza eventuali spazi) in maiuscolo.
    """

    def extract_letters(s, consonants=True):
        s = s.upper()
        if consonants:
            return "".join([c for c in s if c.isalpha() and c not in "AEIOU"])
        else:
            return "".join([c for c in s if c in "AEIOU"])

    # Calcola la parte del cognome
    cons = extract_letters(cognome, consonants=True)
    vowels = extract_letters(cognome, consonants=False)
    cognome_code = (cons + vowels + "XXX")[:3]

    # Calcola la parte del nome
    cons = extract_letters(nome, consonants=True)
    vowels = extract_letters(nome, consonants=False)
    if len(cons) >= 4:
        # Se il nome ha almeno 4 consonanti, usa la prima, la terza e la quarta
        nome_code = cons[0] + cons[2] + cons[3]
    else:
        nome_code = (cons + vowels + "XXX")[:3]

    # Estrai giorno, mese, anno dalla data (formato DD/MM/YYYY)
    try:
        day, month, year = data_nascita.split("/")
        year_code = year[-2:]
        day = int(day)
        month = int(month)
    except Exception as e:
        raise ValueError("Formato data_nascita non valido. Usa DD/MM/YYYY.") from e

    month_codes = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "H",
                   7: "L", 8: "M", 9: "P", 10: "R", 11: "S", 12: "T"}
    month_code = month_codes.get(month, "X")

    # Se il sesso è femminile, aggiunge 40 al giorno
    if sesso.upper() == "F":
        day += 40
    day_code = f"{day:02d}"

    # Recupera il codice catastale del comune di nascita
    codice_catastale = get_codice_catastale(comune_nascita, db_path=db_path)

    # Codice fiscale parziale (15 caratteri)
    cf_partial = (cognome_code + nome_code + year_code + month_code + day_code + codice_catastale).upper()
    check_char = compute_check_char(cf_partial)
    return cf_partial + check_char

def compute_check_char(cf_partial):
    """
    Calcola il carattere di controllo del codice fiscale.
    Utilizza due tabelle di conversione: una per i caratteri in posizione dispari e
    una per quelli in posizione pari.
    """
    odd_table = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    }
    even_table = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
        'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
    }
    total = 0
    for i, ch in enumerate(cf_partial):
        # Le posizioni si contano a partire da 1
        if (i + 1) % 2 == 1:  # posizione dispari
            total += odd_table.get(ch, 0)
        else:
            total += even_table.get(ch, 0)
    remainder = total % 26
    # Il carattere di controllo: 0 -> A, 1 -> B, ..., 25 -> Z
    return chr(remainder + ord('A'))

def get_codice_catastale(comune, db_path="gestione_armi.db"):
    """
    Recupera il "Codice Catastale del comune" dalla tabella comuni.
    Si assume che il campo si chiami [Codice Catastale del comune].
    """
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        comune = comune.upper()  # Assicurati che il comune sia in maiuscolo
        cursor.execute(
            "SELECT UPPER([Codice Catastale del comune]) FROM comuni WHERE UPPER([Denominazione in italiano]) = ?",
            (comune,))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]
        else:
            return ""
    except Exception as e:
        print("Errore in get_codice_catastale:", e)
        return ""
    finally:
        conn.close()



from PyQt5.QtWidgets import QLineEdit, QCalendarWidget, QToolButton, QHBoxLayout, QWidget
from PyQt5.QtCore import QDate, Qt, pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator


class DateInputWidget(QWidget):
    """
    Widget personalizzato per l'inserimento di date con formato guidato
    Mantiene sempre il formato __/__/____ e completa automaticamente
    """

    dateChanged = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout orizzontale per contenere i controlli
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Campo di testo per inserimento con maschera
        self.lineEdit = QLineEdit(self)
        self._placeholder = "__/__/____"
        self.lineEdit.setText(self._placeholder)

        # Regole di validazione per accettare solo numeri nelle posizioni corrette
        self._setupMaskedInput()

        # Pulsante calendario
        self.calendarButton = QToolButton(self)
        self.calendarButton.setText("📅")
        self.calendarButton.setCursor(Qt.PointingHandCursor)
        self.calendarButton.clicked.connect(self._showCalendar)

        # Widget calendario (inizialmente nascosto)
        self.calendar = QCalendarWidget(self)
        self.calendar.setWindowFlags(Qt.Popup)
        self.calendar.clicked.connect(self._setDateFromCalendar)
        self.calendar.hide()

        # Aggiunta dei widget al layout
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.calendarButton)

        # Formato di visualizzazione predefinito
        self._displayFormat = "dd/MM/yyyy"

        # Connessione dei segnali
        self.lineEdit.textEdited.connect(self._onTextEdited)

    def _setupMaskedInput(self):
        """Configura la maschera di input e gestori eventi per il formato guidato"""
        # Impostiamo il focus per attivare la gestione avanzata degli input
        self.lineEdit.setFocusPolicy(Qt.StrongFocus)

        # Colleghiamo i gestori di eventi chiave
        self.lineEdit.keyPressEvent = self._handleKeyPress

    def _handleKeyPress(self, event):
        """Gestisce la pressione dei tasti per mantenere il formato __/__/____"""
        key = event.key()
        text = self.lineEdit.text()
        cursor_pos = self.lineEdit.cursorPosition()

        # Gestione backspace - mantiene il formato
        if key == Qt.Key_Backspace:
            if cursor_pos > 0:
                if text[cursor_pos - 1] in '0123456789':
                    # Sostituisci il numero con un underscore
                    new_text = text[:cursor_pos - 1] + '_' + text[cursor_pos:]
                    self.lineEdit.setText(new_text)
                    self.lineEdit.setCursorPosition(cursor_pos - 1)
                elif cursor_pos > 1 and text[cursor_pos - 1] in '/' and text[cursor_pos - 2] in '0123456789':
                    # Se siamo su uno slash, torna indietro e cancella il numero
                    new_text = text[:cursor_pos - 2] + '_' + text[cursor_pos - 1:]
                    self.lineEdit.setText(new_text)
                    self.lineEdit.setCursorPosition(cursor_pos - 2)
            return

        # Gestione inserimento numeri
        if key >= Qt.Key_0 and key <= Qt.Key_9:
            digit = chr(key)

            # Trova la prossima posizione disponibile per un numero
            valid_positions = [0, 1, 3, 4, 6, 7, 8, 9]
            current_pos = cursor_pos

            # Se siamo su una posizione valida e c'è un underscore, sostituiscilo
            if current_pos in valid_positions and text[current_pos] == '_':
                new_text = text[:current_pos] + digit + text[current_pos + 1:]
                self.lineEdit.setText(new_text)

                # Se abbiamo inserito il primo o terzo numero, spostiamo automaticamente dopo lo slash
                if current_pos == 1 or current_pos == 4:
                    self.lineEdit.setCursorPosition(current_pos + 2)
                else:
                    self.lineEdit.setCursorPosition(current_pos + 1)

                # Controlla se la data è valida e segnala il cambiamento
                self._checkAndEmitDateChanged()
                return

            # Cerca la prossima posizione valida con un underscore
            for pos in valid_positions:
                if pos >= current_pos and text[pos] == '_':
                    new_text = text[:pos] + digit + text[pos + 1:]
                    self.lineEdit.setText(new_text)

                    # Se abbiamo inserito il primo o terzo numero, spostiamo automaticamente dopo lo slash
                    if pos == 1 or pos == 4:
                        self.lineEdit.setCursorPosition(pos + 2)
                    else:
                        self.lineEdit.setCursorPosition(pos + 1)

                    # Controlla se la data è valida e segnala il cambiamento
                    self._checkAndEmitDateChanged()
                    return

        # Per altri tasti, usa il comportamento di default
        QLineEdit.keyPressEvent(self.lineEdit, event)

    def _checkAndEmitDateChanged(self):
        """Controlla se la data attuale è valida e in caso emette il segnale dateChanged"""
        text = self.lineEdit.text().replace('_', '')
        if len(text) == 10:  # dd/MM/yyyy
            date = QDate.fromString(text, self._displayFormat)
            if date.isValid():
                self.dateChanged.emit(date)

    def _onTextEdited(self, text):
        """Gestisce i cambiamenti manuali del testo"""
        # Assicura che il formato __/__/____ sia sempre mantenuto
        if len(text) < 10 or '_' not in text:
            self.lineEdit.setText(self._placeholder)
            self.lineEdit.setCursorPosition(0)

    def _showCalendar(self):
        """Mostra il calendario popup sotto il widget"""
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.calendar.move(pos)

        # Se c'è già una data valida, imposta il calendario su quella data
        date = self.date()
        if date.isValid():
            self.calendar.setSelectedDate(date)

        self.calendar.show()

    def _setDateFromCalendar(self, date):
        """Imposta la data quando selezionata dal calendario"""
        self.setDate(date)
        self.calendar.hide()
        self.dateChanged.emit(date)

    def date(self):
        """Restituisce la data corrente"""
        text = self.lineEdit.text()
        # Ignora il formato se contiene underscore
        if '_' in text:
            # Controlla se ci sono abbastanza cifre per ottenere una data parziale
            cleaned_text = text.replace('_', '')
            if len(cleaned_text) < 8:  # Necessari almeno gg/mm/yyyy
                return QDate()

        date = QDate.fromString(text, self._displayFormat)
        if date.isValid():
            return date
        return QDate()

    def setDate(self, date):
        """Imposta la data"""
        if isinstance(date, QDate) and date.isValid():
            self.lineEdit.setText(date.toString(self._displayFormat))

    def text(self):
        """Restituisce il testo corrente"""
        text = self.lineEdit.text()
        # Ritorna una stringa vuota se il formato contiene ancora underscore
        if '_' in text:
            return ""
        return text

    def setDisplayFormat(self, format_string):
        """Imposta il formato di visualizzazione della data"""
        self._displayFormat = format_string
        # Aggiorna anche il formato placeholder se necessario
        if format_string == "dd/MM/yyyy":
            self._placeholder = "__/__/____"
        elif format_string == "yyyy-MM-dd":
            self._placeholder = "____-__-__"
        else:
            # Crea un placeholder appropriato basato sul formato
            self._placeholder = format_string.replace('d', '_').replace('M', '_').replace('y', '_')

        # Se non c'è una data valida, mostra il placeholder
        current_date = self.date()
        if not current_date.isValid():
            self.lineEdit.setText(self._placeholder)
        else:
            self.setDate(current_date)

    def displayFormat(self):
        """Restituisce il formato di visualizzazione corrente"""
        return self._displayFormat