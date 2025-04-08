import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QGroupBox,
    QListWidget, QTabWidget, QWidget, QHBoxLayout, QListWidgetItem, QComboBox,
    QCompleter, QTableWidget, QGridLayout, QLabel, QScrollArea, QSizePolicy,
    QMessageBox, QHeaderView, QTableWidgetItem
)
from Utility import convert_all_lineedits_to_uppercase
from PyQt5.QtCore import Qt
from Utility import get_sigla_provincia, DateInputWidget


class InserisciDetentoreDialog(QDialog):
    def __init__(self, detentore_data=None):
        super().__init__()
        self.detentore_data = detentore_data  # se presente, significa che è un update
        self.setWindowTitle("Detentore")
        self.setMinimumWidth(850)
        self.setMinimumHeight(600)

        main_layout = QVBoxLayout()

        # Creazione del tab widget principale
        self.tab_widget = QTabWidget()

        # Creazione delle tab
        self.create_dati_tab()
        self.create_documenti_tab()
        self.create_armi_tab()

        # Aggiunta delle tab al QTabWidget
        self.tab_widget.addTab(self.tab_dati, "Detentore")
        self.tab_widget.addTab(self.tab_documenti, "Documenti")
        self.tab_widget.addTab(self.tab_armi, "Armi")

        # Aggiungo il QTabWidget al layout principale
        main_layout.addWidget(self.tab_widget)

        # Creazione dei pulsanti principali
        self.create_main_buttons()
        main_layout.addLayout(self.button_layout)

        self.setLayout(main_layout)

        # Connessione dei segnali
        self.connect_signals()

        # Popolazione dei campi se sono forniti dati
        if detentore_data:
            self.populate_fields(detentore_data)
            self.carica_armi()

        # Converti tutto in maiuscolo
        convert_all_lineedits_to_uppercase(self)

    def create_dati_tab(self):
        """Crea la tab con i dati personali e di contatto del detentore"""
        self.tab_dati = QWidget()
        main_layout = QVBoxLayout()

        # Creazione dei widget
        self.create_personal_data_widgets()
        self.create_contact_widgets()

        # Creazione dei gruppi
        personal_group = self.create_personal_data_group()
        contact_group = self.create_contact_group()

        # Aggiunta dei gruppi al layout
        main_layout.addWidget(personal_group)
        main_layout.addWidget(contact_group)
        main_layout.addStretch(1)

        self.tab_dati.setLayout(main_layout)

    def create_personal_data_widgets(self):
        """Crea i widget per i dati personali"""
        self.nomeEdit = QLineEdit()
        self.cognomeEdit = QLineEdit()

        # Sostituisci QLineEdit con DateInputWidget per la data di nascita
        self.dataNascitaEdit = DateInputWidget()
        self.dataNascitaEdit.setDisplayFormat("dd/MM/yyyy")

        # Combo per il luogo di nascita
        self.luogoNascitaCombo = QComboBox()
        self.luogoNascitaCombo.setEditable(True)
        comuni = load_comuni()
        self.luogoNascitaCombo.addItems(comuni)
        self.luogoNascitaCombo.setCurrentIndex(-1)
        self.luogoNascitaCombo.clearEditText()

        completer = QCompleter(comuni)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.luogoNascitaCombo.setCompleter(completer)

        self.siglaProvinciaNascitaEdit = QLineEdit()
        self.siglaProvinciaNascitaEdit.setMaximumWidth(60)
        self.sessoEdit = QLineEdit()
        self.sessoEdit.setMaximumWidth(60)
        self.codiceFiscaleEdit = QLineEdit()
        self.btnCalcolaCF = QPushButton("Calcola CF")
        self.btnCalcolaCF.setMaximumWidth(100)

    def create_contact_widgets(self):
        """Crea i widget per i contatti"""
        self.comuneResidenzaCombo = QComboBox()
        self.comuneResidenzaCombo.setEditable(True)
        comuni = load_comuni()
        self.comuneResidenzaCombo.addItems(comuni)
        self.comuneResidenzaCombo.setCurrentIndex(-1)
        self.comuneResidenzaCombo.clearEditText()

        completer_residenza = QCompleter(comuni)
        completer_residenza.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneResidenzaCombo.setCompleter(completer_residenza)

        self.siglaProvinciaResidenzaEdit = QLineEdit()
        self.siglaProvinciaResidenzaEdit.setMaximumWidth(60)
        self.tipoViaEdit = QLineEdit()
        self.tipoViaEdit.setMaximumWidth(100)
        self.viaEdit = QLineEdit()
        self.civicoEdit = QLineEdit()
        self.civicoEdit.setMaximumWidth(80)
        self.telefonoEdit = QLineEdit()

    def create_personal_data_group(self):
        """Crea il gruppo per i dati personali"""
        group_personale = QGroupBox("Dati Personali")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Cognome:"), 0, 0)
        grid.addWidget(self.cognomeEdit, 0, 1)
        grid.addWidget(QLabel("Nome:"), 0, 2)
        grid.addWidget(self.nomeEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Data Nascita:"), 1, 0)
        grid.addWidget(self.dataNascitaEdit, 1, 1)
        grid.addWidget(QLabel("Sesso:"), 1, 2)
        grid.addWidget(self.sessoEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Luogo Nascita:"), 2, 0)
        grid.addWidget(self.luogoNascitaCombo, 2, 1)
        grid.addWidget(QLabel("Prov. Nascita:"), 2, 2)
        grid.addWidget(self.siglaProvinciaNascitaEdit, 2, 3)

        # Riga 4
        grid.addWidget(QLabel("Codice Fiscale:"), 3, 0)
        grid.addWidget(self.codiceFiscaleEdit, 3, 1)
        grid.addWidget(self.btnCalcolaCF, 3, 2)

        group_personale.setLayout(grid)
        return group_personale

    def create_contact_group(self):
        """Crea il gruppo per i contatti"""
        group_contatti = QGroupBox("Contatti e Residenza")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Comune Residenza:"), 0, 0)
        grid.addWidget(self.comuneResidenzaCombo, 0, 1)
        grid.addWidget(QLabel("Provincia:"), 0, 2)
        grid.addWidget(self.siglaProvinciaResidenzaEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Tipo Via:"), 1, 0)
        grid.addWidget(self.tipoViaEdit, 1, 1)
        grid.addWidget(QLabel("Via:"), 1, 2)
        grid.addWidget(self.viaEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Civico:"), 2, 0)
        grid.addWidget(self.civicoEdit, 2, 1)
        grid.addWidget(QLabel("Telefono:"), 2, 2)
        grid.addWidget(self.telefonoEdit, 2, 3)

        group_contatti.setLayout(grid)
        return group_contatti

    def create_documenti_tab(self):
        """Crea la tab con i documenti e detenzioni"""
        self.tab_documenti = QWidget()
        main_layout = QVBoxLayout()

        # Creazione dei widget per i documenti
        self.create_documents_widgets()

        # Utilizzo di uno scroll area per gestire molti campi
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Creazione dei gruppi
        license_group = self.create_license_group()
        detention_group = self.create_detention_group()
        document_group = self.create_document_group()

        # Aggiunta dei gruppi al layout
        content_layout.addWidget(license_group)
        content_layout.addWidget(detention_group)
        content_layout.addWidget(document_group)
        content_layout.addStretch(1)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        self.tab_documenti.setLayout(main_layout)

    def create_documents_widgets(self):
        """Crea i widget per i documenti"""
        # Fascicolo e titolo
        self.fascicoloPersonaleEdit = QLineEdit()
        self.tipologiaTitoloEdit = QLineEdit()

        # Ente rilascio
        self.enteRilascioEdit = QLineEdit()

        # Combobox province per ente rilascio
        self.provinciaEnteRilascioCombo = QComboBox()
        self.provinciaEnteRilascioCombo.setEditable(True)
        province = load_province()
        self.provinciaEnteRilascioCombo.addItems(province)
        self.provinciaEnteRilascioCombo.setCurrentIndex(-1)
        self.provinciaEnteRilascioCombo.clearEditText()
        completer_provincia = QCompleter(province)
        completer_provincia.setCaseSensitivity(Qt.CaseInsensitive)
        self.provinciaEnteRilascioCombo.setCompleter(completer_provincia)

        # Sostituzione per la data di rilascio
        self.dataRilascioEdit = DateInputWidget()
        self.dataRilascioEdit.setDisplayFormat("dd/MM/yyyy")

        self.numeroPortoArmiEdit = QLineEdit()

        # Luogo detenzione
        self.tipoLuogoDetenzioneEdit = QLineEdit()

        # Converto comuneDetenzioneEdit da QLineEdit a QComboBox
        self.comuneDetenzioneCombo = QComboBox()
        self.comuneDetenzioneCombo.setEditable(True)
        comuni = load_comuni()
        self.comuneDetenzioneCombo.addItems(comuni)
        self.comuneDetenzioneCombo.setCurrentIndex(-1)
        self.comuneDetenzioneCombo.clearEditText()

        completer_detenzione = QCompleter(comuni)
        completer_detenzione.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneDetenzioneCombo.setCompleter(completer_detenzione)

        self.siglaProvinciaDetenzioneEdit = QLineEdit()
        self.siglaProvinciaDetenzioneEdit.setMaximumWidth(60)
        self.tipoViaDetenzioneEdit = QLineEdit()
        self.tipoViaDetenzioneEdit.setMaximumWidth(100)
        self.viaDetenzioneEdit = QLineEdit()
        self.civicoDetenzioneEdit = QLineEdit()
        self.civicoDetenzioneEdit.setMaximumWidth(80)

        # Documento identità
        self.tipoDocumentoEdit = QLineEdit()
        self.numeroDocumentoEdit = QLineEdit()

        # Sostituzione per la data di rilascio documento
        self.dataRilascioDocumentoEdit = DateInputWidget()
        self.dataRilascioDocumentoEdit.setDisplayFormat("dd/MM/yyyy")

        self.enteRilascioDocumentoEdit = QLineEdit()

        # Converto comuneEnteRilascioDocumentoEdit da QLineEdit a QComboBox
        self.comuneEnteRilascioDocumentoCombo = QComboBox()
        self.comuneEnteRilascioDocumentoCombo.setEditable(True)
        self.comuneEnteRilascioDocumentoCombo.addItems(comuni)
        self.comuneEnteRilascioDocumentoCombo.setCurrentIndex(-1)
        self.comuneEnteRilascioDocumentoCombo.clearEditText()

        completer_ente_rilascio = QCompleter(comuni)
        completer_ente_rilascio.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneEnteRilascioDocumentoCombo.setCompleter(completer_ente_rilascio)

    def create_license_group(self):
        """Crea il gruppo per licenza e fascicolo"""
        group_license = QGroupBox("Licenza e Fascicolo")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Fascicolo Personale:"), 0, 0)
        grid.addWidget(self.fascicoloPersonaleEdit, 0, 1)
        grid.addWidget(QLabel("Tipologia Titolo:"), 0, 2)
        grid.addWidget(self.tipologiaTitoloEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Ente Rilascio:"), 1, 0)
        grid.addWidget(self.enteRilascioEdit, 1, 1)
        grid.addWidget(QLabel("Provincia Ente:"), 1, 2)
        grid.addWidget(self.provinciaEnteRilascioCombo, 1, 3)  # Uso della ComboBox anziché LineEdit

        # Riga 3
        grid.addWidget(QLabel("Data Rilascio:"), 2, 0)
        grid.addWidget(self.dataRilascioEdit, 2, 1)
        grid.addWidget(QLabel("Numero Porto Armi:"), 2, 2)
        grid.addWidget(self.numeroPortoArmiEdit, 2, 3)

        group_license.setLayout(grid)
        return group_license

    def create_detention_group(self):
        """Crea il gruppo per il luogo di detenzione"""
        group_detention = QGroupBox("Luogo di Detenzione")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Tipo Luogo:"), 0, 0)
        grid.addWidget(self.tipoLuogoDetenzioneEdit, 0, 1)
        grid.addWidget(QLabel("Comune:"), 0, 2)
        grid.addWidget(self.comuneDetenzioneCombo, 0, 3)  # Uso della ComboBox anziché LineEdit

        # Riga 2
        grid.addWidget(QLabel("Provincia:"), 1, 0)
        grid.addWidget(self.siglaProvinciaDetenzioneEdit, 1, 1)
        grid.addWidget(QLabel("Tipo Via:"), 1, 2)
        grid.addWidget(self.tipoViaDetenzioneEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Via:"), 2, 0)
        grid.addWidget(self.viaDetenzioneEdit, 2, 1, 1, 2)
        grid.addWidget(QLabel("Civico:"), 2, 3)
        grid.addWidget(self.civicoDetenzioneEdit, 2, 4)

        group_detention.setLayout(grid)
        return group_detention

    def create_document_group(self):
        """Crea il gruppo per il documento di identità"""
        group_document = QGroupBox("Documento di Identità")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Tipo Documento:"), 0, 0)
        grid.addWidget(self.tipoDocumentoEdit, 0, 1)
        grid.addWidget(QLabel("Numero:"), 0, 2)
        grid.addWidget(self.numeroDocumentoEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Data Rilascio:"), 1, 0)
        grid.addWidget(self.dataRilascioDocumentoEdit, 1, 1)
        grid.addWidget(QLabel("Ente Rilascio:"), 1, 2)
        grid.addWidget(self.enteRilascioDocumentoEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Comune Ente:"), 2, 0)
        grid.addWidget(self.comuneEnteRilascioDocumentoCombo, 2, 1, 1, 3)  # Uso della ComboBox anziché LineEdit

        group_document.setLayout(grid)
        return group_document

    def create_armi_tab(self):
        """Crea la tab per le armi associate"""
        self.tab_armi = QWidget()
        main_layout = QVBoxLayout()

        # Creazione tabella armi
        group_armi = QGroupBox("Armi del Detentore")
        table_layout = QVBoxLayout()

        self.armiTable = QTableWidget()
        self.armiTable.setColumnCount(3)
        self.armiTable.setHorizontalHeaderLabels(["Marca", "Modello", "Matricola"])
        self.armiTable.horizontalHeader().setStretchLastSection(True)
        self.armiTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.armiTable.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addWidget(self.armiTable)
        group_armi.setLayout(table_layout)

        # Pulsanti per gestire le armi
        btn_layout = QHBoxLayout()
        self.btnInserisciArma = QPushButton("Inserisci Arma")
        self.btnInserisciArma.setMinimumWidth(140)
        self.btnModificaArma = QPushButton("Modifica Arma")
        self.btnModificaArma.setMinimumWidth(140)
        self.btnCancellaArma = QPushButton("Cancella Arma")
        self.btnCancellaArma.setMinimumWidth(140)

        btn_layout.addWidget(self.btnInserisciArma)
        btn_layout.addWidget(self.btnModificaArma)
        btn_layout.addWidget(self.btnCancellaArma)
        btn_layout.addStretch(1)

        main_layout.addWidget(group_armi)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)

        self.tab_armi.setLayout(main_layout)

    def create_main_buttons(self):
        """Crea i pulsanti principali"""
        self.button_layout = QHBoxLayout()

        self.btnSaveDetentore = QPushButton("Salva Detentore")
        self.btnSaveDetentore.setMinimumWidth(140)
        self.btnUpdateDetentore = QPushButton("Aggiorna Detentore")
        self.btnUpdateDetentore.setMinimumWidth(140)
        self.btnDeleteDetentore = QPushButton("Elimina Detentore")
        self.btnDeleteDetentore.setMinimumWidth(140)

        self.button_layout.addWidget(self.btnSaveDetentore)
        self.button_layout.addWidget(self.btnUpdateDetentore)
        self.button_layout.addWidget(self.btnDeleteDetentore)
        self.button_layout.addStretch(1)

    def connect_signals(self):
        """Collega i segnali agli slot"""
        # Segnali per i pulsanti principali
        self.btnSaveDetentore.clicked.connect(self.save_detentore)
        self.btnUpdateDetentore.clicked.connect(self.save_detentore)
        self.btnDeleteDetentore.clicked.connect(self.delete_detentore)

        # Segnali per i pulsanti delle armi
        self.btnInserisciArma.clicked.connect(self.inserisci_arma)
        self.btnModificaArma.clicked.connect(self.modifica_arma_selected)
        self.btnCancellaArma.clicked.connect(self.cancella_arma)

        # Segnali per gli altri controlli
        self.luogoNascitaCombo.lineEdit().editingFinished.connect(self.update_sigla_provincia_nascita)
        self.comuneResidenzaCombo.lineEdit().editingFinished.connect(self.update_sigla_provincia_residenza)

        # Nuovo segnale per il comune di detenzione
        self.comuneDetenzioneCombo.lineEdit().editingFinished.connect(self.update_sigla_provincia_detenzione)

        self.btnCalcolaCF.clicked.connect(self.calcola_codice_fiscale)

        # Double click su tabella
        self.armiTable.cellDoubleClicked.connect(self.modifica_arma)

    def populate_fields(self, data):
        """Popola i campi con i dati esistenti"""
        self.nomeEdit.setText(data.get('nome', ''))
        self.cognomeEdit.setText(data.get('cognome', ''))

        # Imposta la data di nascita con il nuovo widget
        if data.get('dataNascita'):
            from PyQt5.QtCore import QDate
            self.dataNascitaEdit.setDate(QDate.fromString(data.get('dataNascita'), "dd/MM/yyyy"))

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

        # Aggiornamento per la provincia ente rilascio con combobox
        if data.get('provinciaEnteRilascio'):
            index = self.provinciaEnteRilascioCombo.findText(data.get('provinciaEnteRilascio'), Qt.MatchFixedString)
            if index >= 0:
                self.provinciaEnteRilascioCombo.setCurrentIndex(index)
            else:
                self.provinciaEnteRilascioCombo.setEditText(data.get('provinciaEnteRilascio'))

        # Imposta le altre date con i nuovi widget
        if data.get('dataRilascio'):
            from PyQt5.QtCore import QDate
            self.dataRilascioEdit.setDate(QDate.fromString(data.get('dataRilascio'), "dd/MM/yyyy"))

        self.numeroPortoArmiEdit.setText(data.get('numeroPortoArmi', ''))
        self.tipoLuogoDetenzioneEdit.setText(data.get('tipoLuogoDetenzione', ''))

        # Per comuneDetenzione ora utilizziamo una QComboBox
        if data.get('comuneDetenzione'):
            index = self.comuneDetenzioneCombo.findText(data.get('comuneDetenzione'), Qt.MatchFixedString)
            if index >= 0:
                self.comuneDetenzioneCombo.setCurrentIndex(index)
            else:
                self.comuneDetenzioneCombo.setEditText(data.get('comuneDetenzione'))

        self.siglaProvinciaDetenzioneEdit.setText(data.get('siglaProvinciaDetenzione', ''))
        self.tipoViaDetenzioneEdit.setText(data.get('tipoViaDetenzione', ''))
        self.viaDetenzioneEdit.setText(data.get('viaDetenzione', ''))
        self.civicoDetenzioneEdit.setText(data.get('civicoDetenzione', ''))
        self.tipoDocumentoEdit.setText(data.get('tipoDocumento', ''))
        self.numeroDocumentoEdit.setText(data.get('numeroDocumento', ''))

        if data.get('dataRilascioDocumento'):
            from PyQt5.QtCore import QDate
            self.dataRilascioDocumentoEdit.setDate(QDate.fromString(data.get('dataRilascioDocumento'), "dd/MM/yyyy"))

        self.enteRilascioDocumentoEdit.setText(data.get('enteRilascioDocumento', ''))

        # Per comuneEnteRilascioDocumento ora utilizziamo una QComboBox
        if data.get('comuneEnteRilascioDocumento'):
            index = self.comuneEnteRilascioDocumentoCombo.findText(data.get('comuneEnteRilascioDocumento'),
                                                                   Qt.MatchFixedString)
            if index >= 0:
                self.comuneEnteRilascioDocumentoCombo.setCurrentIndex(index)
            else:
                self.comuneEnteRilascioDocumentoCombo.setEditText(data.get('comuneEnteRilascioDocumento'))

    def save_detentore(self):
        """Salva o aggiorna i dati del detentore"""
        print("Salvataggio record Detentore in corso...")
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()

        # Raccolta dati dai campi
        nome = self.nomeEdit.text()
        cognome = self.cognomeEdit.text()
        dataNascita = self.dataNascitaEdit.text()
        luogoNascita = self.luogoNascitaCombo.currentText()
        siglaProvinciaNascita = self.siglaProvinciaNascitaEdit.text()
        sesso = self.sessoEdit.text()
        codiceFiscale = self.codiceFiscaleEdit.text()
        comuneResidenza = self.comuneResidenzaCombo.currentText()
        siglaProvinciaResidenza = self.siglaProvinciaResidenzaEdit.text()
        tipoVia = self.tipoViaEdit.text()
        via = self.viaEdit.text()
        civico = self.civicoEdit.text()
        telefono = self.telefonoEdit.text()
        fascicoloPersonale = self.fascicoloPersonaleEdit.text()
        tipologiaTitolo = self.tipologiaTitoloEdit.text()
        enteRilascio = self.enteRilascioEdit.text()
        provinciaEnteRilascio = self.provinciaEnteRilascioCombo.currentText()  # Legge dalla ComboBox
        dataRilascio = self.dataRilascioEdit.text()
        numeroPortoArmi = self.numeroPortoArmiEdit.text()
        tipoLuogoDetenzione = self.tipoLuogoDetenzioneEdit.text()
        comuneDetenzione = self.comuneDetenzioneCombo.currentText()
        siglaProvinciaDetenzione = self.siglaProvinciaDetenzioneEdit.text()
        tipoViaDetenzione = self.tipoViaDetenzioneEdit.text()
        viaDetenzione = self.viaDetenzioneEdit.text()
        civicoDetenzione = self.civicoDetenzioneEdit.text()
        tipoDocumento = self.tipoDocumentoEdit.text()
        numeroDocumento = self.numeroDocumentoEdit.text()
        dataRilascioDocumento = self.dataRilascioDocumentoEdit.text()
        enteRilascioDocumento = self.enteRilascioDocumentoEdit.text()
        comuneEnteRilascioDocumento = self.comuneEnteRilascioDocumentoCombo.currentText()

        try:
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
                    nome, cognome, fascicoloPersonale, dataNascita, luogoNascita, siglaProvinciaNascita, sesso,
                    codiceFiscale,
                    comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono, tipologiaTitolo,
                    enteRilascio,
                    provinciaEnteRilascio, dataRilascio, numeroPortoArmi, tipoLuogoDetenzione, comuneDetenzione,
                    siglaProvinciaDetenzione,
                    tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento,
                    dataRilascioDocumento,
                    enteRilascioDocumento, comuneEnteRilascioDocumento, self.detentore_data.get('id')))

                QMessageBox.information(self, "Successo", "Detentore aggiornato con successo!")
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
                    nome, cognome, fascicoloPersonale, dataNascita, luogoNascita, siglaProvinciaNascita, sesso,
                    codiceFiscale,
                    comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono, tipologiaTitolo,
                    enteRilascio,
                    provinciaEnteRilascio, dataRilascio, numeroPortoArmi, tipoLuogoDetenzione, comuneDetenzione,
                    siglaProvinciaDetenzione,
                    tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento,
                    dataRilascioDocumento,
                    enteRilascioDocumento, comuneEnteRilascioDocumento))

                QMessageBox.information(self, "Successo", "Nuovo detentore salvato con successo!")

            conn.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante il salvataggio: {str(e)}")
        finally:
            conn.close()

    def delete_detentore(self):
        """Elimina il detentore dal database"""
        if not self.detentore_data or not self.detentore_data.get('id'):
            QMessageBox.warning(self, "Attenzione", "Nessun detentore da eliminare.")
            return

        # Conferma eliminazione
        reply = QMessageBox.question(self, "Conferma eliminazione",
                                     "Sei sicuro di voler eliminare questo detentore?\nTutte le armi associate verranno eliminate.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()

                # Elimina prima le armi associate
                cursor.execute("DELETE FROM armi WHERE ID_Detentore = ?", (self.detentore_data.get('id'),))

                # Poi elimina il detentore
                cursor.execute("DELETE FROM detentori WHERE ID_Detentore = ?", (self.detentore_data.get('id'),))

                conn.commit()
                QMessageBox.information(self, "Successo", "Detentore e armi associate eliminati con successo!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante l'eliminazione: {str(e)}")
            finally:
                conn.close()

    def modifica_arma_selected(self):
        """Modifica l'arma selezionata nella tabella"""
        row = self.armiTable.currentRow()
        if row >= 0:
            self.modifica_arma(row, 0)
        else:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un'arma da modificare.")

    def modifica_arma(self, row, column):
        """Apre la finestra di dialogo per modificare un'arma"""
        from PyQt5.QtWidgets import QDialog

        # Recupera l'ID dell'arma dal primo item della riga
        id_item = self.armiTable.item(row, 0)
        if id_item:
            arma_id = id_item.data(Qt.UserRole)

            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
                row_data = cursor.fetchone()
                conn.close()

                if row_data:
                    columns = ["ID_ArmaDetenuta", "ID_Detentore", "TipoArma", "MarcaArma", "ModelloArma",
                               "TipologiaArma",
                               "Matricola", "CalibroArma", "MatricolaCanna", "LunghezzaCanna", "NumeroCanne",
                               "ArmaLungaCorta", "TipoCanna", "CategoriaArma", "FunzionamentoArma", "CaricamentoArma",
                               "PunzoniArma", "StatoProduzioneArma", "ExOrdDem", "TipoMunizioni", "QuantitaMunizioni",
                               "TipoBossolo", "TipoCedente", "NoteArma", "CognomeCedente", "NomeCedente",
                               "DataNascitaCedente", "LuogoNascitaCedente", "SiglaProvinciaResidenzaCedente",
                               "ComuneResidenzaCedente", "SiglaProvinciaNascitaCedente", "TipoViaResidenzaCedente",
                               "IndirizzoResidenzaCedente", "CivicoResidenzaCedente", "TelefonoCedente"]

                    arma_data = dict(zip(columns, row_data))

                    from ArmiDialog import ArmaDialog
                    det_id = self.detentore_data.get('id') if self.detentore_data else None
                    dialog = ArmaDialog(arma_data=arma_data, detentore_id=det_id)
                    if dialog.exec_() == QDialog.Accepted:
                        self.carica_armi()

            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante il caricamento dell'arma: {str(e)}")

    def carica_armi(self):
        """Carica le armi del detentore nella tabella"""
        if not self.detentore_data or not self.detentore_data.get('id'):
            self.armiTable.setRowCount(0)
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            det_id = self.detentore_data.get('id')
            cursor.execute("""
                SELECT ID_ArmaDetenuta, MarcaArma, ModelloArma, Matricola 
                FROM armi 
                WHERE ID_Detentore = ?
                ORDER BY MarcaArma, ModelloArma
            """, (det_id,))

            rows = cursor.fetchall()

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

            # Adatta le dimensioni delle colonne al contenuto
            self.armiTable.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento delle armi: {str(e)}")
        finally:
            conn.close()

    def inserisci_arma(self):
        """Inserisce una nuova arma per il detentore"""
        if not self.detentore_data or not self.detentore_data.get('id'):
            QMessageBox.warning(self, "Attenzione",
                                "È necessario salvare il detentore prima di poter inserire un'arma.")
            return

        from ArmiDialog import ArmaDialog
        det_id = self.detentore_data.get('id')
        dialog = ArmaDialog(arma_data=None, detentore_id=det_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carica_armi()

    def cancella_arma(self):
        """Elimina l'arma selezionata"""
        row = self.armiTable.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un'arma da eliminare.")
            return

        # Recupera l'ID dell'arma dal primo item della riga
        item = self.armiTable.item(row, 0)
        if item is None:
            return

        arma_id = item.data(Qt.UserRole)

        # Conferma eliminazione
        reply = QMessageBox.question(self, "Conferma eliminazione",
                                     "Sei sicuro di voler eliminare questa arma?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
                conn.commit()
                conn.close()
                # Ricarica la tabella
                self.carica_armi()
                QMessageBox.information(self, "Successo", "Arma eliminata con successo!")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione dell'arma: {str(e)}")

    def update_sigla_provincia_nascita(self):
        """Aggiorna la sigla provincia di nascita in base al comune selezionato"""
        comune = self.luogoNascitaCombo.currentText()
        if not comune:
            self.siglaProvinciaNascitaEdit.clear()
            return

        sigla = get_sigla_provincia(comune)
        self.siglaProvinciaNascitaEdit.setText(sigla)

    def update_sigla_provincia_residenza(self):
        """Aggiorna la sigla provincia di residenza in base al comune selezionato"""
        comune = self.comuneResidenzaCombo.currentText()
        if not comune:
            self.siglaProvinciaResidenzaEdit.clear()
            return

        sigla = get_sigla_provincia(comune)
        self.siglaProvinciaResidenzaEdit.setText(sigla)

    def update_sigla_provincia_detenzione(self):
        """Aggiorna la sigla provincia di detenzione in base al comune selezionato"""
        comune = self.comuneDetenzioneCombo.currentText()
        if not comune:
            self.siglaProvinciaDetenzioneEdit.clear()
            return

        sigla = get_sigla_provincia(comune)
        self.siglaProvinciaDetenzioneEdit.setText(sigla)

    def calcola_codice_fiscale(self):
        """Calcola il codice fiscale in base ai dati inseriti"""
        from Utility import compute_codice_fiscale

        # Recupera i dati necessari
        nome = self.nomeEdit.text().strip()
        cognome = self.cognomeEdit.text().strip()
        data_nascita = self.dataNascitaEdit.text().strip()  # Usa il metodo text() del widget personalizzato
        sesso = self.sessoEdit.text().strip()
        comune_nascita = self.luogoNascitaCombo.currentText().strip()

        if not (nome and cognome and data_nascita and sesso and comune_nascita):
            QMessageBox.warning(self, "Dati mancanti",
                                "Inserisci nome, cognome, data di nascita, sesso e comune di nascita.")
            return

        try:
            cf = compute_codice_fiscale(nome, cognome, data_nascita, sesso, comune_nascita)
            self.codiceFiscaleEdit.setText(cf)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile calcolare il codice fiscale:\n{e}")


def load_comuni():
    """Carica la lista dei comuni dal database"""
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

def load_province():
    """Carica la lista delle province dal database"""
    try:
        conn = sqlite3.connect("gestione_armi.db")
        cursor = conn.cursor()
        cursor.execute('SELECT C15 FROM province')
        rows = cursor.fetchall()
        conn.close()
        # Converte in maiuscolo
        return [row[0].upper() for row in rows if row[0]]
    except Exception as e:
        print("Errore nel caricamento delle province:", e)
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