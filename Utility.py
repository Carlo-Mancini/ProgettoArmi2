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

def cerca_arma_per_matricola(matricola, db_path="gestione_armi.db"):
    """
    Cerca l'arma nel database in base alla matricola.
    Restituisce l'ID_ArmaDetenuta se trovata, altrimenti None.
    """
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ID_ArmaDetenuta FROM armi WHERE Matricola = ?", (matricola.upper(),))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print("Errore in cerca_arma_per_matricola:", e)
        return None
    finally:
        conn.close()
