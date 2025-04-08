import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QMessageBox, QFormLayout, QSplitter, QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon
from Utility import convert_all_lineedits_to_uppercase


class TransferimentoDialog(QDialog):
    def __init__(self, arma_id=None, cedente_id=None, current_detentore=None, parent=None):
        super().__init__(parent)
        self.arma_id = arma_id
        self.cedente_id = cedente_id
        self.current_detentore = current_detentore
        self.selected_detentore_id = None
        self.selected_detentore_data = None

        self.setWindowTitle("Trasferimento Arma")
        self.setMinimumWidth(900)
        self.setMinimumHeight(650)

        # Configura l'interfaccia
        self.setup_ui()
        self.load_arma_details()

        # Timer per ritardare la ricerca durante la digitazione
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Creazione dello splitter principale
        splitter = QSplitter(Qt.Vertical)

        # ---- SEZIONE SUPERIORE: INFORMAZIONI ARMA ----
        arma_widget = QFrame()
        arma_layout = QVBoxLayout(arma_widget)

        # Dettagli dell'arma
        arma_group = QGroupBox("Dettagli Arma da Trasferire")
        arma_grid = QGridLayout()

        # Prima riga
        self.marcaLabel = QLabel("Marca: ")
        self.marcaValueLabel = QLabel("")
        self.marcaValueLabel.setFont(QFont("Arial", 10, QFont.Bold))

        self.modelloLabel = QLabel("Modello: ")
        self.modelloValueLabel = QLabel("")
        self.modelloValueLabel.setFont(QFont("Arial", 10, QFont.Bold))

        # Seconda riga
        self.matricolaLabel = QLabel("Matricola: ")
        self.matricolaValueLabel = QLabel("")
        self.matricolaValueLabel.setFont(QFont("Arial", 10, QFont.Bold))

        self.calibroLabel = QLabel("Calibro: ")
        self.calibroValueLabel = QLabel("")
        self.calibroValueLabel.setFont(QFont("Arial", 10, QFont.Bold))

        # Terza riga
        self.detentoreAttualeLabel = QLabel("Detentore Attuale: ")
        self.detentoreAttualeValueLabel = QLabel("")
        self.detentoreAttualeValueLabel.setFont(QFont("Arial", 10, QFont.Bold))

        arma_grid.addWidget(self.marcaLabel, 0, 0)
        arma_grid.addWidget(self.marcaValueLabel, 0, 1)
        arma_grid.addWidget(self.modelloLabel, 0, 2)
        arma_grid.addWidget(self.modelloValueLabel, 0, 3)

        arma_grid.addWidget(self.matricolaLabel, 1, 0)
        arma_grid.addWidget(self.matricolaValueLabel, 1, 1)
        arma_grid.addWidget(self.calibroLabel, 1, 2)
        arma_grid.addWidget(self.calibroValueLabel, 1, 3)

        arma_grid.addWidget(self.detentoreAttualeLabel, 2, 0)
        arma_grid.addWidget(self.detentoreAttualeValueLabel, 2, 1, 1, 3)

        arma_group.setLayout(arma_grid)
        arma_layout.addWidget(arma_group)
        splitter.addWidget(arma_widget)

        # ---- SEZIONE CENTRALE: RICERCA DETENTORI ----
        search_widget = QFrame()
        search_layout = QVBoxLayout(search_widget)

        search_group = QGroupBox("Cerca Nuovo Detentore")
        search_main = QVBoxLayout()

        # Criteri di ricerca
        search_grid = QGridLayout()

        self.cognomeSearchLabel = QLabel("Cognome:")
        self.cognomeSearchEdit = QLineEdit()
        self.cognomeSearchEdit.setPlaceholderText("Inserisci il cognome...")

        self.nomeSearchLabel = QLabel("Nome:")
        self.nomeSearchEdit = QLineEdit()
        self.nomeSearchEdit.setPlaceholderText("Inserisci il nome...")

        self.codFiscSearchLabel = QLabel("Codice Fiscale:")
        self.codFiscSearchEdit = QLineEdit()
        self.codFiscSearchEdit.setPlaceholderText("Inserisci il codice fiscale...")

        self.fascicoloSearchLabel = QLabel("Fascicolo:")
        self.fascicoloSearchEdit = QLineEdit()
        self.fascicoloSearchEdit.setPlaceholderText("Inserisci il numero fascicolo...")

        search_grid.addWidget(self.cognomeSearchLabel, 0, 0)
        search_grid.addWidget(self.cognomeSearchEdit, 0, 1)
        search_grid.addWidget(self.nomeSearchLabel, 0, 2)
        search_grid.addWidget(self.nomeSearchEdit, 0, 3)

        search_grid.addWidget(self.codFiscSearchLabel, 1, 0)
        search_grid.addWidget(self.codFiscSearchEdit, 1, 1)
        search_grid.addWidget(self.fascicoloSearchLabel, 1, 2)
        search_grid.addWidget(self.fascicoloSearchEdit, 1, 3)

        search_main.addLayout(search_grid)

        # Pulsanti di ricerca
        search_buttons = QHBoxLayout()
        self.searchButton = QPushButton("Cerca")
        self.searchButton.setIcon(QIcon.fromTheme("system-search"))
        self.searchButton.setMinimumWidth(120)
        self.clearButton = QPushButton("Pulisci")
        self.clearButton.setMinimumWidth(120)
        search_buttons.addWidget(self.searchButton)
        search_buttons.addWidget(self.clearButton)
        search_buttons.addStretch()

        search_main.addLayout(search_buttons)

        # Tabella risultati
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(6)
        self.resultTable.setHorizontalHeaderLabels(
            ["ID", "Cognome", "Nome", "Codice Fiscale", "Comune Residenza", "Fascicolo"])
        self.resultTable.verticalHeader().setVisible(False)
        self.resultTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.resultTable.setSelectionMode(QTableWidget.SingleSelection)
        self.resultTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resultTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Imposta la colonna ID come nascosta, ma manteniamo i dati
        self.resultTable.setColumnHidden(0, True)

        # Configura le colonne per adattarsi al contenuto
        header = self.resultTable.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        search_main.addWidget(self.resultTable)
        search_group.setLayout(search_main)
        search_layout.addWidget(search_group)
        splitter.addWidget(search_widget)

        # ---- SEZIONE INFERIORE: DETTAGLI TRASFERIMENTO ----
        transfer_widget = QFrame()
        transfer_layout = QVBoxLayout(transfer_widget)

        transfer_group = QGroupBox("Conferma Trasferimento")
        transfer_grid = QGridLayout()

        # Detentore selezionato
        self.selectedDetentoreLabel = QLabel("Nuovo Detentore:")
        self.selectedDetentoreValueLabel = QLabel("Nessun detentore selezionato")
        self.selectedDetentoreValueLabel.setStyleSheet("font-weight: bold; color: blue;")

        # Data trasferimento
        self.dataLabel = QLabel("Data Trasferimento:")
        self.dataEdit = QLineEdit()
        self.dataEdit.setPlaceholderText("GG/MM/AAAA")

        # Motivo trasferimento
        self.motivoLabel = QLabel("Motivo Trasferimento:")
        self.motivoCombo = QComboBox()
        self.motivoCombo.addItems(["Vendita", "Donazione", "Eredità", "Comodato", "Altro"])

        # Note
        self.noteLabel = QLabel("Note:")
        self.noteEdit = QLineEdit()

        transfer_grid.addWidget(self.selectedDetentoreLabel, 0, 0)
        transfer_grid.addWidget(self.selectedDetentoreValueLabel, 0, 1, 1, 3)

        transfer_grid.addWidget(self.dataLabel, 1, 0)
        transfer_grid.addWidget(self.dataEdit, 1, 1)
        transfer_grid.addWidget(self.motivoLabel, 1, 2)
        transfer_grid.addWidget(self.motivoCombo, 1, 3)

        transfer_grid.addWidget(self.noteLabel, 2, 0)
        transfer_grid.addWidget(self.noteEdit, 2, 1, 1, 3)

        transfer_group.setLayout(transfer_grid)
        transfer_layout.addWidget(transfer_group)
        splitter.addWidget(transfer_widget)

        # Imposta le dimensioni relative delle sezioni dello splitter
        splitter.setSizes([150, 350, 150])

        # Aggiungi lo splitter al layout principale
        main_layout.addWidget(splitter)

        # Pulsanti finali
        buttons_layout = QHBoxLayout()
        self.transferButton = QPushButton("Conferma Trasferimento")
        self.transferButton.setMinimumWidth(180)
        self.transferButton.setEnabled(False)  # Inizialmente disabilitato
        self.cancelButton = QPushButton("Annulla")
        self.cancelButton.setMinimumWidth(120)

        buttons_layout.addWidget(self.transferButton)
        buttons_layout.addWidget(self.cancelButton)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Connessione segnali
        self.searchButton.clicked.connect(self.perform_search)
        self.clearButton.clicked.connect(self.clear_search)
        self.resultTable.itemSelectionChanged.connect(self.update_selected_detentore)
        self.transferButton.clicked.connect(self.execute_transfer)
        self.cancelButton.clicked.connect(self.reject)

        # Connessione dei campi di ricerca con timer per la ricerca dinamica
        self.cognomeSearchEdit.textChanged.connect(self.delayed_search)
        self.nomeSearchEdit.textChanged.connect(self.delayed_search)
        self.codFiscSearchEdit.textChanged.connect(self.delayed_search)
        self.fascicoloSearchEdit.textChanged.connect(self.delayed_search)

        # Doppio click sulla tabella seleziona il detentore
        self.resultTable.cellDoubleClicked.connect(self.select_detentore)

        # Converti tutto in maiuscolo
        convert_all_lineedits_to_uppercase(self)

    def load_arma_details(self):
        """Carica e visualizza i dettagli dell'arma da trasferire"""
        if not self.arma_id:
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Ottieni i dettagli dell'arma
            cursor.execute("""
                SELECT a.MarcaArma, a.ModelloArma, a.Matricola, a.CalibroArma,
                       d.Cognome, d.Nome, d.CodiceFiscale
                FROM armi a
                LEFT JOIN detentori d ON a.ID_Detentore = d.ID_Detentore
                WHERE a.ID_ArmaDetenuta = ?
            """, (self.arma_id,))

            result = cursor.fetchone()
            if result:
                marca, modello, matricola, calibro, cognome_det, nome_det, cf_det = result

                self.marcaValueLabel.setText(marca or "")
                self.modelloValueLabel.setText(modello or "")
                self.matricolaValueLabel.setText(matricola or "")
                self.calibroValueLabel.setText(calibro or "")

                detentore_info = f"{cognome_det or ''} {nome_det or ''}"
                if cf_det:
                    detentore_info += f" (CF: {cf_det})"
                self.detentoreAttualeValueLabel.setText(detentore_info)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei dati dell'arma: {str(e)}")

    def delayed_search(self):
        """Ritarda la ricerca per evitare troppe query durante la digitazione"""
        self.search_timer.start(500)  # Ritardo di 500ms

    def perform_search(self):
        """Esegue la ricerca dei detentori in base ai criteri inseriti"""
        cognome = self.cognomeSearchEdit.text().strip()
        nome = self.nomeSearchEdit.text().strip()
        codice_fiscale = self.codFiscSearchEdit.text().strip()
        fascicolo = self.fascicoloSearchEdit.text().strip()

        # Verifica se almeno un criterio è valorizzato
        if not (cognome or nome or codice_fiscale or fascicolo):
            self.resultTable.setRowCount(0)
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Costruisci la query dinamicamente in base ai criteri inseriti
            query = """
                SELECT ID_Detentore, Cognome, Nome, CodiceFiscale, ComuneResidenza, FascicoloPersonale
                FROM detentori
                WHERE 1=1
            """
            params = []

            if cognome:
                query += " AND Cognome LIKE ?"
                params.append(f"%{cognome}%")

            if nome:
                query += " AND Nome LIKE ?"
                params.append(f"%{nome}%")

            if codice_fiscale:
                query += " AND CodiceFiscale LIKE ?"
                params.append(f"%{codice_fiscale}%")

            if fascicolo:
                query += " AND FascicoloPersonale LIKE ?"
                params.append(f"%{fascicolo}%")

            # Escludiamo il detentore corrente
            if self.current_detentore:
                query += " AND ID_Detentore <> ?"
                params.append(self.current_detentore)

            # Aggiungi ordinamento
            query += " ORDER BY Cognome, Nome"

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Popola la tabella con i risultati
            self.resultTable.setRowCount(len(results))
            for row, (id_detentore, cognome, nome, cf, comune, fascicolo) in enumerate(results):
                id_item = QTableWidgetItem(str(id_detentore))
                id_item.setData(Qt.UserRole, id_detentore)  # Conserviamo l'ID come dato ausiliario

                cognome_item = QTableWidgetItem(cognome or "")
                nome_item = QTableWidgetItem(nome or "")
                cf_item = QTableWidgetItem(cf or "")
                comune_item = QTableWidgetItem(comune or "")
                fascicolo_item = QTableWidgetItem(fascicolo or "")

                self.resultTable.setItem(row, 0, id_item)
                self.resultTable.setItem(row, 1, cognome_item)
                self.resultTable.setItem(row, 2, nome_item)
                self.resultTable.setItem(row, 3, cf_item)
                self.resultTable.setItem(row, 4, comune_item)
                self.resultTable.setItem(row, 5, fascicolo_item)

            conn.close()

            # Imposta il messaggio appropriato se non ci sono risultati
            if len(results) == 0:
                QMessageBox.information(self, "Ricerca", "Nessun detentore trovato con i criteri specificati.")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca: {str(e)}")

    def clear_search(self):
        """Pulisce i campi di ricerca e la tabella risultati"""
        self.cognomeSearchEdit.clear()
        self.nomeSearchEdit.clear()
        self.codFiscSearchEdit.clear()
        self.fascicoloSearchEdit.clear()
        self.resultTable.setRowCount(0)
        self.selected_detentore_id = None
        self.selected_detentore_data = None
        self.selectedDetentoreValueLabel.setText("Nessun detentore selezionato")
        self.transferButton.setEnabled(False)

    def update_selected_detentore(self):
        """Aggiorna l'etichetta con il detentore selezionato"""
        selected_items = self.resultTable.selectedItems()
        if not selected_items:
            self.selected_detentore_id = None
            self.selected_detentore_data = None
            self.selectedDetentoreValueLabel.setText("Nessun detentore selezionato")
            self.transferButton.setEnabled(False)
            return

        # Ottieni la riga selezionata
        row = selected_items[0].row()
        id_item = self.resultTable.item(row, 0)
        cognome_item = self.resultTable.item(row, 1)
        nome_item = self.resultTable.item(row, 2)
        cf_item = self.resultTable.item(row, 3)

        if id_item and cognome_item and nome_item:
            self.selected_detentore_id = id_item.data(Qt.UserRole)
            self.selected_detentore_data = {
                'id': self.selected_detentore_id,
                'cognome': cognome_item.text(),
                'nome': nome_item.text(),
                'cf': cf_item.text() if cf_item else ""
            }

            detentore_info = f"{cognome_item.text()} {nome_item.text()}"
            if cf_item and cf_item.text():
                detentore_info += f" (CF: {cf_item.text()})"

            self.selectedDetentoreValueLabel.setText(detentore_info)
            self.transferButton.setEnabled(True)

    def select_detentore(self, row, column):
        """Doppio click su una riga seleziona il detentore"""
        if self.selected_detentore_id:
            reply = QMessageBox.question(self, "Conferma Selezione",
                                         f"Vuoi selezionare questo detentore per il trasferimento?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.dataEdit.setFocus()

    def execute_transfer(self):
        """Esegue il trasferimento dell'arma al nuovo detentore"""
        if not self.selected_detentore_id:
            QMessageBox.warning(self, "Attenzione", "Nessun detentore selezionato.")
            return

        if not self.validate_transfer_data():
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Aggiorna il detentore dell'arma
            cursor.execute("""
                UPDATE armi
                SET ID_Detentore = ?
                WHERE ID_ArmaDetenuta = ?
            """, (self.selected_detentore_id, self.arma_id))

            # Registra il trasferimento nella tabella dei trasferimenti
            cursor.execute("""
                INSERT INTO trasferimenti 
                (ID_Arma, ID_Detentore_Cedente, ID_Detentore_Ricevente, Data_Trasferimento, Motivo_Trasferimento, Note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.arma_id,
                self.cedente_id,
                self.selected_detentore_id,
                self.dataEdit.text(),
                self.motivoCombo.currentText(),
                self.noteEdit.text()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Successo", "Trasferimento dell'arma completato con successo!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il trasferimento: {str(e)}")

    def validate_transfer_data(self):
        """Valida i dati del trasferimento"""
        data = self.dataEdit.text().strip()
        if not data:
            QMessageBox.warning(self, "Attenzione", "Inserire la data di trasferimento.")
            self.dataEdit.setFocus()
            return False

        # Qui si potrebbero aggiungere ulteriori validazioni sulla data

        return True


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = TransferimentoDialog(arma_id=1, cedente_id=1, current_detentore=1)
    dialog.exec_()