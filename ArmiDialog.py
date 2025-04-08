import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QGroupBox, QPushButton, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QSizePolicy, QComboBox, QMessageBox, QInputDialog
)
from Utility import convert_all_lineedits_to_uppercase
from TransferimentoDialog import TransferimentoDialog


class ArmaDialog(QDialog):
    def __init__(self, arma_data=None, detentore_id=None):
        """
        Se arma_data è None, si tratta di un nuovo inserimento.
        detentore_id è l'ID del detentore a cui l'arma appartiene.
        """
        super().__init__()
        self.arma_data = arma_data
        self.detentore_id = detentore_id

        # Configurazione iniziale della finestra
        self.setWindowTitle("Gestione Arma")
        self.setMinimumWidth(850)
        self.setMinimumHeight(600)

        # Creazione dei widget principali
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()

        # Popola i campi se sono stati forniti dati esistenti
        if arma_data:
            self.populate_fields(arma_data)

        # Converti tutto in maiuscolo
        convert_all_lineedits_to_uppercase(self)

    def _create_widgets(self):
        """Crea tutti i widget necessari"""
        # Tab 1: Dettagli Arma
        self._create_arma_tab()

        # Tab 2: Dati Cedente
        self._create_cedente_tab()

        # Pulsanti
        self.saveButton = QPushButton("Salva Arma")
        self.saveButton.setMinimumWidth(120)
        self.modifyButton = QPushButton("Modifica Arma")
        self.modifyButton.setMinimumWidth(120)
        self.deleteButton = QPushButton("Cancella Arma")
        self.deleteButton.setMinimumWidth(120)
        self.transferButton = QPushButton("Trasferisci Arma")
        self.transferButton.setMinimumWidth(120)

    def _create_arma_tab(self):
        """Crea la tab con i dettagli dell'arma"""
        self.tab_arma = QWidget()
        self.dataAcquistoEdit = QLineEdit()

        # Creazione dei campi di testo e combobox
        # Tipo Arma - ComboBox
        self.tipoArmaEdit = QComboBox()
        self.tipoArmaEdit.setEditable(True)
        self.initialize_tipo_arma_combo()

        # Marca Arma - ComboBox
        self.marcaArmaEdit = QComboBox()
        self.marcaArmaEdit.setEditable(True)
        self.load_marche_from_db()

        self.modelloArmaEdit = QLineEdit()
        self.tipologiaArmaEdit = QLineEdit()
        self.matricolaEdit = QLineEdit()
        self.calibroArmaEdit = QLineEdit()
        self.matricolaCannaEdit = QLineEdit()
        self.lunghezzaCannaEdit = QLineEdit()
        self.numeroCanneEdit = QLineEdit()

        # Arma Lunga/Corta - ComboBox
        self.armaLungaCortaEdit = QComboBox()
        self.armaLungaCortaEdit.setEditable(True)
        self.initialize_arma_lunga_corta_combo()

        self.tipoCannaEdit = QLineEdit()

        # Categoria Arma - ComboBox
        self.categoriaArmaEdit = QComboBox()
        self.categoriaArmaEdit.setEditable(True)
        self.initialize_categoria_arma_combo()

        # Funzionamento Arma - ComboBox
        self.funzionamentoArmaEdit = QComboBox()
        self.funzionamentoArmaEdit.setEditable(True)
        self.initialize_funzionamento_arma_combo()

        # Caricamento Arma - ComboBox
        self.caricamentoArmaEdit = QComboBox()
        self.caricamentoArmaEdit.setEditable(True)
        self.initialize_caricamento_arma_combo()

        self.punzoniArmaEdit = QLineEdit()
        self.statoProduzioneArmaEdit = QLineEdit()
        self.exOrdDemEdit = QLineEdit()
        self.tipoMunizioniEdit = QLineEdit()
        self.quantitaMunizioniEdit = QLineEdit()
        self.tipoBossoloEdit = QLineEdit()
        self.tipoCedenteEdit = QLineEdit()
        self.noteArmaEdit = QLineEdit()

        # Creazione dei gruppi di campi
        self.create_arma_identification_group()
        self.create_arma_technical_group()
        self.create_arma_classification_group()
        self.create_arma_munition_group()

        # Layout principale per la tab arma con scrolling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Aggiunta dei gruppi al layout
        scroll_layout.addWidget(self.group_identification)
        scroll_layout.addWidget(self.group_technical)
        scroll_layout.addWidget(self.group_classification)
        scroll_layout.addWidget(self.group_munition)

        # Note aggiuntive
        group_notes = QGroupBox("Note")
        notes_layout = QFormLayout()
        notes_layout.addRow("Note Arma:", self.noteArmaEdit)
        group_notes.setLayout(notes_layout)
        scroll_layout.addWidget(group_notes)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)

        # Layout principale della tab
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.tab_arma.setLayout(main_layout)

    def initialize_tipo_arma_combo(self):
        """Inizializza la combobox per il tipo di arma"""
        tipi_arma = [
            "PISTOLA",
            "FUCILE",
            "REVOLVER",
            "CARABINA",
            "FUCILE A POMPA",
            "MITRAGLIATRICE",
            "FUCILE D'ASSALTO",
            "FUCILE DI PRECISIONE",
            "ARMA BIANCA",
            "SHOTGUN",
            "PISTOLA MITRAGLIATRICE",
            "FUCILE A CANNA LISCIA"
        ]
        for tipo in tipi_arma:
            self.tipoArmaEdit.addItem(tipo)

    def initialize_arma_lunga_corta_combo(self):
        """Inizializza la combobox per arma lunga/corta"""
        tipi = ["ARMA LUNGA", "ARMA CORTA"]
        for tipo in tipi:
            self.armaLungaCortaEdit.addItem(tipo)

    def initialize_categoria_arma_combo(self):
        """Inizializza la combobox per la categoria dell'arma"""
        categorie = [
            "ARMA DA CACCIA",
            "USO SPORTIVO",
            "ARMA BIANCA",
            "ARMA DA COLLEZIONE",
            "DIFESA PERSONALE",
            "USO MILITARE",
            "USO CIVILE",
            "ARMA COMUNE",
            "ARMA SPORTIVA",
            "ARMA ANTICA"
        ]
        for categoria in categorie:
            self.categoriaArmaEdit.addItem(categoria)

    def initialize_funzionamento_arma_combo(self):
        """Inizializza la combobox per il funzionamento dell'arma"""
        funzionamenti = [
            "SEMIAUTOMATICO",
            "AUTOMATICO",
            "CARICAMENTO SINGOLO",
            "A ROTAZIONE",
            "A LEVA",
            "A POMPA",
            "A OTTURATORE GIREVOLE-SCORREVOLE",
            "A MASSA BATTENTE",
            "A CORTO RINCULO",
            "A CANNA BASCULANTE",
            "A RIPETIZIONE MANUALE"
        ]
        for funzionamento in funzionamenti:
            self.funzionamentoArmaEdit.addItem(funzionamento)

    def initialize_caricamento_arma_combo(self):
        """Inizializza la combobox per il caricamento dell'arma"""
        caricamenti = ["AVANCARICA", "RETROCARICA"]
        for caricamento in caricamenti:
            self.caricamentoArmaEdit.addItem(caricamento)

    def load_marche_from_db(self):
        """Carica le marche dal database nella combobox"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Assicuriamoci che la tabella esista
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marche_armi (
                    ID_MarcaArma INTEGER PRIMARY KEY AUTOINCREMENT,
                    NomeMarca TEXT NOT NULL UNIQUE,
                    StatoProduzione TEXT
                )
            """)
            conn.commit()

            cursor.execute("SELECT NomeMarca FROM marche_armi ORDER BY NomeMarca")
            marche = cursor.fetchall()

            self.marcaArmaEdit.clear()
            for marca in marche:
                self.marcaArmaEdit.addItem(marca[0])

        except Exception as e:
            print("Errore durante il caricamento delle marche:", e)
        finally:
            conn.close()

    def create_arma_identification_group(self):
        """Crea il gruppo per i dati identificativi dell'arma"""
        self.group_identification = QGroupBox("Dati Identificativi")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Tipo Arma:"), 0, 0)
        grid.addWidget(self.tipoArmaEdit, 0, 1)
        grid.addWidget(QLabel("Marca:"), 0, 2)
        grid.addWidget(self.marcaArmaEdit, 0, 3)
        grid.addWidget(QLabel("Data Acquisto:"), 0, 4)
        grid.addWidget(self.dataAcquistoEdit, 0, 5)  # Corretto: self.dataAcquistoEdit invece di self.DEdit

        # Riga 2
        grid.addWidget(QLabel("Modello:"), 1, 0)
        grid.addWidget(self.modelloArmaEdit, 1, 1)
        grid.addWidget(QLabel("Tipologia:"), 1, 2)
        grid.addWidget(self.tipologiaArmaEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Matricola:"), 2, 0)
        grid.addWidget(self.matricolaEdit, 2, 1)
        grid.addWidget(QLabel("Calibro:"), 2, 2)
        grid.addWidget(self.calibroArmaEdit, 2, 3)

        self.group_identification.setLayout(grid)

    def create_arma_technical_group(self):
        """Crea il gruppo per i dettagli tecnici dell'arma"""
        self.group_technical = QGroupBox("Dati Tecnici")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Matricola Canna:"), 0, 0)
        grid.addWidget(self.matricolaCannaEdit, 0, 1)
        grid.addWidget(QLabel("Lunghezza Canna:"), 0, 2)
        grid.addWidget(self.lunghezzaCannaEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Numero Canne:"), 1, 0)
        grid.addWidget(self.numeroCanneEdit, 1, 1)
        grid.addWidget(QLabel("Tipo Canna:"), 1, 2)
        grid.addWidget(self.tipoCannaEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Arma Lunga/Corta:"), 2, 0)
        grid.addWidget(self.armaLungaCortaEdit, 2, 1)
        grid.addWidget(QLabel("Punzoni:"), 2, 2)
        grid.addWidget(self.punzoniArmaEdit, 2, 3)

        self.group_technical.setLayout(grid)

    def create_arma_classification_group(self):
        """Crea il gruppo per la classificazione dell'arma"""
        self.group_classification = QGroupBox("Classificazione")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Categoria:"), 0, 0)
        grid.addWidget(self.categoriaArmaEdit, 0, 1)
        grid.addWidget(QLabel("Funzionamento:"), 0, 2)
        grid.addWidget(self.funzionamentoArmaEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Caricamento:"), 1, 0)
        grid.addWidget(self.caricamentoArmaEdit, 1, 1)
        grid.addWidget(QLabel("Stato Produzione:"), 1, 2)
        grid.addWidget(self.statoProduzioneArmaEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("ExOrdDem:"), 2, 0)
        grid.addWidget(self.exOrdDemEdit, 2, 1)
        grid.addWidget(QLabel("Tipo Cedente:"), 2, 2)
        grid.addWidget(self.tipoCedenteEdit, 2, 3)

        self.group_classification.setLayout(grid)

    def create_arma_munition_group(self):
        """Crea il gruppo per i dati sulle munizioni"""
        self.group_munition = QGroupBox("Munizioni")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Tipo Munizioni:"), 0, 0)
        grid.addWidget(self.tipoMunizioniEdit, 0, 1)
        grid.addWidget(QLabel("Quantità:"), 0, 2)
        grid.addWidget(self.quantitaMunizioniEdit, 0, 3)

        # Riga 2
        grid.addWidget(QLabel("Tipo Bossolo:"), 1, 0)
        grid.addWidget(self.tipoBossoloEdit, 1, 1)

        self.group_munition.setLayout(grid)

    def _create_cedente_tab(self):
        """Crea la tab con i dati del cedente"""
        self.tab_cedente = QWidget()

        # Creazione dei campi di testo
        self.cognomeCedenteEdit = QLineEdit()
        self.nomeCedenteEdit = QLineEdit()
        self.dataNascitaCedenteEdit = QLineEdit()
        self.luogoNascitaCedenteEdit = QLineEdit()
        self.siglaProvinciaResidenzaCedenteEdit = QLineEdit()
        self.comuneResidenzaCedenteEdit = QLineEdit()
        self.siglaProvinciaNascitaCedenteEdit = QLineEdit()
        self.tipoViaResidenzaCedenteEdit = QLineEdit()
        self.indirizzoResidenzaCedenteEdit = QLineEdit()
        self.civicoResidenzaCedenteEdit = QLineEdit()
        self.telefonoCedenteEdit = QLineEdit()

        # Creazione dei gruppi
        group_anagrafica = QGroupBox("Dati Anagrafici")
        grid_anagrafica = QGridLayout()

        # Riga 1
        grid_anagrafica.addWidget(QLabel("Cognome:"), 0, 0)
        grid_anagrafica.addWidget(self.cognomeCedenteEdit, 0, 1)
        grid_anagrafica.addWidget(QLabel("Nome:"), 0, 2)
        grid_anagrafica.addWidget(self.nomeCedenteEdit, 0, 3)

        # Riga 2
        grid_anagrafica.addWidget(QLabel("Data di Nascita:"), 1, 0)
        grid_anagrafica.addWidget(self.dataNascitaCedenteEdit, 1, 1)
        grid_anagrafica.addWidget(QLabel("Luogo di Nascita:"), 1, 2)
        grid_anagrafica.addWidget(self.luogoNascitaCedenteEdit, 1, 3)

        # Riga 3
        grid_anagrafica.addWidget(QLabel("Provincia di Nascita:"), 2, 0)
        grid_anagrafica.addWidget(self.siglaProvinciaNascitaCedenteEdit, 2, 1)
        grid_anagrafica.addWidget(QLabel("Telefono:"), 2, 2)
        grid_anagrafica.addWidget(self.telefonoCedenteEdit, 2, 3)

        group_anagrafica.setLayout(grid_anagrafica)

        group_residenza = QGroupBox("Dati Residenza")
        grid_residenza = QGridLayout()

        # Riga 1
        grid_residenza.addWidget(QLabel("Comune:"), 0, 0)
        grid_residenza.addWidget(self.comuneResidenzaCedenteEdit, 0, 1)
        grid_residenza.addWidget(QLabel("Provincia:"), 0, 2)
        grid_residenza.addWidget(self.siglaProvinciaResidenzaCedenteEdit, 0, 3)

        # Riga 2
        grid_residenza.addWidget(QLabel("Tipo Via:"), 1, 0)
        grid_residenza.addWidget(self.tipoViaResidenzaCedenteEdit, 1, 1)
        grid_residenza.addWidget(QLabel("Indirizzo:"), 1, 2)
        grid_residenza.addWidget(self.indirizzoResidenzaCedenteEdit, 1, 3)

        # Riga 3
        grid_residenza.addWidget(QLabel("Civico:"), 2, 0)
        grid_residenza.addWidget(self.civicoResidenzaCedenteEdit, 2, 1)

        group_residenza.setLayout(grid_residenza)

        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_anagrafica)
        main_layout.addWidget(group_residenza)
        main_layout.addStretch()
        self.tab_cedente.setLayout(main_layout)

    def _setup_layout(self):
        """Configura il layout principale"""
        main_layout = QVBoxLayout()

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tab_arma, "Arma")
        self.tab_widget.addTab(self.tab_cedente, "Cedente")

        # Layout pulsanti
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.saveButton)
        btn_layout.addWidget(self.modifyButton)
        btn_layout.addWidget(self.deleteButton)
        btn_layout.addWidget(self.transferButton)

        # Aggiungi tutto al layout principale
        main_layout.addWidget(self.tab_widget)
        main_layout.addSpacing(10)  # Spazio tra tabs e pulsanti
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Collega i segnali agli slot"""
        self.saveButton.clicked.connect(self.save_arma)
        self.modifyButton.clicked.connect(self.modify_arma)
        self.deleteButton.clicked.connect(self.delete_arma)
        self.transferButton.clicked.connect(self.transfer_arma)

        # Collegare il segnale della combobox marca
        self.marcaArmaEdit.currentIndexChanged.connect(self.on_marca_selected)
        # Collega il segnale quando l'utente finisce di modificare il testo
        self.marcaArmaEdit.editTextChanged.connect(self.on_marca_text_changed)

        # Assicurarsi che tutte le combobox convertano il testo in maiuscolo
        for combo in [self.tipoArmaEdit, self.marcaArmaEdit, self.armaLungaCortaEdit,
                      self.categoriaArmaEdit, self.funzionamentoArmaEdit, self.caricamentoArmaEdit]:
            combo.setEditable(True)
            combo.editTextChanged.connect(self.convert_combobox_text_to_uppercase)

    def convert_combobox_text_to_uppercase(self):
        """Converte il testo della combobox in maiuscolo"""
        sender = self.sender()
        if isinstance(sender, QComboBox):
            current_text = sender.currentText()
            upper_text = current_text.upper()
            if current_text != upper_text:
                sender.setEditText(upper_text)

    def on_marca_selected(self, index):
        """Gestisce la selezione di una marca dalla combobox"""
        if index >= 0:
            marca_selezionata = self.marcaArmaEdit.currentText()
            self.load_stato_produzione(marca_selezionata)

    def on_marca_text_changed(self, text):
        """Gestisce il cambio di testo nella combobox"""
        # Convertire il testo in maiuscolo
        upper_text = text.upper()
        if upper_text != text:
            self.marcaArmaEdit.setEditText(upper_text)
            return

        # Verifica se il testo è già presente nel database
        conn = None
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT StatoProduzione FROM marche_armi WHERE NomeMarca = ?", (upper_text,))
            result = cursor.fetchone()

            if result:
                # La marca esiste, carica lo stato produzione
                self.statoProduzioneArmaEdit.setText(result[0] if result[0] else "")
        except Exception as e:
            print("Errore nella verifica della marca:", e)
        finally:
            if conn:
                conn.close()

    def load_stato_produzione(self, marca):
        """Carica lo stato di produzione associato alla marca selezionata"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT StatoProduzione FROM marche_armi WHERE NomeMarca = ?", (marca,))
            result = cursor.fetchone()

            if result and result[0]:
                self.statoProduzioneArmaEdit.setText(result[0])
        except Exception as e:
            print("Errore nel caricamento dello stato di produzione:", e)
        finally:
            conn.close()

    def check_and_add_new_marca(self):
        """Verifica se la marca inserita esiste nel db e, se non esiste, chiede di aggiungerla"""
        marca_text = self.marcaArmaEdit.currentText().upper()

        if not marca_text:
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM marche_armi WHERE NomeMarca = ?", (marca_text,))
            count = cursor.fetchone()[0]

            if count == 0:
                # La marca non esiste, chiedi se aggiungerla
                reply = QMessageBox.question(
                    self,
                    'Nuova Marca',
                    f'La marca "{marca_text}" non esiste nel database. Vuoi aggiungerla?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # Chiedi lo stato di produzione
                    stato_produzione, ok = QInputDialog.getText(
                        self,
                        'Stato Produzione',
                        'Inserisci lo stato di produzione per questa marca:',
                        text=self.statoProduzioneArmaEdit.text().upper()
                    )

                    if ok:
                        stato_produzione = stato_produzione.upper()
                        # Aggiungi la nuova marca al database
                        cursor.execute(
                            "INSERT INTO marche_armi (NomeMarca, StatoProduzione) VALUES (?, ?)",
                            (marca_text, stato_produzione)
                        )
                        conn.commit()

                        # Aggiorna la combobox
                        self.load_marche_from_db()
                        # Imposta il valore corrente
                        index = self.marcaArmaEdit.findText(marca_text)
                        if index >= 0:
                            self.marcaArmaEdit.setCurrentIndex(index)
                        else:
                            self.marcaArmaEdit.setEditText(marca_text)

                        # Aggiorna lo stato di produzione
                        self.statoProduzioneArmaEdit.setText(stato_produzione)
                else:
                    # L'utente non vuole aggiungerla, lascia il testo ma non salvare nel database
                    pass
        except Exception as e:
            print("Errore durante il controllo/aggiunta della marca:", e)
        finally:
            conn.close()

    def populate_fields(self, data):
        """Popola i campi con i dati esistenti"""
        # Per i campi con combobox
        self.set_combobox_value(self.tipoArmaEdit, data.get('TipoArma', ''))
        self.set_combobox_value(self.marcaArmaEdit, data.get('MarcaArma', ''))
        self.set_combobox_value(self.armaLungaCortaEdit, data.get('ArmaLungaCorta', ''))
        self.set_combobox_value(self.categoriaArmaEdit, data.get('CategoriaArma', ''))
        self.set_combobox_value(self.funzionamentoArmaEdit, data.get('FunzionamentoArma', ''))
        self.set_combobox_value(self.caricamentoArmaEdit, data.get('CaricamentoArma', ''))

        # Per i campi con QLineEdit
        self.modelloArmaEdit.setText(data.get('ModelloArma', ''))
        self.tipologiaArmaEdit.setText(data.get('TipologiaArma', ''))
        self.matricolaEdit.setText(data.get('Matricola', ''))
        self.calibroArmaEdit.setText(data.get('CalibroArma', ''))
        self.matricolaCannaEdit.setText(data.get('MatricolaCanna', ''))
        self.lunghezzaCannaEdit.setText(data.get('LunghezzaCanna', ''))
        self.numeroCanneEdit.setText(data.get('NumeroCanne', ''))
        self.tipoCannaEdit.setText(data.get('TipoCanna', ''))
        self.punzoniArmaEdit.setText(data.get('PunzoniArma', ''))
        self.statoProduzioneArmaEdit.setText(data.get('StatoProduzioneArma', ''))
        self.exOrdDemEdit.setText(data.get('ExOrdDem', ''))
        self.tipoMunizioniEdit.setText(data.get('TipoMunizioni', ''))
        self.quantitaMunizioniEdit.setText(data.get('QuantitaMunizioni', ''))
        self.tipoBossoloEdit.setText(data.get('TipoBossolo', ''))
        self.tipoCedenteEdit.setText(data.get('TipoCedente', ''))
        self.noteArmaEdit.setText(data.get('NoteArma', ''))
        self.cognomeCedenteEdit.setText(data.get('CognomeCedente', ''))
        self.nomeCedenteEdit.setText(data.get('NomeCedente', ''))
        self.dataNascitaCedenteEdit.setText(data.get('DataNascitaCedente', ''))
        self.luogoNascitaCedenteEdit.setText(data.get('LuogoNascitaCedente', ''))
        self.siglaProvinciaResidenzaCedenteEdit.setText(data.get('SiglaProvinciaResidenzaCedente', ''))
        self.comuneResidenzaCedenteEdit.setText(data.get('ComuneResidenzaCedente', ''))
        self.siglaProvinciaNascitaCedenteEdit.setText(data.get('SiglaProvinciaNascitaCedente', ''))
        self.tipoViaResidenzaCedenteEdit.setText(data.get('TipoViaResidenzaCedente', ''))
        self.indirizzoResidenzaCedenteEdit.setText(data.get('IndirizzoResidenzaCedente', ''))
        self.civicoResidenzaCedenteEdit.setText(data.get('CivicoResidenzaCedente', ''))
        self.telefonoCedenteEdit.setText(data.get('TelefonoCedente', ''))
        self.dataAcquistoEdit.setText(data.get('DataAcquisto', ''))

        # Carica lo stato di produzione se la marca esiste
        marca = data.get('MarcaArma', '')
        if marca:
            self.load_stato_produzione(marca)

    def set_combobox_value(self, combobox, value):
        """Imposta il valore di una combobox, aggiungendolo se non esiste"""
        if not value:
            return

        value = value.upper()
        index = combobox.findText(value)
        if index >= 0:
            combobox.setCurrentIndex(index)
        else:
            combobox.addItem(value)
            combobox.setCurrentText(value)

    def update_cedente_data_before_transfer(self):
        """
        Aggiorna i dati del cedente con quelli del proprietario attuale prima del trasferimento
        """
        try:
            if not self.detentore_id:
                return False

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Ottieni i dati del detentore attuale
            cursor.execute("""
                SELECT Cognome, Nome, DataNascita, LuogoNascita, SiglaProvinciaNascita, 
                       ComuneResidenza, SiglaProvinciaResidenza, TipoViaResidenza, 
                       IndirizzoResidenza, CivicoResidenza, Telefono
                FROM detentori
                WHERE ID_Detentore = ?
            """, (self.detentore_id,))

            detentore = cursor.fetchone()

            if not detentore:
                return False

            # Aggiorna i dati del cedente nell'arma con quelli del detentore attuale
            cursor.execute("""
                UPDATE armi
                SET CognomeCedente = ?,
                    NomeCedente = ?,
                    DataNascitaCedente = ?,
                    LuogoNascitaCedente = ?,
                    SiglaProvinciaNascitaCedente = ?,
                    ComuneResidenzaCedente = ?,
                    SiglaProvinciaResidenzaCedente = ?,
                    TipoViaResidenzaCedente = ?,
                    IndirizzoResidenzaCedente = ?,
                    CivicoResidenzaCedente = ?,
                    TelefonoCedente = ?
                WHERE ID_ArmaDetenuta = ?
            """, (
                detentore[0],  # Cognome
                detentore[1],  # Nome
                detentore[2],  # DataNascita
                detentore[3],  # LuogoNascita
                detentore[4],  # SiglaProvinciaNascita
                detentore[5],  # ComuneResidenza
                detentore[6],  # SiglaProvinciaResidenza
                detentore[7],  # TipoViaResidenza
                detentore[8],  # IndirizzoResidenza
                detentore[9],  # CivicoResidenza
                detentore[10],  # Telefono
                self.arma_data['ID_ArmaDetenuta']
            ))

            conn.commit()
            return True

        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati del cedente: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def save_arma(self):
        """Salva i dati dell'arma nel database"""
        try:
            # Verifica se la marca è nuova e chiedi di aggiungerla
            self.check_and_add_new_marca()

            # Verifica che almeno l'ID del detentore sia valorizzato per un nuovo inserimento
            if self.arma_data is None and self.detentore_id is None:
                raise ValueError("ID_Detentore non valorizzato. Impossibile salvare l'arma.")

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Raccogli i dati
            tipoArma = self.tipoArmaEdit.currentText()
            marcaArma = self.marcaArmaEdit.currentText()
            modelloArma = self.modelloArmaEdit.text()
            tipologiaArma = self.tipologiaArmaEdit.text()
            matricola = self.matricolaEdit.text()
            calibroArma = self.calibroArmaEdit.text()
            matricolaCanna = self.matricolaCannaEdit.text()
            lunghezzaCanna = self.lunghezzaCannaEdit.text()
            numeroCanne = self.numeroCanneEdit.text()
            armaLungaCorta = self.armaLungaCortaEdit.currentText()
            tipoCanna = self.tipoCannaEdit.text()
            categoriaArma = self.categoriaArmaEdit.currentText()
            funzionamentoArma = self.funzionamentoArmaEdit.currentText()
            caricamentoArma = self.caricamentoArmaEdit.currentText()
            punzoniArma = self.punzoniArmaEdit.text()
            statoProduzioneArma = self.statoProduzioneArmaEdit.text()
            exOrdDem = self.exOrdDemEdit.text()
            tipoMunizioni = self.tipoMunizioniEdit.text()
            quantitaMunizioni = self.quantitaMunizioniEdit.text()
            tipoBossolo = self.tipoBossoloEdit.text()
            tipoCedente = self.tipoCedenteEdit.text()
            noteArma = self.noteArmaEdit.text()
            cognomeCedente = self.cognomeCedenteEdit.text()
            nomeCedente = self.nomeCedenteEdit.text()
            dataNascitaCedente = self.dataNascitaCedenteEdit.text()
            luogoNascitaCedente = self.luogoNascitaCedenteEdit.text()
            siglaProvinciaResidenzaCedente = self.siglaProvinciaResidenzaCedenteEdit.text()
            comuneResidenzaCedente = self.comuneResidenzaCedenteEdit.text()
            siglaProvinciaNascitaCedente = self.siglaProvinciaNascitaCedenteEdit.text()
            tipoViaResidenzaCedente = self.tipoViaResidenzaCedenteEdit.text()
            indirizzoResidenzaCedente = self.indirizzoResidenzaCedenteEdit.text()
            civicoResidenzaCedente = self.civicoResidenzaCedenteEdit.text()
            telefonoCedente = self.telefonoCedenteEdit.text()
            dataAcquisto = self.dataAcquistoEdit.text()  # Corretto riferimento al campo DataAcquisto

            if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
                # UPDATE per la modifica
                cursor.execute("""
                    UPDATE armi
                    SET TipoArma=?, MarcaArma=?, ModelloArma=?, TipologiaArma=?, Matricola=?, CalibroArma=?, MatricolaCanna=?, LunghezzaCanna=?, NumeroCanne=?,
                        ArmaLungaCorta=?, TipoCanna=?, CategoriaArma=?, FunzionamentoArma=?, CaricamentoArma=?, PunzoniArma=?, StatoProduzioneArma=?,
                        ExOrdDem=?, TipoMunizioni=?, QuantitaMunizioni=?, TipoBossolo=?, TipoCedente=?, NoteArma=?, CognomeCedente=?, NomeCedente=?,
                        DataNascitaCedente=?, LuogoNascitaCedente=?, SiglaProvinciaResidenzaCedente=?, ComuneResidenzaCedente=?, SiglaProvinciaNascitaCedente=?,
                        TipoViaResidenzaCedente=?, IndirizzoResidenzaCedente=?, CivicoResidenzaCedente=?, TelefonoCedente=?, DataAcquisto=?
                    WHERE ID_ArmaDetenuta=?
                """, (
                    tipoArma, marcaArma, modelloArma, tipologiaArma, matricola, calibroArma, matricolaCanna,
                    lunghezzaCanna, numeroCanne,
                    armaLungaCorta, tipoCanna, categoriaArma, funzionamentoArma, caricamentoArma, punzoniArma,
                    statoProduzioneArma,
                    exOrdDem, tipoMunizioni, quantitaMunizioni, tipoBossolo, tipoCedente, noteArma, cognomeCedente,
                    nomeCedente,
                    dataNascitaCedente, luogoNascitaCedente, siglaProvinciaResidenzaCedente, comuneResidenzaCedente,
                    siglaProvinciaNascitaCedente,
                    tipoViaResidenzaCedente, indirizzoResidenzaCedente, civicoResidenzaCedente, telefonoCedente,
                    dataAcquisto,
                    self.arma_data.get('ID_ArmaDetenuta')
                ))
            else:
                # INSERT per un nuovo record
                cursor.execute("""
                    INSERT INTO armi (ID_Detentore, TipoArma, MarcaArma, ModelloArma, TipologiaArma, Matricola, CalibroArma, MatricolaCanna, LunghezzaCanna,
                        NumeroCanne, ArmaLungaCorta, TipoCanna, CategoriaArma, FunzionamentoArma, CaricamentoArma, PunzoniArma, StatoProduzioneArma,
                        ExOrdDem, TipoMunizioni, QuantitaMunizioni, TipoBossolo, TipoCedente, NoteArma, CognomeCedente, NomeCedente, DataNascitaCedente,
                        LuogoNascitaCedente, SiglaProvinciaResidenzaCedente, ComuneResidenzaCedente, SiglaProvinciaNascitaCedente, TipoViaResidenzaCedente,
                        IndirizzoResidenzaCedente, CivicoResidenzaCedente, TelefonoCedente, DataAcquisto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.detentore_id, tipoArma, marcaArma, modelloArma, tipologiaArma, matricola, calibroArma,
                    matricolaCanna, lunghezzaCanna,
                    numeroCanne, armaLungaCorta, tipoCanna, categoriaArma, funzionamentoArma, caricamentoArma,
                    punzoniArma, statoProduzioneArma,
                    exOrdDem, tipoMunizioni, quantitaMunizioni, tipoBossolo, tipoCedente, noteArma, cognomeCedente,
                    nomeCedente,
                    dataNascitaCedente, luogoNascitaCedente, siglaProvinciaResidenzaCedente, comuneResidenzaCedente,
                    siglaProvinciaNascitaCedente,
                    tipoViaResidenzaCedente, indirizzoResidenzaCedente, civicoResidenzaCedente, telefonoCedente,
                    dataAcquisto
                ))
            conn.commit()
        except Exception as e:
            print("Errore durante il salvataggio dell'arma:", e)
        finally:
            conn.close()
        self.accept()

    def modify_arma(self):
        """Modifica l'arma esistente"""
        self.save_arma()

    def delete_arma(self):
        """Elimina l'arma dal database"""
        if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM armi WHERE ID_ArmaDetenuta = ?", (self.arma_data.get('ID_ArmaDetenuta'),))
            conn.commit()
            conn.close()
        self.accept()

    def transfer_arma(self):
        """Apre la finestra di dialogo per il trasferimento dell'arma"""
        try:
            if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
                # Aggiorna i dati del cedente con quelli del proprietario attuale
                success = self.update_cedente_data_before_transfer()

                if not success:
                    QMessageBox.warning(
                        self,
                        "Aggiornamento Cedente",
                        "Non è stato possibile aggiornare automaticamente i dati del cedente. " +
                        "Il trasferimento continuerà comunque."
                    )

                dialog = TransferimentoDialog(
                    arma_id=self.arma_data['ID_ArmaDetenuta'],
                    cedente_id=self.detentore_id,
                    current_detentore=self.detentore_id,
                    parent=self
                )
                if dialog.exec_() == QDialog.Accepted:
                    self.accept()
        except Exception as e:
            print("Errore nel trasferimento dell'arma:", e)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Per testare, si passa None per arma_data e un detentore id fittizio (es. 1)
    dialog = ArmaDialog(detentore_id=1)
    dialog.exec_()