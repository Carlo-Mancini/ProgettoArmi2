import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QGroupBox, QPushButton, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QSizePolicy
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

        # Creazione dei campi di testo
        self.tipoArmaEdit = QLineEdit()
        self.marcaArmaEdit = QLineEdit()
        self.modelloArmaEdit = QLineEdit()
        self.tipologiaArmaEdit = QLineEdit()
        self.matricolaEdit = QLineEdit()
        self.calibroArmaEdit = QLineEdit()
        self.matricolaCannaEdit = QLineEdit()
        self.lunghezzaCannaEdit = QLineEdit()
        self.numeroCanneEdit = QLineEdit()
        self.armaLungaCortaEdit = QLineEdit()
        self.tipoCannaEdit = QLineEdit()
        self.categoriaArmaEdit = QLineEdit()
        self.funzionamentoArmaEdit = QLineEdit()
        self.caricamentoArmaEdit = QLineEdit()
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

    def create_arma_identification_group(self):
        """Crea il gruppo per i dati identificativi dell'arma"""
        self.group_identification = QGroupBox("Dati Identificativi")
        grid = QGridLayout()

        # Riga 1
        grid.addWidget(QLabel("Tipo Arma:"), 0, 0)
        grid.addWidget(self.tipoArmaEdit, 0, 1)
        grid.addWidget(QLabel("Marca:"), 0, 2)
        grid.addWidget(self.marcaArmaEdit, 0, 3)

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

    def populate_fields(self, data):
        """Popola i campi con i dati esistenti"""
        self.tipoArmaEdit.setText(data.get('TipoArma', ''))
        self.marcaArmaEdit.setText(data.get('MarcaArma', ''))
        self.modelloArmaEdit.setText(data.get('ModelloArma', ''))
        self.tipologiaArmaEdit.setText(data.get('TipologiaArma', ''))
        self.matricolaEdit.setText(data.get('Matricola', ''))
        self.calibroArmaEdit.setText(data.get('CalibroArma', ''))
        self.matricolaCannaEdit.setText(data.get('MatricolaCanna', ''))
        self.lunghezzaCannaEdit.setText(data.get('LunghezzaCanna', ''))
        self.numeroCanneEdit.setText(data.get('NumeroCanne', ''))
        self.armaLungaCortaEdit.setText(data.get('ArmaLungaCorta', ''))
        self.tipoCannaEdit.setText(data.get('TipoCanna', ''))
        self.categoriaArmaEdit.setText(data.get('CategoriaArma', ''))
        self.funzionamentoArmaEdit.setText(data.get('FunzionamentoArma', ''))
        self.caricamentoArmaEdit.setText(data.get('CaricamentoArma', ''))
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

    def save_arma(self):
        """Salva i dati dell'arma nel database"""
        try:
            # Verifica che almeno l'ID del detentore sia valorizzato per un nuovo inserimento
            if self.arma_data is None and self.detentore_id is None:
                raise ValueError("ID_Detentore non valorizzato. Impossibile salvare l'arma.")

            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Raccogli i dati
            tipoArma = self.tipoArmaEdit.text()
            marcaArma = self.marcaArmaEdit.text()
            modelloArma = self.modelloArmaEdit.text()
            tipologiaArma = self.tipologiaArmaEdit.text()
            matricola = self.matricolaEdit.text()
            calibroArma = self.calibroArmaEdit.text()
            matricolaCanna = self.matricolaCannaEdit.text()
            lunghezzaCanna = self.lunghezzaCannaEdit.text()
            numeroCanne = self.numeroCanneEdit.text()
            armaLungaCorta = self.armaLungaCortaEdit.text()
            tipoCanna = self.tipoCannaEdit.text()
            categoriaArma = self.categoriaArmaEdit.text()
            funzionamentoArma = self.funzionamentoArmaEdit.text()
            caricamentoArma = self.caricamentoArmaEdit.text()
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

            if self.arma_data and self.arma_data.get('ID_ArmaDetenuta'):
                # UPDATE per la modifica
                cursor.execute("""
                    UPDATE armi
                    SET TipoArma=?, MarcaArma=?, ModelloArma=?, TipologiaArma=?, Matricola=?, CalibroArma=?, MatricolaCanna=?, LunghezzaCanna=?, NumeroCanne=?,
                        ArmaLungaCorta=?, TipoCanna=?, CategoriaArma=?, FunzionamentoArma=?, CaricamentoArma=?, PunzoniArma=?, StatoProduzioneArma=?,
                        ExOrdDem=?, TipoMunizioni=?, QuantitaMunizioni=?, TipoBossolo=?, TipoCedente=?, NoteArma=?, CognomeCedente=?, NomeCedente=?,
                        DataNascitaCedente=?, LuogoNascitaCedente=?, SiglaProvinciaResidenzaCedente=?, ComuneResidenzaCedente=?, SiglaProvinciaNascitaCedente=?,
                        TipoViaResidenzaCedente=?, IndirizzoResidenzaCedente=?, CivicoResidenzaCedente=?, TelefonoCedente=?
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
                    self.arma_data.get('ID_ArmaDetenuta')
                ))
            else:
                # INSERT per un nuovo record
                cursor.execute("""
                    INSERT INTO armi (ID_Detentore, TipoArma, MarcaArma, ModelloArma, TipologiaArma, Matricola, CalibroArma, MatricolaCanna, LunghezzaCanna,
                        NumeroCanne, ArmaLungaCorta, TipoCanna, CategoriaArma, FunzionamentoArma, CaricamentoArma, PunzoniArma, StatoProduzioneArma,
                        ExOrdDem, TipoMunizioni, QuantitaMunizioni, TipoBossolo, TipoCedente, NoteArma, CognomeCedente, NomeCedente, DataNascitaCedente,
                        LuogoNascitaCedente, SiglaProvinciaResidenzaCedente, ComuneResidenzaCedente, SiglaProvinciaNascitaCedente, TipoViaResidenzaCedente,
                        IndirizzoResidenzaCedente, CivicoResidenzaCedente, TelefonoCedente)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.detentore_id, tipoArma, marcaArma, modelloArma, tipologiaArma, matricola, calibroArma,
                    matricolaCanna, lunghezzaCanna,
                    numeroCanne, armaLungaCorta, tipoCanna, categoriaArma, funzionamentoArma, caricamentoArma,
                    punzoniArma, statoProduzioneArma,
                    exOrdDem, tipoMunizioni, quantitaMunizioni, tipoBossolo, tipoCedente, noteArma, cognomeCedente,
                    nomeCedente,
                    dataNascitaCedente, luogoNascitaCedente, siglaProvinciaResidenzaCedente, comuneResidenzaCedente,
                    siglaProvinciaNascitaCedente,
                    tipoViaResidenzaCedente, indirizzoResidenzaCedente, civicoResidenzaCedente, telefonoCedente
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