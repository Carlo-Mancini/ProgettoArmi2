import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QGroupBox,
    QListWidget, QTabWidget, QWidget, QHBoxLayout, QListWidgetItem, QComboBox, QCompleter, QTableWidget
)
from Utility import convert_all_lineedits_to_uppercase
from PyQt5.QtCore import Qt
from Utility import get_sigla_provincia

class InserisciDetentoreDialog(QDialog):
    def __init__(self, detentore_data=None):
        super().__init__()
        self.detentore_data = detentore_data  # se presente, significa che è un update
        self.setWindowTitle("Detentore")
        self.setMinimumWidth(800)

        main_layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # Tab 1: Dati Detentore (Dati Personali e Contatti)
        tab_dati = QWidget()
        dati_layout = QHBoxLayout()
        group_personale = QGroupBox("Dati Personali")
        layout_personale = QFormLayout()
        self.nomeEdit = QLineEdit()
        self.cognomeEdit = QLineEdit()
        self.dataNascitaEdit = QLineEdit()
        # Inizializzo la QComboBox per "Luogo Nascita" con i comuni dal DB
        self.luogoNascitaCombo = QComboBox()
        self.luogoNascitaCombo.setEditable(True)
        comuni = load_comuni()  # restituisce una lista di comuni (senza il primo record, in maiuscolo)
        self.luogoNascitaCombo.addItems(comuni)
        self.luogoNascitaCombo.setCurrentIndex(-1)
        self.luogoNascitaCombo.clearEditText()
        completer = QCompleter(comuni)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.luogoNascitaCombo.setCompleter(completer)
        layout_personale.addRow("Luogo Nascita:", self.luogoNascitaCombo)
        # Collega editingFinished del QLineEdit interno per aggiornare la sigla
        self.luogoNascitaCombo.lineEdit().editingFinished.connect(self.update_sigla_provincia_nascita)

        self.siglaProvinciaNascitaEdit = QLineEdit()
        layout_personale.addRow("Sigla Provincia Nascita:", self.siglaProvinciaNascitaEdit)
        self.sessoEdit = QLineEdit()
        self.codiceFiscaleEdit = QLineEdit()
        layout_personale.addRow("Nome:", self.nomeEdit)
        layout_personale.addRow("Cognome:", self.cognomeEdit)
        layout_personale.addRow("Data Nascita:", self.dataNascitaEdit)
        layout_personale.addRow("Sesso:", self.sessoEdit)
        layout_personale.addRow("Codice Fiscale:", self.codiceFiscaleEdit)
        # Aggiungi un pulsante per il calcolo
        self.btnCalcolaCF = QPushButton("Calcola CF")
        layout_personale.addRow("", self.btnCalcolaCF)
        self.btnCalcolaCF.clicked.connect(self.calcola_codice_fiscale)

        group_personale.setLayout(layout_personale)

        group_contatti = QGroupBox("Contatti")
        layout_contatti = QFormLayout()
        self.comuneResidenzaCombo = QComboBox()
        self.comuneResidenzaCombo.setEditable(True)
        comuni = load_comuni()
        self.comuneResidenzaCombo.addItems(comuni)
        self.comuneResidenzaCombo.setCurrentIndex(-1)
        self.comuneResidenzaCombo.clearEditText()

        completer_residenza = QCompleter(comuni)
        completer_residenza.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneResidenzaCombo.setCompleter(completer_residenza)
        layout_contatti.addRow("Comune Residenza:", self.comuneResidenzaCombo)
        self.siglaProvinciaResidenzaEdit = QLineEdit()
        layout_contatti.addRow("Sigla Provincia Residenza:", self.siglaProvinciaResidenzaEdit)
        self.comuneResidenzaCombo.lineEdit().editingFinished.connect(self.update_sigla_provincia_residenza)
        self.tipoViaEdit = QLineEdit()
        self.viaEdit = QLineEdit()
        self.civicoEdit = QLineEdit()
        self.telefonoEdit = QLineEdit()
        layout_contatti.addRow("Tipo Via:", self.tipoViaEdit)
        layout_contatti.addRow("Via:", self.viaEdit)
        layout_contatti.addRow("Civico:", self.civicoEdit)
        layout_contatti.addRow("Telefono:", self.telefonoEdit)
        group_contatti.setLayout(layout_contatti)

        dati_layout.addWidget(group_personale)
        dati_layout.addWidget(group_contatti)
        tab_dati.setLayout(dati_layout)

        # Tab 2: Documenti e Detenzioni
        tab_documenti = QWidget()
        documenti_layout = QVBoxLayout()
        group_documenti = QGroupBox("Documenti e Detenzioni")
        layout_documenti = QFormLayout()
        self.fascicoloPersonaleEdit = QLineEdit()
        self.tipologiaTitoloEdit = QLineEdit()
        self.enteRilascioEdit = QLineEdit()
        self.provinciaEnteRilascioEdit = QLineEdit()
        self.dataRilascioEdit = QLineEdit()
        self.numeroPortoArmiEdit = QLineEdit()
        self.tipoLuogoDetenzioneEdit = QLineEdit()
        self.comuneDetenzioneEdit = QLineEdit()
        self.siglaProvinciaDetenzioneEdit = QLineEdit()
        self.tipoViaDetenzioneEdit = QLineEdit()
        self.viaDetenzioneEdit = QLineEdit()
        self.civicoDetenzioneEdit = QLineEdit()
        self.tipoDocumentoEdit = QLineEdit()
        self.numeroDocumentoEdit = QLineEdit()
        self.dataRilascioDocumentoEdit = QLineEdit()
        self.enteRilascioDocumentoEdit = QLineEdit()
        self.comuneEnteRilascioDocumentoEdit = QLineEdit()
        layout_documenti.addRow("Fascicolo Personale:", self.fascicoloPersonaleEdit)
        layout_documenti.addRow("Tipologia Titolo:", self.tipologiaTitoloEdit)
        layout_documenti.addRow("Ente Rilascio:", self.enteRilascioEdit)
        layout_documenti.addRow("Provincia Ente Rilascio:", self.provinciaEnteRilascioEdit)
        layout_documenti.addRow("Data Rilascio:", self.dataRilascioEdit)
        layout_documenti.addRow("Numero Porto Armi:", self.numeroPortoArmiEdit)
        layout_documenti.addRow("Tipo Luogo Detenzione:", self.tipoLuogoDetenzioneEdit)
        layout_documenti.addRow("Comune Detenzione:", self.comuneDetenzioneEdit)
        layout_documenti.addRow("Sigla Provincia Detenzione:", self.siglaProvinciaDetenzioneEdit)
        layout_documenti.addRow("Tipo Via Detenzione:", self.tipoViaDetenzioneEdit)
        layout_documenti.addRow("Via Detenzione:", self.viaDetenzioneEdit)
        layout_documenti.addRow("Civico Detenzione:", self.civicoDetenzioneEdit)
        layout_documenti.addRow("Tipo Documento:", self.tipoDocumentoEdit)
        layout_documenti.addRow("Numero Documento:", self.numeroDocumentoEdit)
        layout_documenti.addRow("Data Rilascio Documento:", self.dataRilascioDocumentoEdit)
        layout_documenti.addRow("Ente Rilascio Documento:", self.enteRilascioDocumentoEdit)
        layout_documenti.addRow("Comune Ente Rilascio Documento:", self.comuneEnteRilascioDocumentoEdit)
        group_documenti.setLayout(layout_documenti)
        documenti_layout.addWidget(group_documenti)
        tab_documenti.setLayout(documenti_layout)

        # Tab 3: Armi associate
        tab_armi = QWidget()
        armi_layout = QVBoxLayout()
        group_armi = QGroupBox("Armi del Detentore")
        layout_armi = QVBoxLayout()
        self.armiTable = QTableWidget()
        self.armiTable.setColumnCount(3)
        self.armiTable.setHorizontalHeaderLabels(["Marca", "Modello", "Matricola"])
        self.armiTable.horizontalHeader().setStretchLastSection(True)
        layout_armi.addWidget(self.armiTable)
        group_armi.setLayout(layout_armi)
        armi_layout.addWidget(group_armi)
        if detentore_data:
            self.populate_fields(detentore_data)
        self.carica_armi()
        # Connetti il double-click per modificare l'arma (usando il QTableWidget)
        self.armiTable.cellDoubleClicked.connect(self.modifica_arma)
        tab_armi.setLayout(armi_layout)


        # Pulsanti per gestire le armi
        btn_armi_layout = QHBoxLayout()
        self.btnInserisciArma = QPushButton("Inserisci Arma")
        self.btnModificaArma = QPushButton("Modifica Arma")
        self.btnCancellaArma = QPushButton("Cancella Arma")
        btn_armi_layout.addWidget(self.btnInserisciArma)
        btn_armi_layout.addWidget(self.btnModificaArma)
        btn_armi_layout.addWidget(self.btnCancellaArma)
        armi_layout.addLayout(btn_armi_layout)
        tab_armi.setLayout(armi_layout)

        # Aggiungo tutti i tab al QTabWidget
        tab_widget.addTab(tab_dati, "Detentore")
        tab_widget.addTab(tab_documenti, "Documenti")
        tab_widget.addTab(tab_armi, "Armi")

        # Aggiungo il QTabWidget al layout principale
        main_layout.addWidget(tab_widget)

        # Dopo aver aggiunto il QTabWidget, creo il layout per i pulsanti del detentore
        button_layout = QHBoxLayout()
        self.btnSaveDetentore = QPushButton("Salva Detentore")
        self.btnUpdateDetentore = QPushButton("Aggiorna Detentore")
        self.btnDeleteDetentore = QPushButton("Elimina Detentore")
        button_layout.addWidget(self.btnSaveDetentore)
        button_layout.addWidget(self.btnUpdateDetentore)
        button_layout.addWidget(self.btnDeleteDetentore)
        main_layout.addLayout(button_layout)
        self.btnSaveDetentore.clicked.connect(self.save_detentore)
        self.btnUpdateDetentore.clicked.connect(self.save_detentore)

        self.setLayout(main_layout)

        # Collego i pulsanti per le armi
        self.btnInserisciArma.clicked.connect(self.inserisci_arma)
        self.btnModificaArma.clicked.connect(self.modifica_arma)
        # Collego il doppio click sugli elementi della listbox
        self.btnCancellaArma.clicked.connect(self.cancella_arma)


        # Se vengono passati dati, precompila i campi
        if detentore_data:
            self.populate_fields(detentore_data)
        convert_all_lineedits_to_uppercase(self)
    def populate_fields(self, data):
        self.nomeEdit.setText(data.get('nome', ''))
        self.cognomeEdit.setText(data.get('cognome', ''))
        self.dataNascitaEdit.setText(data.get('dataNascita', ''))
        if data.get('luogoNascita'):
            index = self.luogoNascitaCombo.findText(data.get('luogoNascita'), Qt.MatchFixedString)
            if index >= 0:
                self.luogoNascitaCombo.setCurrentIndex(index)
            else:
                self.luogoNascitaCombo.setEditText(data.get('luogoNascita'))
        self.siglaProvinciaNascitaEdit.setText(data.get('siglaProvinciaNascita', ''))
        self.sessoEdit.setText(data.get('sesso', ''))
        self.codiceFiscaleEdit.setText(data.get('codiceFiscale', ''))
        if data.get('comuneResidenza'):
            index = self.comuneResidenzaCombo.findText(data.get('comuneResidenza'), Qt.MatchFixedString)
            if index >= 0:
                self.comuneResidenzaCombo.setCurrentIndex(index)
            else:
                self.comuneResidenzaCombo.setEditText(data.get('comuneResidenza'))
        self.siglaProvinciaResidenzaEdit.setText(data.get('siglaProvinciaResidenza', ''))
        self.tipoViaEdit.setText(data.get('tipoVia', ''))
        self.viaEdit.setText(data.get('via', ''))
        self.civicoEdit.setText(data.get('civico', ''))
        self.telefonoEdit.setText(data.get('telefono', ''))
        self.fascicoloPersonaleEdit.setText(data.get('fascicoloPersonale', ''))
        self.tipologiaTitoloEdit.setText(data.get('tipologiaTitolo', ''))
        self.enteRilascioEdit.setText(data.get('enteRilascio', ''))
        self.provinciaEnteRilascioEdit.setText(data.get('provinciaEnteRilascio', ''))
        self.dataRilascioEdit.setText(data.get('dataRilascio', ''))
        self.numeroPortoArmiEdit.setText(data.get('numeroPortoArmi', ''))
        self.tipoLuogoDetenzioneEdit.setText(data.get('tipoLuogoDetenzione', ''))
        self.comuneDetenzioneEdit.setText(data.get('comuneDetenzione', ''))
        self.siglaProvinciaDetenzioneEdit.setText(data.get('siglaProvinciaDetenzione', ''))
        self.tipoViaDetenzioneEdit.setText(data.get('tipoViaDetenzione', ''))
        self.viaDetenzioneEdit.setText(data.get('viaDetenzione', ''))
        self.civicoDetenzioneEdit.setText(data.get('civicoDetenzione', ''))
        self.tipoDocumentoEdit.setText(data.get('tipoDocumento', ''))
        self.numeroDocumentoEdit.setText(data.get('numeroDocumento', ''))
        self.dataRilascioDocumentoEdit.setText(data.get('dataRilascioDocumento', ''))
        self.enteRilascioDocumentoEdit.setText(data.get('enteRilascioDocumento', ''))
        self.comuneEnteRilascioDocumentoEdit.setText(data.get('comuneEnteRilascioDocumento', ''))
    def save_detentore(self):
        print("Salvataggio record Detentore in corso...")
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()
        # Raccogliamo i dati dai campi
        nome = self.nomeEdit.text()
        cognome = self.cognomeEdit.text()
        dataNascita = self.dataNascitaEdit.text()
        # Usa currentText() per la combo
        luogoNascita = self.luogoNascitaCombo.currentText()
        siglaProvinciaNascita = self.siglaProvinciaNascitaEdit.text()
        sesso = self.sessoEdit.text()
        codiceFiscale = self.codiceFiscaleEdit.text()
        # Per Comune Residenza usa currentText()
        comuneResidenza = self.comuneResidenzaCombo.currentText()
        siglaProvinciaResidenza = self.siglaProvinciaResidenzaEdit.text()
        tipoVia = self.tipoViaEdit.text()
        via = self.viaEdit.text()
        civico = self.civicoEdit.text()
        telefono = self.telefonoEdit.text()
        fascicoloPersonale = self.fascicoloPersonaleEdit.text()
        tipologiaTitolo = self.tipologiaTitoloEdit.text()
        enteRilascio = self.enteRilascioEdit.text()
        provinciaEnteRilascio = self.provinciaEnteRilascioEdit.text()
        dataRilascio = self.dataRilascioEdit.text()
        numeroPortoArmi = self.numeroPortoArmiEdit.text()
        tipoLuogoDetenzione = self.tipoLuogoDetenzioneEdit.text()
        comuneDetenzione = self.comuneDetenzioneEdit.text()
        siglaProvinciaDetenzione = self.siglaProvinciaDetenzioneEdit.text()
        tipoViaDetenzione = self.tipoViaDetenzioneEdit.text()
        viaDetenzione = self.viaDetenzioneEdit.text()
        civicoDetenzione = self.civicoDetenzioneEdit.text()
        tipoDocumento = self.tipoDocumentoEdit.text()
        numeroDocumento = self.numeroDocumentoEdit.text()
        dataRilascioDocumento = self.dataRilascioDocumentoEdit.text()
        enteRilascioDocumento = self.enteRilascioDocumentoEdit.text()
        comuneEnteRilascioDocumento = self.comuneEnteRilascioDocumentoEdit.text()

        if self.detentore_data and self.detentore_data.get('id'):
            # UPDATE record esistente
            cursor.execute("""
                UPDATE detentori
                SET Nome=?, Cognome=?, FascicoloPersonale=?, DataNascita=?, LuogoNascita=?, SiglaProvinciaNascita=?,
                    Sesso=?, CodiceFiscale=?, ComuneResidenza=?, SiglaProvinciaResidenza=?, TipoVia=?, Via=?, Civico=?, Telefono=?,
                    TipologiaTitolo=?, EnteRilascio=?, ProvinciaEnteRilascio=?, DataRilascio=?, NumeroPortoArmi=?, TipoLuogoDetenzione=?,
                    ComuneDetenzione=?, SiglaProvinciaDetenzione=?, TipoViaDetenzione=?, ViaDetenzione=?, CivicoDetenzione=?,
                    TipoDocumento=?, NumeroDocumento=?, DataRilascioDocumento=?, EnteRilascioDocumento=?, ComuneEnteRilascioDocumento=?
                WHERE ID_Detentore=?
            """, (
            nome, cognome, fascicoloPersonale, dataNascita, luogoNascita, siglaProvinciaNascita, sesso, codiceFiscale,
            comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono, tipologiaTitolo, enteRilascio,
            provinciaEnteRilascio, dataRilascio, numeroPortoArmi, tipoLuogoDetenzione, comuneDetenzione,
            siglaProvinciaDetenzione,
            tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento, dataRilascioDocumento,
            enteRilascioDocumento, comuneEnteRilascioDocumento, self.detentore_data.get('id')))
        else:
            # INSERT nuovo record
            cursor.execute("""
                INSERT INTO detentori (Nome, Cognome, FascicoloPersonale, DataNascita, LuogoNascita, SiglaProvinciaNascita,
                    Sesso, CodiceFiscale, ComuneResidenza, SiglaProvinciaResidenza, TipoVia, Via, Civico, Telefono,
                    TipologiaTitolo, EnteRilascio, ProvinciaEnteRilascio, DataRilascio, NumeroPortoArmi, TipoLuogoDetenzione,
                    ComuneDetenzione, SiglaProvinciaDetenzione, TipoViaDetenzione, ViaDetenzione, CivicoDetenzione,
                    TipoDocumento, NumeroDocumento, DataRilascioDocumento, EnteRilascioDocumento, ComuneEnteRilascioDocumento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            nome, cognome, fascicoloPersonale, dataNascita, luogoNascita, siglaProvinciaNascita, sesso, codiceFiscale,
            comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono, tipologiaTitolo, enteRilascio,
            provinciaEnteRilascio, dataRilascio, numeroPortoArmi, tipoLuogoDetenzione, comuneDetenzione,
            siglaProvinciaDetenzione,
            tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento, dataRilascioDocumento,
            enteRilascioDocumento, comuneEnteRilascioDocumento))
        conn.commit()
        conn.close()
        self.accept()

    def modifica_arma(self, row, column):
        from PyQt5.QtWidgets import QDialog
        # Recupera l'ID dell'arma dal primo item della riga
        id_item = self.armiTable.item(row, 0)
        if id_item:
            arma_id = id_item.data(Qt.UserRole)
            import sqlite3
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
            row_data = cursor.fetchone()
            conn.close()
            if row_data:
                columns = ["ID_ArmaDetenuta", "ID_Detentore", "TipoArma", "MarcaArma", "ModelloArma", "TipologiaArma",
                           "Matricola", "CalibroArma", "MatricolaCanna", "LunghezzaCanna", "NumeroCanne",
                           "ArmaLungaCorta",
                           "TipoCanna", "CategoriaArma", "FunzionamentoArma", "CaricamentoArma", "PunzoniArma",
                           "StatoProduzioneArma", "ExOrdDem", "TipoMunizioni", "QuantitaMunizioni", "TipoBossolo",
                           "TipoCedente", "NoteArma", "CognomeCedente", "NomeCedente", "DataNascitaCedente",
                           "LuogoNascitaCedente", "SiglaProvinciaResidenzaCedente", "ComuneResidenzaCedente",
                           "SiglaProvinciaNascitaCedente", "TipoViaResidenzaCedente", "IndirizzoResidenzaCedente",
                           "CivicoResidenzaCedente", "TelefonoCedente"]
                arma_data = dict(zip(columns, row_data))
                from ArmiDialog import ArmaDialog
                det_id = self.detentore_data.get('id') if self.detentore_data else None
                dialog = ArmaDialog(arma_data=arma_data, detentore_id=det_id)
                if dialog.exec_() == QDialog.Accepted:
                    self.carica_armi()

    def carica_armi(self):
        import sqlite3
        from PyQt5.QtWidgets import QTableWidgetItem
        from PyQt5.QtCore import Qt

        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()
        if self.detentore_data and self.detentore_data.get('id'):
            det_id = self.detentore_data.get('id')
            cursor.execute("SELECT ID_ArmaDetenuta, MarcaArma, ModelloArma, Matricola FROM armi WHERE ID_Detentore = ?",
                           (det_id,))
            rows = cursor.fetchall()
            conn.close()

            self.armiTable.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                id_arma = row[0]
                marca = row[1] if row[1] is not None else ""
                modello = row[2] if row[2] is not None else ""
                matricola = row[3] if row[3] is not None else ""

                marca_item = QTableWidgetItem(marca)
                modello_item = QTableWidgetItem(modello)
                matricola_item = QTableWidgetItem(matricola)

                # Salva l'ID dell'arma nel primo item tramite Qt.UserRole
                marca_item.setData(Qt.UserRole, id_arma)

                self.armiTable.setItem(row_index, 0, marca_item)
                self.armiTable.setItem(row_index, 1, modello_item)
                self.armiTable.setItem(row_index, 2, matricola_item)
        else:
            self.armiTable.setRowCount(0)
        conn.close()

    def inserisci_arma(self):
        from ArmiDialog import ArmaDialog
        det_id = self.detentore_data.get('id') if self.detentore_data else None
        dialog = ArmaDialog(arma_data=None, detentore_id=det_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carica_armi()

    def cancella_arma(self):
        # Ottieni la riga selezionata nella tabella
        row = self.armiTable.currentRow()
        if row < 0:
            return  # Nessuna riga selezionata
        # Recupera l'ID dell'arma dal primo item della riga (salvato in Qt.UserRole)
        item = self.armiTable.item(row, 0)
        if item is None:
            return
        arma_id = item.data(Qt.UserRole)
        import sqlite3
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
        conn.commit()
        conn.close()
        # Ricarica la tabella per aggiornare la visualizzazione
        self.carica_armi()

    def update_sigla_provincia_nascita(self):
        comune = self.luogoNascitaCombo.currentText()
        if not comune:
            self.siglaProvinciaNascitaEdit.clear()
            return
        sigla = get_sigla_provincia(comune)
        self.siglaProvinciaNascitaEdit.setText(sigla)
    def update_sigla_provincia_residenza(self):
        # Ottieni il comune selezionato dalla combo (già in maiuscolo se lo hai caricato così)
        comune = self.comuneResidenzaCombo.currentText()
        if not comune:
            self.siglaProvinciaResidenzaEdit.clear()
            return
        # Richiama la funzione globale per ottenere la sigla della provincia
        from Utility import get_sigla_provincia
        sigla = get_sigla_provincia(comune)
        self.siglaProvinciaResidenzaEdit.setText(sigla)
    def calcola_codice_fiscale(self):
        from Utility import compute_codice_fiscale
        # Recupera i dati necessari
        nome = self.nomeEdit.text().strip()
        cognome = self.cognomeEdit.text().strip()
        data_nascita = self.dataNascitaEdit.text().strip()
        sesso = self.sessoEdit.text().strip()
        comune_nascita = self.luogoNascitaCombo.currentText().strip()

        if not (nome and cognome and data_nascita and sesso and comune_nascita):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Dati mancanti", "Inserisci nome, cognome, data di nascita, sesso e comune di nascita.")
            return

        try:
            cf = compute_codice_fiscale(nome, cognome, data_nascita, sesso, comune_nascita)
            self.codiceFiscaleEdit.setText(cf)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Errore", f"Impossibile calcolare il codice fiscale:\n{e}")


def load_comuni():
    try:
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()
        cursor.execute('SELECT [Denominazione in italiano] FROM comuni')
        rows = cursor.fetchall()
        conn.close()
        # Salta il primo record e converte in maiuscolo
        return [row[0].upper() for row in rows[1:] if row[0]]
    except Exception as e:
        print("Errore nel caricamento dei comuni:", e)
        return []


class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test ComboBox Comuni")
        layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.setEditable(True)
        comuni = load_comuni()
        self.combo.addItems(comuni)
        completer = QCompleter(comuni)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo.setCompleter(completer)
        layout.addWidget(self.combo)
        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = InserisciDetentoreDialog()
    dialog.exec_()
