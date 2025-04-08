import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QMessageBox, QDateEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from Utility import convert_all_lineedits_to_uppercase


class TransferimentoDialog(QDialog):
    """Dialog per gestire il trasferimento di un'arma tra detentori"""

    def __init__(self, arma_id, cedente_id, current_detentore=None, parent=None):
        super().__init__(parent)
        self.arma_id = arma_id
        self.cedente_id = cedente_id
        self.current_detentore = current_detentore
        self.destinatario_id = None

        self.setup_ui()
        self.setup_connections()
        self.load_initial_data()
        convert_all_lineedits_to_uppercase(self)  # Applica uppercase a tutti i campi

        self.setWindowTitle("Trasferimento Arma")
        self.setMinimumWidth(600)
        self.setStyleSheet("QLineEdit { text-transform: uppercase; }")

    # region UI Setup
    def setup_ui(self):
        """Configura l'interfaccia grafica"""
        self.layout = QVBoxLayout(self)
        self.create_arma_section()
        self.create_transfer_section()
        self.create_external_recipient_section()
        self.create_action_buttons()

    def setup_connections(self):
        """Configura i collegamenti tra segnali e slot"""
        self.btnCercaDetentore.clicked.connect(self.cerca_detentore)
        self.btnNuovoDetentore.clicked.connect(self.nuovo_detentore)
        self.saveButton.clicked.connect(self.save_transfer)
        self.cancelButton.clicked.connect(self.reject)

    def create_arma_section(self):
        """Crea la sezione per visualizzare i dati dell'arma"""
        group = QGroupBox("Dati Arma")
        form = QFormLayout()

        fields = [
            ("Tipo Arma:", "tipoArmaEdit"),
            ("Marca:", "marcaArmaEdit"),
            ("Modello:", "modelloArmaEdit"),
            ("Matricola:", "matricolaEdit")
        ]

        for label, name in fields:
            edit = self.create_readonly_lineedit()
            setattr(self, name, edit)
            form.addRow(label, edit)

        group.setLayout(form)
        self.layout.addWidget(group)

    def create_transfer_section(self):
        """Crea la sezione per i dati del trasferimento"""
        group = QGroupBox("Dati Trasferimento")
        form = QFormLayout()

        # Data movimento
        self.dataMovimentoEdit = QDateEdit()
        self.dataMovimentoEdit.setDate(QDate.currentDate())
        self.dataMovimentoEdit.setCalendarPopup(True)

        # Tipo movimento
        self.tipoMovimentoCombo = QComboBox()
        self.tipoMovimentoCombo.addItems(["VENDITA", "DONO", "SUCCESSIONE", "DEPOSITO", "ALTRO"])

        # Destinatario
        self.destinatarioEdit = QLineEdit()
        self.btnCercaDetentore = QPushButton("Cerca")
        self.btnNuovoDetentore = QPushButton("Nuovo Detentore")
        det_layout = QHBoxLayout()
        det_layout.addWidget(self.destinatarioEdit)
        det_layout.addWidget(self.btnCercaDetentore)
        det_layout.addWidget(self.btnNuovoDetentore)

        # Note
        self.noteEdit = QLineEdit()

        form.addRow("Data Movimento:", self.dataMovimentoEdit)
        form.addRow("Tipo Movimento:", self.tipoMovimentoCombo)
        form.addRow("Destinatario:", det_layout)
        form.addRow("Note:", self.noteEdit)

        group.setLayout(form)
        self.layout.addWidget(group)

    def create_external_recipient_section(self):
        """Crea la sezione per inserire un destinatario esterno"""
        self.group_dest_esterno = QGroupBox("Dati destinatario esterno")
        form = QFormLayout()

        fields = [
            ("Nome:", "nomeDestEdit"),
            ("Cognome:", "cognomeDestEdit"),
            ("Data di nascita (gg/mm/aaaa):", "dataNascitaDestEdit"),
            ("Luogo di nascita:", "luogoNascitaDestEdit"),
            ("Comune di residenza:", "comuneResidenzaDestEdit"),
            ("Via:", "viaDestEdit"),
            ("Civico:", "civicoDestEdit")
        ]

        for label, name in fields:
            edit = QLineEdit()
            setattr(self, name, edit)
            form.addRow(label, edit)

        self.group_dest_esterno.setLayout(form)
        self.group_dest_esterno.setVisible(False)
        self.layout.addWidget(self.group_dest_esterno)

    # endregion

    def create_action_buttons(self):
        """Crea i pulsanti di azione"""
        btn_layout = QHBoxLayout()
        self.saveButton = QPushButton("Conferma Trasferimento")
        self.cancelButton = QPushButton("Annulla")

        btn_layout.addWidget(self.saveButton)
        btn_layout.addWidget(self.cancelButton)
        self.layout.addLayout(btn_layout)

    def create_readonly_lineedit(self):
        """Crea un QLineEdit readonly con stile coerente"""
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        return line_edit

    def load_initial_data(self):
        """Carica i dati iniziali dell'arma e dei detentori"""
        self.load_arma_data()
        self.load_detentori()

    def load_detentori(self):
        """Carica la lista dei detentori disponibili (escluso il cedente)"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID_Detentore, Cognome, Nome FROM detentori WHERE ID_Detentore != ?",
                (self.cedente_id,)
            )
            # Nota: I risultati non vengono usati direttamente in questa versione
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i detentori:\n{e}")

    def load_arma_data(self):
        """Carica i dati dell'arma da trasferire"""
        try:
            with sqlite3.connect("gestione_armi.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TipoArma, MarcaArma, ModelloArma, Matricola 
                    FROM armi WHERE ID_ArmaDetenuta = ?
                """, (self.arma_id,))

                if row := cursor.fetchone():
                    self.tipoArmaEdit.setText(row[0])
                    self.marcaArmaEdit.setText(row[1])
                    self.modelloArmaEdit.setText(row[2])
                    self.matricolaEdit.setText(row[3])
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati dell'arma:\n{e}")

    def save_transfer(self):
        """Salva i dati del trasferimento nel database"""
        try:
            if not (destinatario_data := self.prepare_recipient_data()):
                return

            if self.destinatario_id is None:
                self.insert_new_detentore(destinatario_data)

            with sqlite3.connect("gestione_armi.db") as conn:
                cursor = conn.cursor()
                self.save_movement(cursor, destinatario_data)
                self.update_weapon_owner(cursor)
                conn.commit()

            self.clear_external_recipient_fields()
            QMessageBox.information(self, "Successo", "Trasferimento registrato con successo.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile completare il trasferimento:\n{e}")

    def prepare_recipient_data(self):
        """Prepara e valida i dati del destinatario"""
        if self.destinatario_id is None:  # Destinatario esterno
            return self.prepare_external_recipient_data()
        else:  # Destinatario esistente
            return self.get_existing_recipient_data()

    def prepare_external_recipient_data(self):
        """Prepara e valida i dati del destinatario esterno"""
        nome_ext = self.nomeDestEdit.text().strip()
        cognome_ext = self.cognomeDestEdit.text().strip()
        data_nasc_ext = self.dataNascitaDestEdit.text().strip()
        luogo_nasc_ext = self.luogoNascitaDestEdit.text().strip()
        residenza = self.comuneResidenzaDestEdit.text().strip()
        via = self.viaDestEdit.text().strip()
        civico = self.civicoDestEdit.text().strip()

        # Validazione campi obbligatori
        campi_mancanti = []
        if not nome_ext: campi_mancanti.append("Nome")
        if not cognome_ext: campi_mancanti.append("Cognome")
        if not data_nasc_ext: campi_mancanti.append("Data di nascita")
        if not luogo_nasc_ext: campi_mancanti.append("Luogo di nascita")

        if campi_mancanti:
            QMessageBox.warning(
                self,
                "Dati Mancanti",
                "Compila i seguenti campi:\n- " + "\n- ".join(campi_mancanti)
            )
            return None

        return [cognome_ext, nome_ext, data_nasc_ext, luogo_nasc_ext, residenza, via, civico]

    def get_existing_recipient_data(self):
        """Recupera i dati del destinatario esistente dal database"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Cognome, Nome, DataNascita, LuogoNascita FROM detentori WHERE ID_Detentore = ?",
                (self.destinatario_id,)
            )
            destinatario_data = list(cursor.fetchone()) + ["", "",
                                                           ""]  # aggiunge campi vuoti per residenza, via, civico
            conn.close()
            return destinatario_data
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile recuperare i dati del destinatario:\n{e}")
            return None

    def get_cedente_data(self):
        """Recupera i dati del cedente dal database"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Cognome, Nome, DataNascita, LuogoNascita FROM detentori WHERE ID_Detentore = ?",
                (self.cedente_id,)
            )
            cedente_data = cursor.fetchone()
            conn.close()
            return cedente_data
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile recuperare i dati del cedente:\n{e}")
            return None

    def get_arma_data(self):
        """Recupera i dati completi dell'arma dal database"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TipoArma, MarcaArma, ModelloArma, TipologiaArma, Matricola,
                       CalibroArma, MatricolaCanna, LunghezzaCanna, NumeroCanne, ArmaLungaCorta
                FROM armi WHERE ID_ArmaDetenuta = ?
            """, (self.arma_id,))
            arma_data = cursor.fetchone()
            conn.close()
            return arma_data
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile recuperare i dati dell'arma:\n{e}")
            return None

    def save_movement(self, cursor, destinatario_data):
        """Salva il movimento nel database"""
        query = """
            INSERT INTO MovimentiArma (
                ID_ArmaDetenuta, ID_Detentore, TipoArma, MarcaArma, ModelloArma, TipologiaArma,
                Matricola, CalibroArma, MatricolaCanna, LunghezzaCanna, NumeroCanne, ArmaLungaCorta,
                TipoCanna, CategoriaArma, FunzionamentoArma, CaricamentoArma, StatoProduzioneArma,
                TipoMunizioni, QuantitaMunizioni, TipoBossolo, TipoCedente, NoteArma, DataTrasferimento,
                MotivoTrasferimento, NomeCedente, CognomeCedente, DataNascitaCedente, LuogoNascitaCedente,
                Cedente_CodiceFiscale, TelefonoCedente, Acquirente_Nome, Acquirente_Cognome,
                DataNascitaDestinatario, LuogoNascitaDestinatario, Acquirente_CodiceFiscale,
                DataMovimento, TipoMovimento, ID_Cedente, ID_Destinatario, Note, CognomeDestinatario,
                NomeDestinatario, AltroCampo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = self.prepare_movement_params(destinatario_data)
        cursor.execute(query, params)

    def update_weapon_owner(self, cursor):
        """Aggiorna il proprietario dell'arma"""
        cursor.execute("""
            UPDATE armi 
            SET ID_Detentore = ?
            WHERE ID_ArmaDetenuta = ?
        """, (self.destinatario_id, self.arma_id))
    #endregion

    #region Helpers
    def setup_connections(self):
        """Configura i collegamenti tra segnali e slot"""
        self.btnCercaDetentore.clicked.connect(self.cerca_detentore)
        self.btnNuovoDetentore.clicked.connect(self.nuovo_detentore)
        self.saveButton.clicked.connect(self.save_transfer)
        self.cancelButton.clicked.connect(self.reject)

    def create_readonly_lineedit(self):
        """Crea un QLineEdit readonly con stile coerente"""
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        return line_edit

    def save_transfer_to_db(self, destinatario_data, data_movimento, tipo_movimento, note, cedente_data, arma_data):
        """Salva i dati del trasferimento nel database"""
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()

        # Inserimento nella tabella MovimentiArma
        cursor.execute("""
            INSERT INTO MovimentiArma (
                ID_ArmaDetenuta, ID_Detentore, TipoArma, MarcaArma, ModelloArma, TipologiaArma,
                Matricola, CalibroArma, MatricolaCanna, LunghezzaCanna, NumeroCanne, ArmaLungaCorta,
                TipoCanna, CategoriaArma, FunzionamentoArma, CaricamentoArma, StatoProduzioneArma,
                TipoMunizioni, QuantitaMunizioni, TipoBossolo, TipoCedente, NoteArma, DataTrasferimento,
                MotivoTrasferimento, NomeCedente, CognomeCedente, DataNascitaCedente, LuogoNascitaCedente,
                Cedente_CodiceFiscale, TelefonoCedente, Acquirente_Nome, Acquirente_Cognome,
                DataNascitaDestinatario, LuogoNascitaDestinatario, Acquirente_CodiceFiscale,
                DataMovimento, TipoMovimento, ID_Cedente, ID_Destinatario, Note, CognomeDestinatario,
                NomeDestinatario, AltroCampo
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?  
            )
        """, (
            self.arma_id,  # ID_ArmaDetenuta
            None if self.destinatario_id is None else self.destinatario_id,
            *arma_data[:10],  # Dati arma (primi 10 campi)
            *[""] * 10,  # Campi vuoti per dati non specificati
            data_movimento,  # DataTrasferimento
            tipo_movimento,  # MotivoTrasferimento
            cedente_data[1],  # NomeCedente
            cedente_data[0],  # CognomeCedente
            cedente_data[2],  # DataNascitaCedente
            cedente_data[3],  # LuogoNascitaCedente
            *[""] * 2,  # CodiceFiscale e Telefono cedente
            destinatario_data[1],  # Nome destinatario
            destinatario_data[0],  # Cognome destinatario
            destinatario_data[2],  # Data di nascita destinatario
            destinatario_data[3],  # Luogo di nascita destinatario
            "",  # Codice fiscale destinatario
            data_movimento,  # DataMovimento
            tipo_movimento,  # TipoMovimento
            self.cedente_id,
            None if self.destinatario_id is None else self.destinatario_id,
            note,
            destinatario_data[0],  # CognomeDestinatario
            destinatario_data[1],  # NomeDestinatario
            ""  # AltroCampo
        ))

        # Aggiorna il detentore dell'arma
        cursor.execute("""
            UPDATE armi 
            SET ID_Detentore = ?
            WHERE ID_ArmaDetenuta = ?
        """, (self.destinatario_id, self.arma_id))

        conn.commit()
        conn.close()

    def prepare_movement_params(self, destinatario_data):
        """Prepara i parametri per l'inserimento del movimento"""
        cedente_data = self.get_cedente_data()
        arma_data = self.get_arma_data()

        return (
            self.arma_id,
            self.destinatario_id,
            *arma_data[:10],
            *[""] * 10,
            self.dataMovimentoEdit.date().toString("yyyy-MM-dd"),
            self.tipoMovimentoCombo.currentText(),
            cedente_data[1],  # NomeCedente
            cedente_data[0],  # CognomeCedente
            cedente_data[2],  # DataNascitaCedente
            cedente_data[3],  # LuogoNascitaCedente
            *[""] * 2,
            destinatario_data[1],  # Nome destinatario
            destinatario_data[0],  # Cognome destinatario
            destinatario_data[2],  # Data di nascita
            destinatario_data[3],  # Luogo di nascita
            "",
            self.dataMovimentoEdit.date().toString("yyyy-MM-dd"),
            self.tipoMovimentoCombo.currentText(),
            self.cedente_id,
            self.destinatario_id,
            self.noteEdit.text(),
            destinatario_data[0],  # CognomeDestinatario
            destinatario_data[1],  # NomeDestinatario
            ""
        )
    
    def clear_external_recipient_fields(self):
        """Pulisce i campi del destinatario esterno"""
        for field in [self.nomeDestEdit, self.cognomeDestEdit, self.dataNascitaDestEdit,
                     self.luogoNascitaDestEdit, self.comuneResidenzaDestEdit, self.viaDestEdit,
                     self.civicoDestEdit]:
            field.clear()
        self.group_dest_esterno.setVisible(False)
    #endregion
    def cerca_detentore(self):
        """Cerca un detentore nel database"""
        nome_cognome = self.destinatarioEdit.text().strip().upper()
        if not nome_cognome:
            QMessageBox.warning(self, "Attenzione", "Inserisci nome e cognome da cercare.")
            return

        try:
            # Separa nome e cognome (assumendo formato: COGNOME NOME)
            parts = nome_cognome.split()
            if len(parts) < 2:
                QMessageBox.warning(self, "Formato Errato", "Scrivi almeno nome e cognome separati da spazio.")
                return

            cognome = parts[0]
            nome = " ".join(parts[1:])

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID_Detentore FROM detentori
                WHERE UPPER(Cognome) = ? AND UPPER(Nome) = ?
            """, (cognome, nome))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.destinatario_id = row[0]
                self.group_dest_esterno.setVisible(False)
                QMessageBox.information(self, "Trovato", "Detentore trovato e selezionato.")
            else:
                self.destinatario_id = None
                self.group_dest_esterno.setVisible(True)
                QMessageBox.information(self, "Non trovato",
                                        "Nessun detentore trovato. Inserisci i dati manualmente.")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca:\n{e}")

    def nuovo_detentore(self):
        """Apre il dialog per inserire un nuovo detentore"""
        from Detentori import InserisciDetentoreDialog
        dialog = InserisciDetentoreDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.cerca_detentore()  # Ricarica dopo l'inserimento