import sqlite3
import threading
from datetime import datetime
import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QGroupBox,
    QListWidget, QTabWidget, QWidget, QHBoxLayout, QListWidgetItem, QComboBox,
    QCompleter, QTableWidget, QGridLayout, QLabel, QScrollArea, QSizePolicy,
    QMessageBox, QHeaderView, QTableWidgetItem, QFileDialog
)
from docxtpl import DocxTemplate
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QStringListModel
from PyQt5.QtWidgets import QComboBox, QCompleter
from Utility import get_comuni, get_province
from PyQt5.QtCore import Qt
from Utility import get_sigla_provincia, DateInputWidget
from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog #
from Utility import UpperCaseLineEdit
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
        self.nomeEdit = UpperCaseLineEdit()
        self.cognomeEdit = UpperCaseLineEdit()

        # Sostituisci QLineEdit con DateInputWidget per la data di nascita
        self.dataNascitaEdit = DateInputWidget()
        self.dataNascitaEdit.setDisplayFormat("dd/MM/yyyy")

        # Combo per il luogo di nascita
        self.luogoNascitaCombo = FilterableComboBox()
        comuni = get_comuni()
        self.luogoNascitaCombo.setItems(comuni)
        self.luogoNascitaCombo.setCurrentIndex(-1)
        self.luogoNascitaCombo.clearEditText()


        self.siglaProvinciaNascitaEdit = UpperCaseLineEdit()
        self.siglaProvinciaNascitaEdit.setMaximumWidth(60)
        self.sessoEdit = UpperCaseLineEdit()
        self.sessoEdit.setMaximumWidth(60)
        self.codiceFiscaleEdit = UpperCaseLineEdit()
        self.btnCalcolaCF = QPushButton("Calcola CF")
        self.btnCalcolaCF.setMaximumWidth(100)

    def create_contact_widgets(self):
        """Crea i widget per i contatti"""
        self.comuneResidenzaCombo = FilterableComboBox()
        from Utility import get_comuni
        comuni = get_comuni()
        self.comuneResidenzaCombo.setItems(comuni)
        self.comuneResidenzaCombo.setCurrentIndex(-1)
        self.comuneResidenzaCombo.clearEditText()

        completer_residenza = QCompleter(comuni)
        completer_residenza.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneResidenzaCombo.setCompleter(completer_residenza)

        self.siglaProvinciaResidenzaEdit = UpperCaseLineEdit()
        self.siglaProvinciaResidenzaEdit.setMaximumWidth(60)
        self.tipoViaEdit = UpperCaseLineEdit()
        self.tipoViaEdit.setMaximumWidth(100)
        self.viaEdit = UpperCaseLineEdit()
        self.civicoEdit = UpperCaseLineEdit()
        self.civicoEdit.setMaximumWidth(80)
        self.telefonoEdit = UpperCaseLineEdit()

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
        self.fascicoloPersonaleEdit = UpperCaseLineEdit()
        self.tipologiaTitoloEdit = UpperCaseLineEdit()

        # Ente rilascio
        self.enteRilascioEdit = UpperCaseLineEdit()

        # Combobox province per ente rilascio
        self.provinciaEnteRilascioCombo = QComboBox()
        self.provinciaEnteRilascioCombo.setEditable(True)
        province = get_province()
        self.provinciaEnteRilascioCombo.addItems(province)
        self.provinciaEnteRilascioCombo.setCurrentIndex(-1)
        self.provinciaEnteRilascioCombo.clearEditText()
        completer_provincia = QCompleter(province)
        completer_provincia.setCaseSensitivity(Qt.CaseInsensitive)
        self.provinciaEnteRilascioCombo.setCompleter(completer_provincia)

        # Sostituzione per la data di rilascio
        self.dataRilascioEdit = DateInputWidget()
        self.dataRilascioEdit.setDisplayFormat("dd/MM/yyyy")

        self.numeroPortoArmiEdit = UpperCaseLineEdit()

        # Luogo detenzione
        self.tipoLuogoDetenzioneEdit = UpperCaseLineEdit()

        # Converto comuneDetenzioneEdit da QLineEdit a QComboBox
        self.comuneDetenzioneCombo = QComboBox()
        self.comuneDetenzioneCombo.setEditable(True)
        comuni = get_comuni()
        self.comuneDetenzioneCombo.addItems(comuni)
        self.comuneDetenzioneCombo.setCurrentIndex(-1)
        self.comuneDetenzioneCombo.clearEditText()

        completer_detenzione = QCompleter(comuni)
        completer_detenzione.setCaseSensitivity(Qt.CaseInsensitive)
        self.comuneDetenzioneCombo.setCompleter(completer_detenzione)

        self.siglaProvinciaDetenzioneEdit = UpperCaseLineEdit()
        self.siglaProvinciaDetenzioneEdit.setMaximumWidth(60)
        self.tipoViaDetenzioneEdit = UpperCaseLineEdit()
        self.tipoViaDetenzioneEdit.setMaximumWidth(100)
        self.viaDetenzioneEdit = UpperCaseLineEdit()
        self.civicoDetenzioneEdit = UpperCaseLineEdit()
        self.civicoDetenzioneEdit.setMaximumWidth(80)

        # Documento identità
        self.tipoDocumentoEdit = UpperCaseLineEdit()
        self.numeroDocumentoEdit = UpperCaseLineEdit()

        # Sostituzione per la data di rilascio documento
        self.dataRilascioDocumentoEdit = DateInputWidget()
        self.dataRilascioDocumentoEdit.setDisplayFormat("dd/MM/yyyy")

        self.enteRilascioDocumentoEdit = UpperCaseLineEdit()

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

        # Nuovo pulsante per la stampa della denuncia
        self.btnStampaDenuncia = QPushButton("Stampa Denuncia")
        self.btnStampaDenuncia.setMinimumWidth(140)
        self.btnStampaDenuncia.setIcon(QIcon.fromTheme("document-print"))

        btn_layout.addWidget(self.btnInserisciArma)
        btn_layout.addWidget(self.btnModificaArma)
        btn_layout.addWidget(self.btnCancellaArma)
        btn_layout.addWidget(self.btnStampaDenuncia)  # Aggiunto il nuovo pulsante
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
        self.btnStampaDenuncia.clicked.connect(self.stampa_denuncia_armi)  # Nuovo collegamento

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
        """Salva o aggiorna i dati del detentore utilizzando la connessione persistente fornita dal DatabaseManager."""
        print("Salvataggio record Detentore in corso...")
        from Detentori import DatabaseManager  # Assicurati che l'import sia corretto
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
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
                    codiceFiscale, comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono,
                    tipologiaTitolo, enteRilascio, provinciaEnteRilascio, dataRilascio, numeroPortoArmi,
                    tipoLuogoDetenzione, comuneDetenzione, siglaProvinciaDetenzione,
                    tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento,
                    dataRilascioDocumento, enteRilascioDocumento, comuneEnteRilascioDocumento,
                    self.detentore_data.get('id')
                ))

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
                    codiceFiscale, comuneResidenza, siglaProvinciaResidenza, tipoVia, via, civico, telefono,
                    tipologiaTitolo, enteRilascio, provinciaEnteRilascio, dataRilascio, numeroPortoArmi,
                    tipoLuogoDetenzione, comuneDetenzione, siglaProvinciaDetenzione,
                    tipoViaDetenzione, viaDetenzione, civicoDetenzione, tipoDocumento, numeroDocumento,
                    dataRilascioDocumento, enteRilascioDocumento, comuneEnteRilascioDocumento
                ))

                QMessageBox.information(self, "Successo", "Nuovo detentore salvato con successo!")

            conn.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante il salvataggio: {str(e)}")
            # Nel caso di errori, potresti voler effettuare un rollback
            conn.rollback()

        # Non chiudiamo qui la connessione perché la gestiamo centralmente

    def delete_detentore(self):
        """Elimina il detentore dal database"""
        if not self.detentore_data or not self.detentore_data.get('id'):
            QMessageBox.warning(self, "Attenzione", "Nessun detentore da eliminare.")
            return

        # Conferma eliminazione
        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questo detentore?\nTutte le armi associate verranno eliminate.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Importa DatabaseManager dal file Detentori.py
                from Detentori import DatabaseManager
                db_manager = DatabaseManager()
                conn = db_manager.get_connection()
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
            # Non chiudiamo la connessione qui per mantenere la connessione persistente gestita centralmente

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
                # Importa DatabaseManager dal file in cui è definito (ad es. Detentori.py)
                from Detentori import DatabaseManager
                db_manager = DatabaseManager()
                conn = db_manager.get_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
                row_data = cursor.fetchone()
                # Non chiudiamo la connessione qui; la gestione centralizzata si occuperà di chiuderla al termine dell'app

                if row_data:
                    columns = ["ID_ArmaDetenuta", "ID_Detentore", "TipoArma", "MarcaArma", "ModelloArma",
                               "TipologiaArma", "Matricola", "CalibroArma", "MatricolaCanna", "LunghezzaCanna",
                               "NumeroCanne",
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
            print("DEBUG - carica_armi: Nessun detentore selezionato")
            return

        try:
            # Importa il singleton DatabaseManager dal file Detentori.py
            from Detentori import DatabaseManager
            db_manager = DatabaseManager()
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            det_id = self.detentore_data.get('id')
            print(f"DEBUG - carica_armi: Caricamento armi per detentore ID={det_id}")

            cursor.execute("""
                SELECT ID_ArmaDetenuta, MarcaArma, ModelloArma, Matricola 
                FROM armi 
                WHERE ID_Detentore = ?
                ORDER BY MarcaArma, ModelloArma
            """, (det_id,))

            rows = cursor.fetchall()
            print(f"DEBUG - carica_armi: Trovate {len(rows)} armi")

            self.armiTable.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                id_arma = row[0]
                marca = row[1] if row[1] is not None else ""
                modello = row[2] if row[2] is not None else ""
                matricola = row[3] if row[3] is not None else ""

                print(
                    f"DEBUG - Arma {row_index + 1}: ID={id_arma}, Marca={marca}, Modello={modello}, Matricola={matricola}")

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
            print(f"ERRORE CRITICO nel caricamento delle armi: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento delle armi: {str(e)}")

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
        """Elimina l'arma selezionata con lo stesso processo di ArmaDialog.delete_arma()"""
        row = self.armiTable.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un'arma da eliminare.")
            return

        # Recupera l'ID dell'arma dal primo item della riga
        item = self.armiTable.item(row, 0)
        if item is None:
            return

        arma_id = item.data(Qt.UserRole)
        if not arma_id:
            QMessageBox.warning(self, "Attenzione", "Dati dell'arma non validi.")
            return

        detentore_id = self.detentore_data.get('id') if self.detentore_data else None
        if not detentore_id:
            QMessageBox.warning(self, "Attenzione", "Dati del detentore non validi.")
            return

        try:
            # Importa il DatabaseManager dal file Detentori.py
            from Detentori import DatabaseManager
            db_manager = DatabaseManager()
            conn = db_manager.get_connection()
            cursor = conn.cursor()

            # Recupera i dati dell'arma
            cursor.execute("""
                SELECT ID_ArmaDetenuta, TipoArma, MarcaArma, ModelloArma, Matricola, CalibroArma 
                FROM armi 
                WHERE ID_ArmaDetenuta = ?
            """, (arma_id,))
            arma_data = cursor.fetchone()

            if not arma_data:
                QMessageBox.warning(self, "Attenzione", "Arma non trovata nel database.")
                return

            # Prepara il dizionario con i dati dell'arma
            arma_dict = {
                'ID_ArmaDetenuta': arma_data[0],
                'TipoArma': arma_data[1],
                'MarcaArma': arma_data[2],
                'ModelloArma': arma_data[3],
                'Matricola': arma_data[4],
                'CalibroArma': arma_data[5]
            }

            # Conferma eliminazione
            reply = QMessageBox.question(
                self,
                "Conferma eliminazione",
                f"Sei sicuro di voler eliminare questa arma?\nMatricola: {arma_dict['Matricola']}\nMarca: {arma_dict['MarcaArma']}\nModello: {arma_dict['ModelloArma']}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Importa il dialogo per il motivo dell'eliminazione
                from ArmiDialog import DialogoMotivoEliminazione
                from PyQt5.QtWidgets import QDialog

                # Crea e mostra il dialogo per la motivazione
                dialogo_motivo = DialogoMotivoEliminazione(arma_dict, self)
                if dialogo_motivo.exec_() != QDialog.Accepted:
                    return  # L'utente ha annullato l'eliminazione

                # Ottieni il motivo completo formattato
                motivo_completo = dialogo_motivo.get_motivo_completo()

                # Recupera i dati del detentore (cedente)
                cursor.execute("""
                    SELECT Cognome, Nome, CodiceFiscale 
                    FROM detentori 
                    WHERE ID_Detentore = ?
                """, (detentore_id,))
                detentore_data = cursor.fetchone()

                # Ottieni la data corrente per il trasferimento
                from PyQt5.QtCore import QDate, QDateTime
                data_trasferimento = QDate.currentDate().toString("yyyy-MM-dd")
                timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

                # Registra l'eliminazione nella tabella trasferimenti
                cursor.execute("""
                    INSERT INTO trasferimenti 
                    (ID_Arma, ID_Detentore_Cedente, ID_Detentore_Ricevente, Data_Trasferimento, 
                     Motivo_Trasferimento, Note, Timestamp_Registrazione,
                     MarcaArma, ModelloArma, Matricola, CalibroArma, TipoArma,
                     Cedente_Cognome, Cedente_Nome, Cedente_CodiceFiscale)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    arma_id,  # ID_Arma
                    detentore_id,  # ID_Detentore_Cedente
                    -1,  # ID_Detentore_Ricevente (usiamo -1 come valore speciale per "eliminato")
                    data_trasferimento,  # Data_Trasferimento
                    "ELIMINAZIONE",  # Motivo_Trasferimento
                    motivo_completo,  # Note
                    timestamp,  # Timestamp_Registrazione
                    arma_dict['MarcaArma'],  # MarcaArma
                    arma_dict['ModelloArma'],  # ModelloArma
                    arma_dict['Matricola'],  # Matricola
                    arma_dict['CalibroArma'],  # CalibroArma
                    arma_dict['TipoArma'],  # TipoArma
                    detentore_data[0] if detentore_data else '',  # Cedente_Cognome
                    detentore_data[1] if detentore_data else '',  # Cedente_Nome
                    detentore_data[2] if detentore_data else ''  # Cedente_CodiceFiscale
                ))

                # Elimina l'arma dalla tabella armi
                cursor.execute("DELETE FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
                conn.commit()

                QMessageBox.information(
                    self,
                    "Eliminazione completata",
                    "L'arma è stata eliminata con successo.\nMotivo registrato nello storico."
                )

                # Ricarica la tabella delle armi
                self.carica_armi()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante l'eliminazione: {str(e)}")
            print(f"Errore durante l'eliminazione dell'arma: {e}")
            import traceback
            traceback.print_exc()
        # Non chiudiamo la connessione qui per mantenere la connessione persistente

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

        # Recupera i dati necessari dai campi di input
        nome = self.nomeEdit.text().strip()
        cognome = self.cognomeEdit.text().strip()
        data_nascita = self.dataNascitaEdit.text().strip()  # Usa il metodo text() del widget personalizzato
        sesso = self.sessoEdit.text().strip()
        comune_nascita = self.luogoNascitaCombo.currentText().strip()

        # Se uno dei campi essenziali non è stato compilato, mostra un warning
        if not (nome and cognome and data_nascita and sesso and comune_nascita):
            QMessageBox.warning(self, "Dati mancanti",
                                "Inserisci nome, cognome, data di nascita, sesso e comune di nascita.")
            return

        try:
            # Calcola il codice fiscale usando la funzione di utilità
            cf = compute_codice_fiscale(nome, cognome, data_nascita, sesso, comune_nascita)
            # Imposta il risultato nel widget dedicato
            self.codiceFiscaleEdit.setText(cf)
        except Exception as e:
            # Gestisce eventuali eccezioni mostrando un messaggio di errore
            QMessageBox.critical(self, "Errore", f"Impossibile calcolare il codice fiscale:\n{e}")

    def stampa_denuncia_armi(self):
        """Genera e salva una denuncia di detenzione armi usando DocxTemplate"""
        if not self.detentore_data or not self.detentore_data.get('id'):
            QMessageBox.warning(self, "Attenzione", "Nessun detentore selezionato.")
            return

        try:
            # Connessione al database
            with sqlite3.connect("gestione_armi.db") as conn:
                cursor = conn.cursor()
                detentore_id = self.detentore_data.get('id')

                # Recupera i dati del detentore
                cursor.execute("""
                    SELECT Cognome, Nome, CodiceFiscale, DataNascita, LuogoNascita, SiglaProvinciaNascita,
                          ComuneResidenza, SiglaProvinciaResidenza, TipoVia, Via, Civico, Telefono,
                          NumeroPortoArmi, DataRilascio, EnteRilascio
                    FROM detentori 
                    WHERE ID_Detentore = ?
                """, (detentore_id,))
                detentore = cursor.fetchone()

                if not detentore:
                    QMessageBox.warning(self, "Attenzione", "Detentore non trovato nel database.")
                    return

                # Recupera le armi raggruppate per categoria con tutti i dettagli aggiuntivi
                cursor.execute("""
                    SELECT CategoriaArma, TipoArma, MarcaArma, ModelloArma, Matricola, CalibroArma, 
                           CaricamentoArma, ArmaLungaCorta, DataAcquisto, NoteArma,
                           TipoCedente, CognomeCedente, NomeCedente, 
                           TipoCanna, MatricolaCanna, LunghezzaCanna, NumeroCanne,
                           TipoMunizioni, QuantitaMunizioni, TipoBossolo
                    FROM armi 
                    WHERE ID_Detentore = ?
                    ORDER BY CategoriaArma, TipoArma, MarcaArma, ModelloArma
                """, (detentore_id,))
                armi = cursor.fetchall()

                if not armi:
                    QMessageBox.warning(self, "Attenzione", "Nessuna arma trovata per questo detentore.")
                    return

                # Raggruppa le armi per categoria
                armi_by_categoria = {}
                for arma in armi:
                    categoria = arma[0] or "NON SPECIFICATA"
                    if categoria not in armi_by_categoria:
                        armi_by_categoria[categoria] = []
                    armi_by_categoria[categoria].append(arma)

                # Prepara i dati per il template
                armi_formattate = []
                contatore = 1

                for categoria, armi_in_categoria in armi_by_categoria.items():
                    for arma in armi_in_categoria:
                        armi_formattate.append({
                            'numero': contatore,
                            'categoria': categoria,
                            'tipo': arma[1] or "N/D",
                            'marca': arma[2] or "N/D",
                            'modello': arma[3] or "N/D",
                            'matricola': arma[4] or "N/D",
                            'calibro': arma[5] or "N/D",
                            'caricamento': arma[6] or "N/D",
                            'tipo_arma': arma[7] or "N/D",
                            'data_acquisto': arma[8] or "N/D",
                            'note': arma[9] or "",
                            'tipo_cedente': arma[10] or "N/D",
                            'cognome_cedente': arma[11] or "N/D",
                            'nome_cedente': arma[12] or "N/D",
                            'tipo_canna': arma[13] or "N/D",
                            'matricola_canna': arma[14] or "N/D",
                            'lunghezza_canna': arma[15] or "N/D",
                            'numero_canne': arma[16] or "N/D",
                            'tipo_munizioni': arma[17] or "N/D",
                            'quantita_munizioni': arma[18] or "N/D",
                            'tipo_bossolo': arma[19] or "N/D"
                        })
                        contatore += 1

                # Ottieni data per il documento
                data_corrente = datetime.now().strftime('%d/%m/%Y')
                ora_corrente = datetime.now().strftime('%H:%M')

                # Prepara il contesto per il template
                context = {
                    'data_documento': data_corrente,
                    'ora_documento': ora_corrente,
                    'cognome': detentore[0],
                    'nome': detentore[1],
                    'codice_fiscale': detentore[2],
                    'data_nascita': detentore[3],
                    'luogo_nascita': detentore[4],
                    'provincia_nascita': detentore[5],
                    'comune_residenza': detentore[6],
                    'provincia_residenza': detentore[7],
                    'tipo_via': detentore[8],
                    'via': detentore[9],
                    'civico': detentore[10],
                    'telefono': detentore[11] or "N/D",
                    'numero_porto_armi': detentore[12] or "N/D",
                    'data_rilascio': detentore[13] or "N/D",
                    'ente_rilascio': detentore[14] or "N/D",
                    'armi': armi_formattate,
                    'totale_armi': len(armi),
                    'categorie': [{'nome': cat, 'conteggio': len(armi_cat)} for cat, armi_cat in
                                  armi_by_categoria.items()]
                }

                # Definisci il percorso del template SENZA usare __file__
                current_dir = os.getcwd()  # Otteniamo la directory corrente
                template_path = os.path.join(current_dir, "templates", "denuncia_armi_template.docx")

                # Verifica se il template esiste
                if not os.path.exists(template_path):
                    # Prova a cercare il template in una sottodirectory dell'eseguibile
                    base_dir = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else current_dir
                    template_path = os.path.join(base_dir, "templates", "denuncia_armi_template.docx")

                    if not os.path.exists(template_path):
                        QMessageBox.critical(self, "Errore",
                                             f"Template non trovato in:\n{template_path}\n\nCreare una cartella 'templates' con il file template.")
                        return

                # Carica il template
                doc = DocxTemplate(template_path)

                # Rendering del documento
                doc.render(context)

                # Richiedi all'utente dove salvare il file
                nome_file_default = f"Denuncia_Armi_{detentore[0]}_{detentore[1]}_{data_corrente.replace('/', '_')}.docx"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Salva documento",
                    nome_file_default,
                    "Documenti Word (*.docx)"
                )

                if file_path:
                    doc.save(file_path)
                    QMessageBox.information(self, "Documento generato",
                                            f"Il documento è stato salvato con successo in:\n{file_path}")

                    # Chiedi all'utente se vuole aprire il documento
                    reply = QMessageBox.question(self, "Aprire documento?",
                                                 "Vuoi aprire il documento generato?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        # Apri il documento con l'applicazione predefinita
                        if os.name == 'nt':  # Windows
                            os.startfile(file_path)
                        elif os.name == 'posix':  # macOS o Linux
                            import subprocess
                            subprocess.call(
                                ('open', file_path) if sys.platform == 'darwin' else ('xdg-open', file_path))

        except Exception as e:
            QMessageBox.critical(self, "Errore",
                                 f"Si è verificato un errore durante la preparazione del documento: {str(e)}")
            print(f"Errore nella generazione del documento: {e}")
            import traceback
            traceback.print_exc()
class UpperCaseLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(UpperCaseLineEdit, self).__init__(*args, **kwargs)
        # Colleghiamo il segnale textChanged al metodo onTextChanged
        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, text):
        upper_text = text.upper()
        if text != upper_text:
            self.blockSignals(True)
            self.setText(upper_text)
            self.blockSignals(False)

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()  # Per evitare problemi in ambienti multi-thread

    def __new__(cls, db_path="gestione_armi.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._db_path = db_path
                cls._instance._connection = None
            return cls._instance

    def get_connection(self):
        """Restituisce la connessione attiva; la apre se non esiste già."""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self._db_path)
                # Imposta eventualmente alcune opzioni utili, ad es. l'uso di row_factory per accedere ai campi per nome
                self._connection.row_factory = sqlite3.Row
            except Exception as e:
                raise Exception(f"Errore durante l'apertura del database: {e}")
        return self._connection

    def close_connection(self):
        """Chiude la connessione, se esiste."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(self, query, params=()):
        """
        Esegue una query e restituisce il cursore.
        Ricorda di gestire il commit se stai modificando dati.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor
        except Exception as e:
            raise Exception(f"Errore durante l'esecuzione della query: {e}")

class FilterableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(FilterableComboBox, self).__init__(parent)
        self.setEditable(True)
        # Imposta un modello di stringhe
        self._model = QStringListModel()
        # Imposta un proxy per il filtraggio
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setSourceModel(self._model)
        # Imposta il completer basato sul proxy model
        self._completer = QCompleter(self._proxy_model, self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self._completer)
        # Collega l'evento per il filtraggio in tempo reale
        self.lineEdit().textEdited.connect(self._filterItems)

    def setItems(self, items):
        """Imposta gli elementi nella comboBox e nel modello del completer."""
        self.clear()
        self.addItems(items)
        self._model.setStringList(items)

    def _filterItems(self, text):
        """Aggiorna il filtro del proxy model in base al testo digitato."""
        self._proxy_model.setFilterFixedString(text)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = InserisciDetentoreDialog()
    dialog.exec_()