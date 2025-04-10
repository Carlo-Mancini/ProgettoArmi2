import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QLabel, QPushButton, QComboBox, QMessageBox, QDateEdit,
    QGroupBox, QGridLayout, QCheckBox, QRadioButton, QButtonGroup,
    QStackedWidget, QCompleter, QWidget
)
from PyQt5.QtCore import QDate, QDateTime, Qt, QSortFilterProxyModel, QStringListModel
from Utility import convert_all_lineedits_to_uppercase


class TransferimentoDialog(QDialog):
    def __init__(self, arma_id, cedente_id, current_detentore, parent=None):
        super().__init__(parent)
        self.arma_id = arma_id
        self.cedente_id = cedente_id
        self.current_detentore = current_detentore
        self.arma_data = {}
        self.current_detentore_data = {}
        self.detentori_map = {}  # Mappa ID -> display name
        self.detentori_data = {}  # Mappa ID -> detentore data

        self.setWindowTitle("Trasferimento Arma")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        # Carica i dati necessari
        self.load_arma_data()
        self.load_current_detentore_data()

        # Crea e configura l'interfaccia
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
        self._load_detentori()

    def load_arma_data(self):
        """Carica i dati dell'arma dal database"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Prima verifica che la colonna esista
            cursor.execute("PRAGMA table_info(armi)")
            columns = [column[1] for column in cursor.fetchall()]

            # Costruisci la query dinamicamente in base alle colonne esistenti
            query = "SELECT "
            fields = []

            if "TipoArma" in columns:
                fields.append("TipoArma")
            if "MarcaArma" in columns:
                fields.append("MarcaArma")
            if "ModelloArma" in columns:
                fields.append("ModelloArma")
            if "Matricola" in columns:
                fields.append("Matricola")
            if "CalibroArma" in columns:
                fields.append("CalibroArma")

            # Se non ci sono campi, usa un campo fittizio
            if not fields:
                query += "1"
            else:
                query += ", ".join(fields)

            query += " FROM armi WHERE ID_ArmaDetenuta = ?"

            cursor.execute(query, (self.arma_id,))

            result = cursor.fetchone()
            if result:
                self.arma_data = {}

                for i, field in enumerate(fields):
                    self.arma_data[field] = result[i] if result[i] else ''
            else:
                print(f"Nessun dato trovato per l'arma con ID {self.arma_id}")
        except Exception as e:
            print(f"Errore nel caricamento dei dati dell'arma: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def load_current_detentore_data(self):
        """Carica i dati del detentore attuale"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Prima ottieni la struttura della tabella detentori
            cursor.execute("PRAGMA table_info(detentori)")
            columns = [column[1] for column in cursor.fetchall()]

            # Mappa i campi che ci servono ai nomi delle colonne reali
            fields_mapping = {
                'Cognome': ['Cognome'],
                'Nome': ['Nome'],
                'CodiceFiscale': ['CodiceFiscale', 'CodFiscale', 'CF'],
                'DataNascita': ['DataNascita', 'DataDiNascita'],
                'LuogoNascita': ['LuogoNascita', 'LuogoDiNascita'],
                'SiglaProvinciaNascita': ['SiglaProvinciaNascita', 'ProvinciaNascita'],
                'ComuneResidenza': ['ComuneResidenza', 'Comune'],
                'SiglaProvinciaResidenza': ['SiglaProvinciaResidenza', 'ProvinciaResidenza', 'Provincia'],
                'TipoViaResidenza': ['TipoViaResidenza', 'TipoVia'],
                'IndirizzoResidenza': ['IndirizzoResidenza', 'Indirizzo', 'Via'],
                'CivicoResidenza': ['CivicoResidenza', 'Civico', 'NumeroCivico'],
                'Telefono': ['Telefono', 'Tel', 'Cellulare']
            }

            # Costruisci la query con le colonne che esistono realmente
            query = "SELECT "
            fields = []
            field_names = []

            for field, possible_columns in fields_mapping.items():
                found = False
                for col in possible_columns:
                    if col in columns:
                        fields.append(col)
                        field_names.append(field)
                        found = True
                        break

                if not found:
                    print(f"Attenzione: nessuna colonna trovata per '{field}'")

            # Se non ci sono campi, usa un campo fittizio
            if not fields:
                query += "1"
            else:
                query += ", ".join(fields)

            query += " FROM detentori WHERE ID_Detentore = ?"

            cursor.execute(query, (self.current_detentore,))

            result = cursor.fetchone()
            if result:
                self.current_detentore_data = {}

                for i, field in enumerate(field_names):
                    self.current_detentore_data[field] = result[i] if result[i] else ''
            else:
                print(f"Nessun dato trovato per il detentore con ID {self.current_detentore}")
        except Exception as e:
            print(f"Errore nel caricamento dei dati del detentore: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def _create_widgets(self):
        """Crea i widget per il trasferimento"""
        # Data trasferimento
        self.dataTransferimentoEdit = QDateEdit()
        self.dataTransferimentoEdit.setCalendarPopup(True)
        self.dataTransferimentoEdit.setDate(QDate.currentDate())

        # Gruppo opzioni tipo destinatario
        self.destinatarioGroup = QButtonGroup(self)
        self.rbDetentoreDB = QRadioButton("Detentore nel database")
        self.rbDetentoreEsterno = QRadioButton("Detentore esterno")
        self.destinatarioGroup.addButton(self.rbDetentoreDB)
        self.destinatarioGroup.addButton(self.rbDetentoreEsterno)
        self.rbDetentoreDB.setChecked(True)

        # Stack widget per le diverse opzioni
        self.stackedWidget = QStackedWidget()

        # --- Pagina 1: Detentore dal DB ---
        self.pageDetentoreDB = QWidget()
        layout_db = QVBoxLayout(self.pageDetentoreDB)

        # Campo di ricerca
        self.searchLabel = QLabel("Cerca:")
        self.searchEdit = QLineEdit()
        self.searchEdit.setPlaceholderText("Ricerca per cognome, nome o codice fiscale...")

        # Combobox detentori
        self.detentoriCombo = QComboBox()
        self.detentoriCombo.setMinimumWidth(350)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.searchLabel)
        search_layout.addWidget(self.searchEdit)

        layout_db.addLayout(search_layout)
        layout_db.addWidget(self.detentoriCombo)

        # --- Pagina 2: Detentore Esterno ---
        self.pageDetentoreEsterno = QWidget()
        layout_esterno = QFormLayout(self.pageDetentoreEsterno)

        self.cognomeEsternoEdit = QLineEdit()
        self.nomeEsternoEdit = QLineEdit()
        self.cfEsternoEdit = QLineEdit()
        self.dataNascitaEsternoEdit = QDateEdit()
        self.dataNascitaEsternoEdit.setCalendarPopup(True)
        self.dataNascitaEsternoEdit.setDate(QDate(1970, 1, 1))
        self.luogoNascitaEsternoEdit = QLineEdit()
        self.comuneResidenzaEsternoEdit = QLineEdit()
        self.provinciaEsternoEdit = QLineEdit()
        self.indirizzoEsternoEdit = QLineEdit()
        self.telefonoEsternoEdit = QLineEdit()

        layout_esterno.addRow("Cognome:", self.cognomeEsternoEdit)
        layout_esterno.addRow("Nome:", self.nomeEsternoEdit)
        layout_esterno.addRow("Codice Fiscale:", self.cfEsternoEdit)
        layout_esterno.addRow("Data Nascita:", self.dataNascitaEsternoEdit)
        layout_esterno.addRow("Luogo Nascita:", self.luogoNascitaEsternoEdit)
        layout_esterno.addRow("Comune Residenza:", self.comuneResidenzaEsternoEdit)
        layout_esterno.addRow("Provincia:", self.provinciaEsternoEdit)
        layout_esterno.addRow("Indirizzo:", self.indirizzoEsternoEdit)
        layout_esterno.addRow("Telefono:", self.telefonoEsternoEdit)

        # Aggiunge le pagine allo stack
        self.stackedWidget.addWidget(self.pageDetentoreDB)
        self.stackedWidget.addWidget(self.pageDetentoreEsterno)

        # Motivazione trasferimento
        self.motivoCombo = QComboBox()
        self.motivoCombo.addItems([
            "VENDITA", "DONAZIONE", "EREDITÀ", "COMODATO D'USO",
            "RESO", "RIPARAZIONE", "ALIENAZIONE", "ALTRO"
        ])

        # Note
        self.noteEdit = QLineEdit()

        # Pulsanti
        self.saveButton = QPushButton("Esegui Trasferimento")
        self.cancelButton = QPushButton("Annulla")

    def _setup_layout(self):
        """Configura il layout"""
        main_layout = QVBoxLayout()

        # Gruppo informazioni arma
        arma_group = QGroupBox("Informazioni Arma")
        arma_layout = QGridLayout()
        arma_layout.addWidget(QLabel("Tipo:"), 0, 0)
        arma_layout.addWidget(QLabel(self.arma_data.get('TipoArma', '')), 0, 1)
        arma_layout.addWidget(QLabel("Marca:"), 0, 2)
        arma_layout.addWidget(QLabel(self.arma_data.get('MarcaArma', '')), 0, 3)
        arma_layout.addWidget(QLabel("Modello:"), 1, 0)
        arma_layout.addWidget(QLabel(self.arma_data.get('ModelloArma', '')), 1, 1)
        arma_layout.addWidget(QLabel("Matricola:"), 1, 2)
        arma_layout.addWidget(QLabel(self.arma_data.get('Matricola', '')), 1, 3)
        arma_layout.addWidget(QLabel("Calibro:"), 2, 0)
        arma_layout.addWidget(QLabel(self.arma_data.get('CalibroArma', '')), 2, 1)
        arma_group.setLayout(arma_layout)
        main_layout.addWidget(arma_group)

        # Gruppo detentore attuale
        detentore_group = QGroupBox("Detentore Attuale (Cedente)")
        detentore_layout = QGridLayout()
        detentore_layout.addWidget(QLabel("Cognome:"), 0, 0)
        detentore_layout.addWidget(QLabel(self.current_detentore_data.get('Cognome', '')), 0, 1)
        detentore_layout.addWidget(QLabel("Nome:"), 0, 2)
        detentore_layout.addWidget(QLabel(self.current_detentore_data.get('Nome', '')), 0, 3)
        detentore_layout.addWidget(QLabel("Cod. Fiscale:"), 1, 0)
        detentore_layout.addWidget(QLabel(self.current_detentore_data.get('CodiceFiscale', '')), 1, 1)
        detentore_layout.addWidget(QLabel("Telefono:"), 1, 2)
        detentore_layout.addWidget(QLabel(self.current_detentore_data.get('Telefono', '')), 1, 3)
        detentore_group.setLayout(detentore_layout)
        main_layout.addWidget(detentore_group)

        # Gruppo trasferimento
        transfer_group = QGroupBox("Dati Trasferimento")
        transfer_layout = QFormLayout()

        # Data trasferimento
        transfer_layout.addRow("Data Trasferimento:", self.dataTransferimentoEdit)

        # RadioButton per il tipo di destinatario
        rb_layout = QHBoxLayout()
        rb_layout.addWidget(self.rbDetentoreDB)
        rb_layout.addWidget(self.rbDetentoreEsterno)
        transfer_layout.addRow("Tipo Destinatario:", rb_layout)

        # Widget per selezione detentore/inserimento dati
        transfer_layout.addRow(self.stackedWidget)

        # Motivo e dettagli
        transfer_layout.addRow("Motivo Trasferimento:", self.motivoCombo)

        # Note
        transfer_layout.addRow("Note:", self.noteEdit)

        transfer_group.setLayout(transfer_layout)
        main_layout.addWidget(transfer_group)

        # Informazioni aggiuntive
        info_label = QLabel("Il trasferimento registrerà l'arma come appartenente al nuovo detentore selezionato. "
                            "I dati del cedente verranno aggiornati automaticamente con quelli del detentore attuale.")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        # Layout pulsanti
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.saveButton)
        btn_layout.addWidget(self.cancelButton)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def _connect_signals(self):
        """Collega i segnali agli slot"""
        self.saveButton.clicked.connect(self.save_transfer)
        self.cancelButton.clicked.connect(self.reject)

        # Connessione per le tab detentore interno/esterno
        self.rbDetentoreDB.toggled.connect(self.on_destinatario_changed)

        # Connessione per la ricerca
        self.searchEdit.textChanged.connect(self.filter_detentori)

        # Connessione per convertire il testo in maiuscolo
        self.noteEdit.textChanged.connect(self.convert_to_uppercase)
        self.cognomeEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.nomeEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.cfEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.luogoNascitaEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.comuneResidenzaEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.provinciaEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.indirizzoEsternoEdit.textChanged.connect(self.convert_to_uppercase)
        self.telefonoEsternoEdit.textChanged.connect(self.convert_to_uppercase)

    def on_destinatario_changed(self, checked):
        """Cambia la vista in base alla selezione del tipo di destinatario"""
        if self.rbDetentoreDB.isChecked():
            self.stackedWidget.setCurrentIndex(0)
        else:
            self.stackedWidget.setCurrentIndex(1)

    def convert_to_uppercase(self):
        """Converte il testo dell'oggetto chiamante in maiuscolo"""
        sender = self.sender()
        cursor_pos = sender.cursorPosition()
        sender.setText(sender.text().upper())
        sender.setCursorPosition(cursor_pos)

    def filter_detentori(self, text):
        """Filtra la lista dei detentori in base al testo di ricerca"""
        if not text:
            # Se il testo è vuoto, mostra tutti i detentori
            self.detentoriCombo.clear()
            for id_detentore, display_text in self.detentori_map.items():
                self.detentoriCombo.addItem(display_text, id_detentore)
        else:
            # Filtra i detentori
            self.detentoriCombo.clear()
            text = text.upper()
            for id_detentore, display_text in self.detentori_map.items():
                # Cerca nel testo di visualizzazione che contiene cognome, nome, CF
                if text in display_text.upper():
                    self.detentoriCombo.addItem(display_text, id_detentore)

    def _load_detentori(self):
        """Carica tutti i detentori tranne quello attuale"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Prima ottieni la struttura della tabella detentori
            cursor.execute("PRAGMA table_info(detentori)")
            columns = [column[1] for column in cursor.fetchall()]

            # Costruisci la query con le colonne che esistono realmente
            query = "SELECT ID_Detentore"

            if "Cognome" in columns:
                query += ", Cognome"
            if "Nome" in columns:
                query += ", Nome"

            # Aggiungi CodiceFiscale se esiste con vari nomi possibili
            cf_column = None
            for col in ["CodiceFiscale", "CodFiscale", "CF"]:
                if col in columns:
                    query += f", {col}"
                    cf_column = col
                    break

            query += " FROM detentori WHERE ID_Detentore != ? ORDER BY "

            # Ordina per Cognome e Nome se esistono
            order_by = []
            if "Cognome" in columns:
                order_by.append("Cognome")
            if "Nome" in columns:
                order_by.append("Nome")

            if order_by:
                query += ", ".join(order_by)
            else:
                query += "ID_Detentore"  # Ordina per ID se non ci sono Cognome/Nome

            cursor.execute(query, (self.current_detentore,))

            detentori = cursor.fetchall()

            if not detentori:
                QMessageBox.warning(self, "Nessun Detentore",
                                    "Non ci sono altri detentori disponibili nel database. "
                                    "Sarà possibile solo specificare un detentore esterno.")
                self.rbDetentoreEsterno.setChecked(True)
                self.rbDetentoreDB.setEnabled(False)
                self.stackedWidget.setCurrentIndex(1)
                return

            self.detentori_id = []
            self.detentori_data = {}
            self.detentori_map = {}
            self.detentoriCombo.clear()

            for detentore in detentori:
                id_detentore = detentore[0]

                # Prepara i dati con controllo di sicurezza
                dati_detentore = {'Cognome': '', 'Nome': '', 'CodiceFiscale': ''}

                # Popola i dati in base alle colonne restituite
                col_index = 1  # Inizia da 1 perché l'indice 0 è ID_Detentore

                if "Cognome" in columns and col_index < len(detentore):
                    dati_detentore['Cognome'] = detentore[col_index] if detentore[col_index] else ''
                    col_index += 1

                if "Nome" in columns and col_index < len(detentore):
                    dati_detentore['Nome'] = detentore[col_index] if detentore[col_index] else ''
                    col_index += 1

                if cf_column and col_index < len(detentore):
                    dati_detentore['CodiceFiscale'] = detentore[col_index] if detentore[col_index] else ''

                self.detentori_id.append(id_detentore)
                self.detentori_data[id_detentore] = dati_detentore

                # Crea il testo da visualizzare
                display_text = ""
                if dati_detentore['Cognome'] or dati_detentore['Nome']:
                    display_text = f"{dati_detentore['Cognome']} {dati_detentore['Nome']}"
                else:
                    display_text = f"Detentore {id_detentore}"

                if dati_detentore['CodiceFiscale']:
                    display_text += f" - CF: {dati_detentore['CodiceFiscale']}"

                display_text += f" (ID: {id_detentore})"

                self.detentori_map[id_detentore] = display_text
                self.detentoriCombo.addItem(display_text, id_detentore)

            # Aggiungi un completamento automatico al campo di ricerca
            completer = QCompleter(list(self.detentori_map.values()), self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            self.searchEdit.setCompleter(completer)

        except Exception as e:
            print(f"Errore nel caricamento dei detentori: {e}")
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei detentori: {e}")
            self.reject()
        finally:
            if 'conn' in locals():
                conn.close()

    def update_cedente_data(self, nuovo_detentore_id):
        """Aggiorna i dati del cedente con i dati del detentore attuale"""
        try:
            if not self.current_detentore or not self.arma_id:
                return False

            if not self.current_detentore_data:
                return False

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Prima ottieni la struttura della tabella armi
            cursor.execute("PRAGMA table_info(armi)")
            columns = [column[1] for column in cursor.fetchall()]

            # Mappa i campi del detentore ai campi dell'arma con possibili varianti
            field_mapping = {
                'Cognome': ['CognomeCedente'],
                'Nome': ['NomeCedente'],
                'DataNascita': ['DataNascitaCedente'],
                'LuogoNascita': ['LuogoNascitaCedente'],
                'SiglaProvinciaNascita': ['SiglaProvinciaNascitaCedente'],
                'ComuneResidenza': ['ComuneResidenzaCedente'],
                'SiglaProvinciaResidenza': ['SiglaProvinciaResidenzaCedente'],
                'TipoViaResidenza': ['TipoViaResidenzaCedente'],
                'IndirizzoResidenza': ['IndirizzoResidenzaCedente'],
                'CivicoResidenza': ['CivicoResidenzaCedente'],
                'Telefono': ['TelefonoCedente']
            }

            # Costruisci la query aggiornando solo i campi esistenti
            query = "UPDATE armi SET "
            update_fields = []
            values = []

            for detentore_field, arma_fields in field_mapping.items():
                for arma_field in arma_fields:
                    if arma_field in columns and detentore_field in self.current_detentore_data:
                        update_fields.append(f"{arma_field} = ?")
                        values.append(self.current_detentore_data.get(detentore_field, ''))
                        break

            if not update_fields:
                print("Nessun campo da aggiornare")
                return False

            query += ", ".join(update_fields)
            query += " WHERE ID_ArmaDetenuta = ?"
            values.append(self.arma_id)

            cursor.execute(query, values)
            conn.commit()
            return True

        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati del cedente: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_detentore_esterno_data(self):
        """Restituisce i dati del detentore esterno inseriti manualmente"""
        data = {
            'Cognome': self.cognomeEsternoEdit.text(),
            'Nome': self.nomeEsternoEdit.text(),
            'CodiceFiscale': self.cfEsternoEdit.text(),
            'DataNascita': self.dataNascitaEsternoEdit.date().toString("yyyy-MM-dd"),
            'LuogoNascita': self.luogoNascitaEsternoEdit.text(),
            'ComuneResidenza': self.comuneResidenzaEsternoEdit.text(),
            'SiglaProvinciaResidenza': self.provinciaEsternoEdit.text(),
            'IndirizzoResidenza': self.indirizzoEsternoEdit.text(),
            'Telefono': self.telefonoEsternoEdit.text()
        }
        return data

    def validate_detentore_esterno(self):
        """Verifica che i campi obbligatori per il detentore esterno siano compilati"""
        if not self.cognomeEsternoEdit.text():
            QMessageBox.warning(self, "Dati Mancanti", "Il cognome del detentore esterno è obbligatorio.")
            return False
        if not self.nomeEsternoEdit.text():
            QMessageBox.warning(self, "Dati Mancanti", "Il nome del detentore esterno è obbligatorio.")
            return False

        # Per il codice fiscale potremmo anche fare una validazione più avanzata
        return True

    def save_transfer(self):
        """Esegue il trasferimento dell'arma"""
        try:
            # Raccogli i dati del trasferimento
            data_trasferimento = self.dataTransferimentoEdit.date().toString("yyyy-MM-dd")
            motivo = self.motivoCombo.currentText()
            note = self.noteEdit.text()

            # Determina se stiamo trasferendo a un detentore dal DB o esterno
            using_db_detentore = self.rbDetentoreDB.isChecked()

            # Ottieni i dati del detentore ricevente
            if using_db_detentore:
                # Detentore dal database
                index = self.detentoriCombo.currentIndex()
                if index < 0:
                    QMessageBox.warning(self, "Selezione Detentore", "Seleziona un detentore valido.")
                    return

                nuovo_detentore_id = self.detentoriCombo.currentData()
                if not nuovo_detentore_id:
                    QMessageBox.critical(self, "Errore", "ID detentore non valido.")
                    return

                ricevente_data = self.detentori_data.get(nuovo_detentore_id, {})
            else:
                # Detentore esterno
                if not self.validate_detentore_esterno():
                    return

                # Per un detentore esterno, impostiamo l'ID a -1 (valore speciale)
                nuovo_detentore_id = -1
                ricevente_data = self.get_detentore_esterno_data()

            # Aggiorna i dati del cedente prima di trasferire l'arma
            self.update_cedente_data(nuovo_detentore_id)

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Impostiamo esplicitamente il tipo di cedente a PERSONA FISICA quando trasferiamo armi tra detentori
            if using_db_detentore:
                try:
                    # Imposta sempre il tipo cedente a PERSONA FISICA per i trasferimenti tra detentori del database
                    cursor.execute("""
                        UPDATE armi 
                        SET TipoCedente = 'PERSONA FISICA'
                        WHERE ID_ArmaDetenuta = ?
                    """, (self.arma_id,))
                    print("Tipo cedente aggiornato a PERSONA FISICA durante il trasferimento")
                except Exception as e:
                    print(f"Errore nell'aggiornamento del tipo cedente: {e}")

            # Se stiamo trasferendo a un detentore interno, aggiorna il proprietario dell'arma
            if using_db_detentore:
                cursor.execute("""
                    UPDATE armi
                    SET ID_Detentore = ?
                    WHERE ID_ArmaDetenuta = ?
                """, (nuovo_detentore_id, self.arma_id))

            # Ottieni il timestamp corrente per la registrazione
            timestamp_registrazione = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

            # Verifica la struttura della tabella trasferimenti
            cursor.execute("PRAGMA table_info(trasferimenti)")
            columns = [column[1] for column in cursor.fetchall()]

            # Costruisci la query di inserimento dinamicamente
            query = "INSERT INTO trasferimenti ("
            values_placeholder = ""
            fields = []
            values = []

            # Mappa tra nomi alternativi di colonne e valori da inserire
            fields_to_insert = {
                'ID_Arma': self.arma_id,
                'ID_Detentore_Cedente': self.current_detentore,
                'ID_Detentore_Ricevente': nuovo_detentore_id if using_db_detentore else None,
                'Data_Trasferimento': data_trasferimento,
                'Motivo_Trasferimento': motivo,
                'Note': note,
                'Timestamp_Registrazione': timestamp_registrazione,
                'MarcaArma': self.arma_data.get('MarcaArma', ''),
                'ModelloArma': self.arma_data.get('ModelloArma', ''),
                'Matricola': self.arma_data.get('Matricola', ''),
                'CalibroArma': self.arma_data.get('CalibroArma', ''),
                'TipoArma': self.arma_data.get('TipoArma', ''),
                'Cedente_Cognome': self.current_detentore_data.get('Cognome', ''),
                'Cedente_Nome': self.current_detentore_data.get('Nome', ''),
                'Cedente_CodiceFiscale': self.current_detentore_data.get('CodiceFiscale', ''),
                'Ricevente_Cognome': ricevente_data.get('Cognome', ''),
                'Ricevente_Nome': ricevente_data.get('Nome', ''),
                'Ricevente_CodiceFiscale': ricevente_data.get('CodiceFiscale', ''),
                'ID_DetentorePrecedente': self.current_detentore,
                'ID_NuovoDetentore': nuovo_detentore_id if using_db_detentore else None
            }

            # Aggiungi solo i campi che esistono nella tabella
            for column_name in columns:
                if column_name in fields_to_insert:
                    fields.append(column_name)
                    values.append(fields_to_insert[column_name])

            if not fields:
                raise Exception("Nessun campo valido trovato nella tabella trasferimenti")

            query += ", ".join(fields)
            query += ") VALUES (" + ", ".join(["?" for _ in fields]) + ")"

            cursor.execute(query, values)
            conn.commit()

            # Messaggio di successo diverso in base al tipo di destinatario
            if using_db_detentore:
                QMessageBox.information(self, "Trasferimento Completato",
                                        "L'arma è stata trasferita al detentore selezionato con successo.")
            else:
                QMessageBox.information(self, "Trasferimento Completato",
                                        "Trasferimento al detentore esterno registrato con successo.\n" +
                                        "Nota: l'arma non è più tracciata nel database poiché trasferita a un soggetto esterno.")

            self.accept()

        except Exception as e:
            print(f"Errore durante il trasferimento: {e}")
            QMessageBox.critical(self, "Errore", f"Errore durante il trasferimento: {e}")
        finally:
            if 'conn' in locals():
                conn.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Test con valori fittizi
    dialog = TransferimentoDialog(arma_id=1, cedente_id=1, current_detentore=1)
    dialog.exec_()