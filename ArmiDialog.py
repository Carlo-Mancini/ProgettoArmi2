import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QGroupBox, QPushButton, QHBoxLayout
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
        self.setMinimumWidth(800)

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
        self.modifyButton = QPushButton("Modifica Arma")
        self.deleteButton = QPushButton("Cancella Arma")
        self.transferButton = QPushButton("Trasferisci Arma")

    def _create_arma_tab(self):
        """Crea la tab con i dettagli dell'arma"""
        self.tab_arma = QWidget()
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

        form_arma = QFormLayout()
        form_arma.addRow("Tipo Arma:", self.tipoArmaEdit)
        form_arma.addRow("Marca Arma:", self.marcaArmaEdit)
        form_arma.addRow("Modello Arma:", self.modelloArmaEdit)
        form_arma.addRow("Tipologia Arma:", self.tipologiaArmaEdit)
        form_arma.addRow("Matricola:", self.matricolaEdit)
        form_arma.addRow("Calibro Arma:", self.calibroArmaEdit)
        form_arma.addRow("Matricola Canna:", self.matricolaCannaEdit)
        form_arma.addRow("Lunghezza Canna:", self.lunghezzaCannaEdit)
        form_arma.addRow("Numero Canne:", self.numeroCanneEdit)
        form_arma.addRow("Arma Lunga/Corta:", self.armaLungaCortaEdit)
        form_arma.addRow("Tipo Canna:", self.tipoCannaEdit)
        form_arma.addRow("Categoria Arma:", self.categoriaArmaEdit)
        form_arma.addRow("Funzionamento Arma:", self.funzionamentoArmaEdit)
        form_arma.addRow("Caricamento Arma:", self.caricamentoArmaEdit)
        form_arma.addRow("Punzoni Arma:", self.punzoniArmaEdit)
        form_arma.addRow("Stato Produzione Arma:", self.statoProduzioneArmaEdit)
        form_arma.addRow("ExOrdDem:", self.exOrdDemEdit)
        form_arma.addRow("Tipo Munizioni:", self.tipoMunizioniEdit)
        form_arma.addRow("Quantita Munizioni:", self.quantitaMunizioniEdit)
        form_arma.addRow("Tipo Bossolo:", self.tipoBossoloEdit)
        form_arma.addRow("Tipo Cedente:", self.tipoCedenteEdit)
        form_arma.addRow("Note Arma:", self.noteArmaEdit)

        group_arma = QGroupBox("Dettagli Arma")
        group_arma.setLayout(form_arma)

        arma_layout = QVBoxLayout()
        arma_layout.addWidget(group_arma)
        self.tab_arma.setLayout(arma_layout)

    def _create_cedente_tab(self):
        """Crea la tab con i dati del cedente"""
        self.tab_cedente = QWidget()
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

        form_cedente = QFormLayout()
        form_cedente.addRow("Cognome Cedente:", self.cognomeCedenteEdit)
        form_cedente.addRow("Nome Cedente:", self.nomeCedenteEdit)
        form_cedente.addRow("Data Nascita Cedente:", self.dataNascitaCedenteEdit)
        form_cedente.addRow("Luogo Nascita Cedente:", self.luogoNascitaCedenteEdit)
        form_cedente.addRow("Sigla Provincia Residenza Cedente:", self.siglaProvinciaResidenzaCedenteEdit)
        form_cedente.addRow("Comune Residenza Cedente:", self.comuneResidenzaCedenteEdit)
        form_cedente.addRow("Sigla Provincia Nascita Cedente:", self.siglaProvinciaNascitaCedenteEdit)
        form_cedente.addRow("Tipo Via Residenza Cedente:", self.tipoViaResidenzaCedenteEdit)
        form_cedente.addRow("Indirizzo Residenza Cedente:", self.indirizzoResidenzaCedenteEdit)
        form_cedente.addRow("Civico Residenza Cedente:", self.civicoResidenzaCedenteEdit)
        form_cedente.addRow("Telefono Cedente:", self.telefonoCedenteEdit)

        group_cedente = QGroupBox("Dati Cedente")
        group_cedente.setLayout(form_cedente)

        cedente_layout = QVBoxLayout()
        cedente_layout.addWidget(group_cedente)
        self.tab_cedente.setLayout(cedente_layout)

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

            print("ID_ArmaDetenuta:", self.arma_data.get('ID_ArmaDetenuta') if self.arma_data else None)

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
            from TransferimentoDialog import TransferimentoDialog
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