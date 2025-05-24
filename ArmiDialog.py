import sqlite3
import traceback
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QGroupBox, QPushButton, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QSizePolicy, QComboBox, QMessageBox, QInputDialog, QDateEdit, QCheckBox,
)
from PyQt5.QtCore import QDate, Qt
from Utility import convert_all_lineedits_to_uppercase, DateInputWidget
from TransferimentoDialog import TransferimentoDialog


class ArmaDialog(QDialog):
    def __init__(self, arma_data=None, detentore_id=None):
        """
        Se arma_data è None, si tratta di un nuovo inserimento.
        detentore_id è l'ID del detentore a cui l'arma appartiene.
        """
        super().__init__()

        # Se arma_data esiste, verifichiamo se contiene il campo DataAcquisto
        if arma_data and 'DataAcquisto' not in arma_data:
            # Recuperiamo direttamente il valore dal database
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()
                cursor.execute("SELECT DataAcquisto FROM armi WHERE ID_ArmaDetenuta = ?",
                               (arma_data['ID_ArmaDetenuta'],))
                data_acquisto = cursor.fetchone()
                if data_acquisto:
                    # Aggiungiamo il campo al dizionario
                    arma_data['DataAcquisto'] = data_acquisto[0] if data_acquisto[0] is not None else ''
                else:
                    arma_data['DataAcquisto'] = ''
            except Exception as e:
                print(f"Errore nel recupero della data di acquisto: {e}")
                arma_data['DataAcquisto'] = ''
            finally:
                if conn:
                    conn.close()

        # NUOVA PARTE: Verifica dei campi del luogo di detenzione
        if arma_data:
            # Lista dei campi del luogo di detenzione
            campi_detenzione = ['ComuneDetenzione', 'ProvinciaDetenzione', 'TipoViaDetenzione',
                                'IndirizzoDetenzione', 'CivicoDetenzione', 'NoteDetenzione']

            # Verifica se mancano campi
            campi_mancanti = [campo for campo in campi_detenzione if campo not in arma_data]

            if campi_mancanti:
                print(f"Campi detenzione mancanti: {campi_mancanti}")
                try:
                    conn = sqlite3.connect("gestione_armi.db")
                    cursor = conn.cursor()

                    # Costruisci la query per selezionare i campi mancanti
                    select_fields = ', '.join(campi_mancanti)
                    cursor.execute(f"SELECT {select_fields} FROM armi WHERE ID_ArmaDetenuta = ?",
                                   (arma_data['ID_ArmaDetenuta'],))

                    risultati = cursor.fetchone()

                    # Aggiungi i valori al dizionario arma_data
                    if risultati:
                        for i, campo in enumerate(campi_mancanti):
                            arma_data[campo] = risultati[i] if risultati[i] is not None else ''
                            print(f"Recuperato {campo}: {arma_data[campo]}")
                    else:
                        for campo in campi_mancanti:
                            arma_data[campo] = ''
                except Exception as e:
                    print(f"Errore nel recupero dei dati del luogo di detenzione: {e}")
                    import traceback
                    traceback.print_exc()
                    for campo in campi_mancanti:
                        arma_data[campo] = ''
                finally:
                    if conn:
                        conn.close()

        self.arma_data = arma_data
        self.detentore_id = detentore_id

        # Il resto del codice rimane invariato...
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

        # Tab 3: Luogo Detenzione
        self._create_luogo_detenzione_tab()

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

        # Sostituisci QDateEdit con DateInputWidget
        self.dataAcquistoEdit = DateInputWidget()
        self.dataAcquistoEdit.setDisplayFormat("dd/MM/yyyy")
        self.dataAcquistoEdit.setDate(QDate.currentDate())

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

        # --- nuovi campi ---
        self.numeroCatalogoEdit = QLineEdit()
        self.classificazioneEuropeaEdit = QLineEdit()

        # Modifica: convertire tipoCedenteEdit da QLineEdit a QComboBox
        self.tipoCedenteEdit = QComboBox()
        self.tipoCedenteEdit.addItem("PERSONA FISICA")
        self.tipoCedenteEdit.addItem("PERSONA GIURIDICA")
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

        # **Riga 4: i due nuovi campi**
        grid.addWidget(QLabel("Numero Catalogo:"), 3, 0)
        grid.addWidget(self.numeroCatalogoEdit, 3, 1)
        grid.addWidget(QLabel("Classificazione Europea:"), 3, 2)
        grid.addWidget(self.classificazioneEuropeaEdit, 3, 3)

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

    def _create_luogo_detenzione_tab(self):
        """Crea la tab con i dettagli del luogo di detenzione dell'arma"""
        self.tab_detenzione = QWidget()

        # Creazione dei campi di testo
        self.comuneDetenzioneEdit = QLineEdit()
        self.provinciaDetenzioneEdit = QLineEdit()
        self.tipoViaDetenzioneEdit = QLineEdit()
        self.indirizzoDetenzioneEdit = QLineEdit()
        self.civicoDetenzioneEdit = QLineEdit()
        self.noteDetenzioneEdit = QLineEdit()

        # Aggiungi la checkbox "Uguale alla residenza"
        self.ugualeResidenzaCheck = QCheckBox("Uguale alla residenza del detentore")
        self.ugualeResidenzaCheck.stateChanged.connect(self.on_uguale_residenza_changed)

        # Creazione del gruppo per i dati del luogo
        group_detenzione = QGroupBox("Dati Luogo Detenzione")
        grid = QGridLayout()

        # Aggiungi la checkbox nella prima riga
        grid.addWidget(self.ugualeResidenzaCheck, 0, 0, 1, 4)

        # Riga 2
        grid.addWidget(QLabel("Comune:"), 1, 0)
        grid.addWidget(self.comuneDetenzioneEdit, 1, 1)
        grid.addWidget(QLabel("Provincia:"), 1, 2)
        grid.addWidget(self.provinciaDetenzioneEdit, 1, 3)

        # Riga 3
        grid.addWidget(QLabel("Tipo Via:"), 2, 0)
        grid.addWidget(self.tipoViaDetenzioneEdit, 2, 1)
        grid.addWidget(QLabel("Indirizzo:"), 2, 2)
        grid.addWidget(self.indirizzoDetenzioneEdit, 2, 3)

        # Riga 4
        grid.addWidget(QLabel("Civico:"), 3, 0)
        grid.addWidget(self.civicoDetenzioneEdit, 3, 1)

        group_detenzione.setLayout(grid)

        # Note luogo detenzione
        group_note = QGroupBox("Note Luogo Detenzione")
        note_layout = QFormLayout()
        note_layout.addRow("Note:", self.noteDetenzioneEdit)
        group_note.setLayout(note_layout)

        # Layout principale della tab
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_detenzione)
        main_layout.addWidget(group_note)
        main_layout.addStretch()
        self.tab_detenzione.setLayout(main_layout)

    def on_uguale_residenza_changed(self, state):
        """Gestisce il cambio di stato della checkbox 'Uguale alla residenza'"""
        if state == Qt.Checked:
            # Se è selezionata, copiamo i dati della residenza del detentore
            self.copy_detentore_residence_data()
        else:
            # Se non è selezionata, non facciamo nulla (l'utente potrà inserire dati diversi)
            pass

    def on_detenzione_field_changed(self):
        """
        Gestisce i cambiamenti nei campi del luogo di detenzione.
        Se vengono modificati manualmente, deseleziona la checkbox "Uguale alla residenza".
        """
        # Converti il testo in maiuscolo
        sender = self.sender()
        cursor_pos = sender.cursorPosition()
        sender.setText(sender.text().upper())
        sender.setCursorPosition(cursor_pos)

        # Deseleziona la checkbox se il testo viene modificato manualmente
        # Solo se la checkbox è selezionata
        if hasattr(self, 'ugualeResidenzaCheck') and self.ugualeResidenzaCheck.isChecked():
            self.ugualeResidenzaCheck.blockSignals(True)  # Blocca i segnali per evitare ricorsione
            self.ugualeResidenzaCheck.setChecked(False)
            self.ugualeResidenzaCheck.blockSignals(False)

    def on_uguale_residenza_changed(self, state):
        """Gestisce il cambio di stato della checkbox 'Uguale alla residenza'"""
        if state == Qt.Checked:
            # Se è selezionata, copiamo i dati della residenza del detentore
            self.copy_detentore_residence_data()
        else:
            # Se non è selezionata, non facciamo nulla (l'utente potrà inserire dati diversi)
            pass

    def copy_detentore_residence_data(self):
        """Copia i dati della residenza del detentore nei campi del luogo di detenzione"""
        try:
            # Verifichiamo che ci sia un detentore ID valido
            if not self.detentore_id:
                QMessageBox.warning(self, "Attenzione", "Nessun detentore selezionato.")
                self.ugualeResidenzaCheck.setChecked(False)
                return

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Recupera i dati della residenza del detentore dal database usando i nomi corretti delle colonne
            cursor.execute("""
                SELECT ComuneResidenza, SiglaProvinciaResidenza, TipoVia,
                       Via, Civico
                FROM detentori
                WHERE ID_Detentore = ?
            """, (self.detentore_id,))

            result = cursor.fetchone()

            if result:
                # Copia i dati nei campi del luogo di detenzione
                self.comuneDetenzioneEdit.setText(result[0] if result[0] else '')
                self.provinciaDetenzioneEdit.setText(result[1] if result[1] else '')
                self.tipoViaDetenzioneEdit.setText(result[2] if result[2] else '')
                self.indirizzoDetenzioneEdit.setText(result[3] if result[3] else '')
                self.civicoDetenzioneEdit.setText(result[4] if result[4] else '')

                QMessageBox.information(self, "Informazione",
                                        "Dati della residenza del detentore copiati nel luogo di detenzione.")
            else:
                QMessageBox.warning(self, "Attenzione",
                                    "Non sono stati trovati dati di residenza per il detentore selezionato.")
                self.ugualeResidenzaCheck.setChecked(False)

        except Exception as e:
            QMessageBox.critical(self, "Errore",
                                 f"Si è verificato un errore durante il recupero dei dati della residenza:\n{str(e)}")
            print(f"Errore nel recupero dei dati della residenza: {e}")
            import traceback
            traceback.print_exc()
            self.ugualeResidenzaCheck.setChecked(False)
        finally:
            if conn:
                conn.close()
    def on_detenzione_field_changed(self):
        """
        Gestisce i cambiamenti nei campi del luogo di detenzione.
        Se vengono modificati manualmente, deseleziona la checkbox "Uguale alla residenza".
        """
        # Converti il testo in maiuscolo
        sender = self.sender()
        cursor_pos = sender.cursorPosition()
        sender.setText(sender.text().upper())
        sender.setCursorPosition(cursor_pos)

        # Deseleziona la checkbox se il testo viene modificato manualmente
        # Solo se la checkbox è selezionata
        if hasattr(self, 'ugualeResidenzaCheck') and self.ugualeResidenzaCheck.isChecked():
            self.ugualeResidenzaCheck.blockSignals(True)  # Blocca i segnali per evitare ricorsione
            self.ugualeResidenzaCheck.setChecked(False)
            self.ugualeResidenzaCheck.blockSignals(False)

    def _create_cedente_tab(self):
        self.tab_cedente = QWidget()

        # Creazione dei campi di testo
        self.cognomeCedenteEdit = QLineEdit()
        self.nomeCedenteEdit = QLineEdit()

        # Aggiungiamo le etichette come attributi per poterle modificare
        self.cognomeCedenteLabel = QLabel("Cognome:")
        self.nomeCedenteLabel = QLabel("Nome:")
        self.dataNascitaCedenteLabel = QLabel("Data di Nascita:")
        self.luogoNascitaCedenteLabel = QLabel("Luogo di Nascita:")
        self.provinciaNascitaCedenteLabel = QLabel("Provincia di Nascita:")

        # Widget per la data di nascita
        self.dataNascitaCedenteEdit = DateInputWidget()
        self.dataNascitaCedenteEdit.setDisplayFormat("dd/MM/yyyy")
        self.dataNascitaCedenteEdit.setDate(QDate.currentDate().addYears(-18))

        # Altri widget esistenti
        self.luogoNascitaCedenteEdit = QLineEdit()
        self.siglaProvinciaResidenzaCedenteEdit = QLineEdit()
        self.comuneResidenzaCedenteEdit = QLineEdit()
        self.siglaProvinciaNascitaCedenteEdit = QLineEdit()
        self.tipoViaResidenzaCedenteEdit = QLineEdit()
        self.indirizzoResidenzaCedenteEdit = QLineEdit()
        self.civicoResidenzaCedenteEdit = QLineEdit()
        self.telefonoCedenteEdit = QLineEdit()

        # Creiamo un attributo per il titolo del gruppo residenza
        self.group_residenza = QGroupBox("Dati Residenza")
        self.group_anagrafica = QGroupBox("Dati Anagrafici")

        # Layout per l'anagrafica
        grid_anagrafica = QGridLayout()

        # Riga 1
        grid_anagrafica.addWidget(self.cognomeCedenteLabel, 0, 0)
        grid_anagrafica.addWidget(self.cognomeCedenteEdit, 0, 1)
        grid_anagrafica.addWidget(self.nomeCedenteLabel, 0, 2)
        grid_anagrafica.addWidget(self.nomeCedenteEdit, 0, 3)

        # Riga 2 - questi widget verranno nascosti per persona giuridica
        self.datiNascitaWidget = QWidget()
        nascita_layout = QGridLayout(self.datiNascitaWidget)
        nascita_layout.addWidget(self.dataNascitaCedenteLabel, 0, 0)
        nascita_layout.addWidget(self.dataNascitaCedenteEdit, 0, 1)
        nascita_layout.addWidget(self.luogoNascitaCedenteLabel, 0, 2)
        nascita_layout.addWidget(self.luogoNascitaCedenteEdit, 0, 3)
        nascita_layout.addWidget(self.provinciaNascitaCedenteLabel, 1, 0)
        nascita_layout.addWidget(self.siglaProvinciaNascitaCedenteEdit, 1, 1)
        nascita_layout.addWidget(QLabel("Telefono:"), 1, 2)
        nascita_layout.addWidget(self.telefonoCedenteEdit, 1, 3)
        nascita_layout.setContentsMargins(0, 0, 0, 0)

        grid_anagrafica.addWidget(self.datiNascitaWidget, 1, 0, 2, 4)

        self.group_anagrafica.setLayout(grid_anagrafica)

        # Layout per residenza (stessa configurazione di prima)
        grid_residenza = QGridLayout()
        grid_residenza.addWidget(QLabel("Comune:"), 0, 0)
        grid_residenza.addWidget(self.comuneResidenzaCedenteEdit, 0, 1)
        grid_residenza.addWidget(QLabel("Provincia:"), 0, 2)
        grid_residenza.addWidget(self.siglaProvinciaResidenzaCedenteEdit, 0, 3)
        grid_residenza.addWidget(QLabel("Tipo Via:"), 1, 0)
        grid_residenza.addWidget(self.tipoViaResidenzaCedenteEdit, 1, 1)
        grid_residenza.addWidget(QLabel("Indirizzo:"), 1, 2)
        grid_residenza.addWidget(self.indirizzoResidenzaCedenteEdit, 1, 3)
        grid_residenza.addWidget(QLabel("Civico:"), 2, 0)
        grid_residenza.addWidget(self.civicoResidenzaCedenteEdit, 2, 1)
        self.group_residenza.setLayout(grid_residenza)

        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_anagrafica)
        main_layout.addWidget(self.group_residenza)
        main_layout.addStretch()
        self.tab_cedente.setLayout(main_layout)

    def _update_cedente_type(self):
        tipo = self.tipoCedenteEdit.currentText()

        if tipo == "PERSONA GIURIDICA":
            # Cambiamo le etichette per persona giuridica
            self.cognomeCedenteLabel.setText("Ragione Sociale:")
            self.nomeCedenteLabel.setText("Partita IVA/CF:")
            self.datiNascitaWidget.setVisible(False)
            self.group_residenza.setTitle("Sede")
        else:
            # Ripristiniamo le etichette originali per persona fisica
            self.cognomeCedenteLabel.setText("Cognome:")
            self.nomeCedenteLabel.setText("Nome:")
            self.datiNascitaWidget.setVisible(True)
            self.group_residenza.setTitle("Dati Residenza")

    def _setup_layout(self):
        """Configura il layout principale"""
        main_layout = QVBoxLayout()

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tab_arma, "Arma")
        self.tab_widget.addTab(self.tab_cedente, "Cedente")
        self.tab_widget.addTab(self.tab_detenzione, "Luogo Detenzione")  # Nuova tab

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
        # Aggiungi questo collegamento
        self.tipoCedenteEdit.currentIndexChanged.connect(self._update_cedente_type)

        # Assicurarsi che tutte le combobox convertano il testo in maiuscolo
        for combo in [self.tipoArmaEdit, self.marcaArmaEdit, self.armaLungaCortaEdit,
                      self.categoriaArmaEdit, self.funzionamentoArmaEdit, self.caricamentoArmaEdit]:
            combo.setEditable(True)
            combo.editTextChanged.connect(self.convert_combobox_text_to_uppercase)

        # Collega i segnali per i campi del luogo di detenzione
        for field in [self.comuneDetenzioneEdit, self.provinciaDetenzioneEdit,
                      self.tipoViaDetenzioneEdit, self.indirizzoDetenzioneEdit,
                      self.civicoDetenzioneEdit, self.noteDetenzioneEdit]:
            field.textChanged.connect(self.on_detenzione_field_changed)

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
        # DEBUG: Stampiamo i dati ricevuti per verificare il campo DataAcquisto
        print("DEBUG - Dati arma in populate_fields:")
        print(f"DataAcquisto nel dataset: {data.get('DataAcquisto', 'NON PRESENTE')}")

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
        self.set_combobox_value(self.tipoCedenteEdit, data.get('TipoCedente', ''))
        self.noteArmaEdit.setText(data.get('NoteArma', ''))
        self.cognomeCedenteEdit.setText(data.get('CognomeCedente', ''))
        self.nomeCedenteEdit.setText(data.get('NomeCedente', ''))
        self.luogoNascitaCedenteEdit.setText(data.get('LuogoNascitaCedente', ''))
        self.siglaProvinciaResidenzaCedenteEdit.setText(data.get('SiglaProvinciaResidenzaCedente', ''))
        self.comuneResidenzaCedenteEdit.setText(data.get('ComuneResidenzaCedente', ''))
        self.siglaProvinciaNascitaCedenteEdit.setText(data.get('SiglaProvinciaNascitaCedente', ''))
        self.tipoViaResidenzaCedenteEdit.setText(data.get('TipoViaResidenzaCedente', ''))
        self.indirizzoResidenzaCedenteEdit.setText(data.get('IndirizzoResidenzaCedente', ''))
        self.civicoResidenzaCedenteEdit.setText(data.get('CivicoResidenzaCedente', ''))
        self.telefonoCedenteEdit.setText(data.get('TelefonoCedente', ''))

        # Popola campi del luogo detenzione
        self.comuneDetenzioneEdit.setText(data.get('ComuneDetenzione', ''))
        self.provinciaDetenzioneEdit.setText(data.get('ProvinciaDetenzione', ''))
        self.tipoViaDetenzioneEdit.setText(data.get('TipoViaDetenzione', ''))
        self.indirizzoDetenzioneEdit.setText(data.get('IndirizzoDetenzione', ''))
        self.civicoDetenzioneEdit.setText(data.get('CivicoDetenzione', ''))
        self.noteDetenzioneEdit.setText(data.get('NoteDetenzione', ''))

        # --- nuovi campi ---
        self.numeroCatalogoEdit.setText(data.get('NumeroCatalogo', ''))
        self.classificazioneEuropeaEdit.setText(data.get('ClassificazioneEuropea', ''))

        # Per i campi data
        if 'DataAcquisto' in data and data['DataAcquisto']:
            try:
                date_parts = data['DataAcquisto'].split('/')
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    self.dataAcquistoEdit.setDate(QDate(year, month, day))
            except (ValueError, IndexError):
                self.dataAcquistoEdit.setDate(QDate.currentDate())

        if 'DataNascitaCedente' in data and data['DataNascitaCedente']:
            try:
                date_parts = data['DataNascitaCedente'].split('/')
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    self.dataNascitaCedenteEdit.setDate(QDate(year, month, day))
            except (ValueError, IndexError):
                self.dataNascitaCedenteEdit.setDate(QDate.currentDate().addYears(-18))

        # Imposta il tipo di cedente e aggiorna l'interfaccia
        tipo_cedente = data.get('TipoCedente', '')
        if tipo_cedente == "PERSONA GIURIDICA":
            index = self.tipoCedenteEdit.findText("PERSONA GIURIDICA")
            if index >= 0:
                self.tipoCedenteEdit.setCurrentIndex(index)
        else:
            self.tipoCedenteEdit.setCurrentIndex(0)

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
                    TelefonoCedente = ?,
                    TipoCedente = 'PERSONA FISICA'
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

            print(f"Tipo cedente impostato a PERSONA FISICA per l'arma {self.arma_data['ID_ArmaDetenuta']}")
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
            # Verifica e aggiunge nuova marca se necessario
            self.check_and_add_new_marca()

            # Controllo date
            if not self.validate_dates():
                return False

            # Controllo ID detentore/arma
            if self.arma_data is None and self.detentore_id is None:
                raise ValueError("ID_Detentore non valorizzato. Impossibile salvare l'arma.")

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Raccolta dati dal form
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
            tipoCedente = self.tipoCedenteEdit.currentText()
            noteArma = self.noteArmaEdit.text()
            numeroCatalogo = self.numeroCatalogoEdit.text()
            classificazioneEuropea = self.classificazioneEuropeaEdit.text()
            print(f"[DEBUG] numeroCatalogo = '{numeroCatalogo}', classificazioneEuropea = '{classificazioneEuropea}'")
            cognomeCedente = self.cognomeCedenteEdit.text()
            nomeCedente = self.nomeCedenteEdit.text()
            dataNascitaCedente = self.dataNascitaCedenteEdit.date().toString("dd/MM/yyyy")
            luogoNascitaCedente = self.luogoNascitaCedenteEdit.text()
            siglaProvinciaResidenzaCedente = self.siglaProvinciaResidenzaCedenteEdit.text()
            comuneResidenzaCedente = self.comuneResidenzaCedenteEdit.text()
            siglaProvinciaNascitaCedente = self.siglaProvinciaNascitaCedenteEdit.text()
            tipoViaResidenzaCedente = self.tipoViaResidenzaCedenteEdit.text()
            indirizzoResidenzaCedente = self.indirizzoResidenzaCedenteEdit.text()
            civicoResidenzaCedente = self.civicoResidenzaCedenteEdit.text()
            telefonoCedente = self.telefonoCedenteEdit.text()
            dataAcquisto = self.dataAcquistoEdit.date().toString("dd/MM/yyyy")
            comuneDetenzione = self.comuneDetenzioneEdit.text()
            provinciaDetenzione = self.provinciaDetenzioneEdit.text()
            tipoViaDetenzione = self.tipoViaDetenzioneEdit.text()
            indirizzoDetenzione = self.indirizzoDetenzioneEdit.text()
            civicoDetenzione = self.civicoDetenzioneEdit.text()
            noteDetenzione = self.noteDetenzioneEdit.text()

            # Se esiste un ID_ArmaDetenuta, faccio UPDATE
            if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
                cursor.execute("""
                    UPDATE armi
                    SET TipoArma=?, MarcaArma=?, ModelloArma=?, TipologiaArma=?, Matricola=?, CalibroArma=?,
                        MatricolaCanna=?, LunghezzaCanna=?, NumeroCanne=?, ArmaLungaCorta=?, TipoCanna=?,
                        CategoriaArma=?, FunzionamentoArma=?, CaricamentoArma=?, PunzoniArma=?, StatoProduzioneArma=?,
                        ExOrdDem=?, TipoMunizioni=?, QuantitaMunizioni=?, TipoBossolo=?, TipoCedente=?, NoteArma=?,
                        NumeroCatalogo=?, ClassificazioneEuropea=?, CognomeCedente=?, NomeCedente=?, DataNascitaCedente=?,
                        LuogoNascitaCedente=?, SiglaProvinciaResidenzaCedente=?, ComuneResidenzaCedente=?,
                        SiglaProvinciaNascitaCedente=?, TipoViaResidenzaCedente=?, IndirizzoResidenzaCedente=?,
                        CivicoResidenzaCedente=?, TelefonoCedente=?, DataAcquisto=?, ComuneDetenzione=?,
                        ProvinciaDetenzione=?, TipoViaDetenzione=?, IndirizzoDetenzione=?, CivicoDetenzione=?,
                        NoteDetenzione=?
                    WHERE ID_ArmaDetenuta=?
                """, (
                    tipoArma, marcaArma, modelloArma, tipologiaArma, matricola, calibroArma,
                    matricolaCanna, lunghezzaCanna, numeroCanne, armaLungaCorta, tipoCanna,
                    categoriaArma, funzionamentoArma, caricamentoArma, punzoniArma, statoProduzioneArma,
                    exOrdDem, tipoMunizioni, quantitaMunizioni, tipoBossolo, tipoCedente, noteArma,
                    numeroCatalogo, classificazioneEuropea, cognomeCedente, nomeCedente, dataNascitaCedente,
                    luogoNascitaCedente, siglaProvinciaResidenzaCedente, comuneResidenzaCedente,
                    siglaProvinciaNascitaCedente, tipoViaResidenzaCedente, indirizzoResidenzaCedente,
                    civicoResidenzaCedente, telefonoCedente, dataAcquisto, comuneDetenzione,
                    provinciaDetenzione, tipoViaDetenzione, indirizzoDetenzione, civicoDetenzione,
                    noteDetenzione, self.arma_data.get('ID_ArmaDetenuta')
                ))
            else:
                # Nuovo record: INSERT dinamico per mantenere cols/params allineati
                cols = [
                    "ID_Detentore", "TipoArma", "MarcaArma", "ModelloArma", "TipologiaArma",
                    "Matricola", "CalibroArma", "MatricolaCanna", "LunghezzaCanna", "NumeroCanne",
                    "ArmaLungaCorta", "TipoCanna", "CategoriaArma", "FunzionamentoArma",
                    "CaricamentoArma", "PunzoniArma", "StatoProduzioneArma", "ExOrdDem",
                    "TipoMunizioni", "QuantitaMunizioni", "TipoBossolo", "TipoCedente", "NoteArma",
                    "NumeroCatalogo", "ClassificazioneEuropea", "CognomeCedente", "NomeCedente",
                    "DataNascitaCedente", "LuogoNascitaCedente", "SiglaProvinciaResidenzaCedente",
                    "ComuneResidenzaCedente", "SiglaProvinciaNascitaCedente",
                    "TipoViaResidenzaCedente", "IndirizzoResidenzaCedente", "CivicoResidenzaCedente",
                    "TelefonoCedente", "DataAcquisto", "ComuneDetenzione", "ProvinciaDetenzione",
                    "TipoViaDetenzione", "IndirizzoDetenzione", "CivicoDetenzione", "NoteDetenzione"
                ]
                qs = ", ".join("?" for _ in cols)
                sql = f"INSERT INTO armi ({', '.join(cols)}) VALUES ({qs})"
                params = [
                    self.detentore_id, tipoArma, marcaArma, modelloArma, tipologiaArma,
                    matricola, calibroArma, matricolaCanna, lunghezzaCanna, numeroCanne,
                    armaLungaCorta, tipoCanna, categoriaArma, funzionamentoArma,
                    caricamentoArma, punzoniArma, statoProduzioneArma, exOrdDem,
                    tipoMunizioni, quantitaMunizioni, tipoBossolo, tipoCedente, noteArma,
                    numeroCatalogo, classificazioneEuropea, cognomeCedente, nomeCedente,
                    dataNascitaCedente, luogoNascitaCedente, siglaProvinciaResidenzaCedente,
                    comuneResidenzaCedente, siglaProvinciaNascitaCedente,
                    tipoViaResidenzaCedente, indirizzoResidenzaCedente, civicoResidenzaCedente,
                    telefonoCedente, dataAcquisto, comuneDetenzione, provinciaDetenzione,
                    tipoViaDetenzione, indirizzoDetenzione, civicoDetenzione, noteDetenzione
                ]
                print(f"[DEBUG] SQL: {sql}")
                print(f"[DEBUG] params ({len(params)}): {params}")
                cursor.execute(sql, params)

            conn.commit()
            QMessageBox.information(self, "Successo", "Arma salvata con successo!")
        except Exception as e:
            print(f"ERRORE durante il salvataggio: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio:\n{e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

        self.accept()
        return True

    def modify_arma(self):
        """Modifica l'arma esistente"""
        self.save_arma()

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

    def validate_dates(self):
        """Valida che le date inserite siano coerenti"""
        current_date = QDate.currentDate()

        # Controlla che la data di acquisto non sia nel futuro
        if self.dataAcquistoEdit.date() > current_date:
            QMessageBox.warning(self, "Errore Data", "La data di acquisto non può essere nel futuro.")
            return False

        # Controlla che la data di nascita del cedente sia valida (ad es. età minima 18 anni)
        min_birth_date = current_date.addYears(-18)
        if self.dataNascitaCedenteEdit.date() > min_birth_date:
            QMessageBox.warning(self, "Errore Data", "Il cedente deve avere almeno 18 anni.")
            return False

        return True

    def string_to_qdate(self, date_string):
        """Converte una stringa in formato 'dd/MM/yyyy' in un oggetto QDate"""
        if not date_string:
            return QDate()

        try:
            date_parts = date_string.split('/')
            if len(date_parts) == 3:
                day, month, year = map(int, date_parts)
                return QDate(year, month, day)
        except (ValueError, IndexError):
            pass

        return QDate()  # Restituisce una data invalida in caso di errore

    def delete_arma(self):
        """Elimina l'arma dal database"""
        if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
            # Conferma eliminazione
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Conferma eliminazione",
                                         "Sei sicuro di voler eliminare questa arma?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Apri il dialogo per la motivazione
                dialogo_motivo = DialogoMotivoEliminazione(self.arma_data, self)
                if dialogo_motivo.exec_() != QDialog.Accepted:
                    return  # L'utente ha annullato l'eliminazione

                # Ottieni il motivo completo formattato
                motivo_completo = dialogo_motivo.get_motivo_completo()

                conn = None
                try:
                    conn = sqlite3.connect("gestione_armi.db")
                    cursor = conn.cursor()

                    # Ottieni i dettagli dell'arma prima dell'eliminazione
                    arma_id = self.arma_data.get('ID_ArmaDetenuta')
                    detentore_id = self.detentore_id

                    # Recupera i dati del detentore (cedente)
                    cursor.execute("""
                        SELECT Cognome, Nome, CodiceFiscale 
                        FROM detentori 
                        WHERE ID_Detentore = ?
                    """, (detentore_id,))
                    detentore_data = cursor.fetchone()

                    # Recupera tutti i dati dell'arma
                    cursor.execute("""
                        SELECT TipoArma, MarcaArma, ModelloArma, Matricola, CalibroArma
                        FROM armi 
                        WHERE ID_ArmaDetenuta = ?
                    """, (arma_id,))
                    arma_details = cursor.fetchone()

                    # Ottieni la data corrente per il trasferimento
                    from PyQt5.QtCore import QDate, QDateTime
                    data_trasferimento = QDate.currentDate().toString("yyyy-MM-dd")
                    timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

                    # Prepara la nota con il motivo fornito dall'utente
                    note = motivo_completo

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
                        note,  # Note (con il motivo completo)
                        timestamp,  # Timestamp_Registrazione
                        arma_details[1] if arma_details else self.arma_data.get('MarcaArma', ''),  # MarcaArma
                        arma_details[2] if arma_details else self.arma_data.get('ModelloArma', ''),  # ModelloArma
                        arma_details[3] if arma_details else self.arma_data.get('Matricola', ''),  # Matricola
                        arma_details[4] if arma_details else self.arma_data.get('CalibroArma', ''),  # CalibroArma
                        arma_details[0] if arma_details else self.arma_data.get('TipoArma', ''),  # TipoArma
                        detentore_data[0] if detentore_data else '',  # Cedente_Cognome
                        detentore_data[1] if detentore_data else '',  # Cedente_Nome
                        detentore_data[2] if detentore_data else ''  # Cedente_CodiceFiscale
                    ))

                    # Ora elimina l'arma
                    cursor.execute("DELETE FROM armi WHERE ID_ArmaDetenuta = ?", (arma_id,))
                    conn.commit()

                    QMessageBox.information(self, "Eliminazione completata",
                                            f"L'arma è stata eliminata con successo.\nMotivo registrato nello storico.")
                    self.accept()

                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante l'eliminazione: {str(e)}")
                    print("Errore durante l'eliminazione dell'arma:", e)
                finally:
                    if conn:
                        conn.close()
class DialogoMotivoEliminazione(QDialog):
    def __init__(self, arma_data=None, detentore_id=None):
        """
        Se arma_data è None, si tratta di un nuovo inserimento.
        detentore_id è l'ID del detentore a cui l'arma appartiene.
        """
        super().__init__()

        # --- Recupero DataAcquisto se manca ---
        if arma_data and 'DataAcquisto' not in arma_data:
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DataAcquisto FROM armi WHERE ID_ArmaDetenuta = ?",
                    (arma_data['ID_ArmaDetenuta'],)
                )
                row = cursor.fetchone()
                arma_data['DataAcquisto'] = row[0] if row and row[0] else ''
            except Exception as e:
                print(f"Errore recupero DataAcquisto: {e}")
                arma_data['DataAcquisto'] = ''
            finally:
                conn.close()

        # --- Recupero campi luogo di detenzione se mancano ---
        if arma_data:
            campi_detenzione = [
                'ComuneDetenzione', 'ProvinciaDetenzione', 'TipoViaDetenzione',
                'IndirizzoDetenzione', 'CivicoDetenzione', 'NoteDetenzione'
            ]
            mancanti = [c for c in campi_detenzione if c not in arma_data]
            if mancanti:
                try:
                    conn = sqlite3.connect("gestione_armi.db")
                    cursor = conn.cursor()
                    select_fields = ', '.join(mancanti)
                    cursor.execute(
                        f"SELECT {select_fields} FROM armi WHERE ID_ArmaDetenuta = ?",
                        (arma_data['ID_ArmaDetenuta'],)
                    )
                    risultati = cursor.fetchone() or []
                    for i, campo in enumerate(mancanti):
                        arma_data[campo] = risultati[i] or ''
                except Exception as e:
                    print(f"Errore recupero luogo detenzione: {e}")
                finally:
                    conn.close()

        # --- NUOVO: recupero NumeroCatalogo e ClassificazioneEuropea se mancanti ---
        if arma_data and (
                'NumeroCatalogo' not in arma_data or
                'ClassificazioneEuropea' not in arma_data
        ):
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT NumeroCatalogo, ClassificazioneEuropea FROM armi WHERE ID_ArmaDetenuta = ?",
                    (arma_data['ID_ArmaDetenuta'],)
                )
                row = cursor.fetchone()
                arma_data['NumeroCatalogo'] = row[0] if row and row[0] else ''
                arma_data['ClassificazioneEuropea'] = row[1] if row and row[1] else ''
            except Exception as e:
                print(f"Errore recupero catalogo/classificazione: {e}")
                arma_data['NumeroCatalogo'] = arma_data['ClassificazioneEuropea'] = ''
            finally:
                conn.close()

        # Resto dell’inizializzazione UI
        self.arma_data = arma_data
        self.detentore_id = detentore_id
        self.setWindowTitle("Gestione Arma")
        self.setMinimumWidth(850)
        self.setMinimumHeight(600)
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()

        if arma_data:
            self.populate_fields(arma_data)

        convert_all_lineedits_to_uppercase(self)

    def on_motivo_changed(self, index):
        """Gestisce la visibilità del campo motivo personalizzato"""
        is_altro = self.comboMotivi.currentText() == "ALTRO (SPECIFICARE)"
        self.motivoPersonalizzatoLabel.setVisible(is_altro)
        self.motivoPersonalizzatoEdit.setVisible(is_altro)

    def convert_to_uppercase(self):
        """Converte il testo dell'oggetto chiamante in maiuscolo"""
        sender = self.sender()
        cursor_pos = sender.cursorPosition()
        sender.setText(sender.text().upper())
        sender.setCursorPosition(cursor_pos)

    def get_motivo_completo(self):
        """Restituisce il motivo formattato per il database"""
        motivo_principale = self.comboMotivi.currentText()

        if motivo_principale == "ALTRO (SPECIFICARE)":
            motivo_base = self.motivoPersonalizzatoEdit.text().strip() or "NON SPECIFICATO"
        else:
            motivo_base = motivo_principale

        # Aggiungi dettagli documento se presenti
        has_doc_details = (self.tipoDocumentoEdit.text().strip() or
                           self.numeroDocumentoEdit.text().strip() or
                           self.enteRilascioEdit.text().strip())

        if has_doc_details:
            doc_tipo = self.tipoDocumentoEdit.text().strip() or "DOC"
            doc_numero = self.numeroDocumentoEdit.text().strip() or "N/D"
            doc_data = self.dataDocumentoEdit.date().toString("dd/MM/yyyy")
            doc_ente = self.enteRilascioEdit.text().strip() or "N/D"

            motivo_base += f" - RIF: {doc_tipo} N.{doc_numero} DEL {doc_data} ({doc_ente})"

        # Aggiungi note aggiuntive se presenti
        note = self.noteAggiuntiveEdit.text().strip()
        if note:
            motivo_base += f" - NOTE: {note}"

        return motivo_base


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Per testare, si passa None per arma_data e un detentore id fittizio (es. 1)
    dialog = ArmaDialog(detentore_id=1)
    dialog.exec_()