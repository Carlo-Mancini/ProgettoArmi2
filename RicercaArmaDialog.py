import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QGroupBox,
    QGridLayout, QApplication, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Storico_Movimenti_Armi import StoricoMovimentiArmaDialog


class RicercaArmaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ricerca Arma")
        self.resize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Sezione di ricerca
        search_group = QGroupBox("Filtri di Ricerca")
        search_layout = QGridLayout()

        # Prima riga: Marca, Modello, Matricola
        self.marca_label = QLabel("Marca:")
        self.marca_input = QLineEdit()
        self.marca_input.setPlaceholderText("Inserisci marca...")
        search_layout.addWidget(self.marca_label, 0, 0)
        search_layout.addWidget(self.marca_input, 0, 1)

        self.modello_label = QLabel("Modello:")
        self.modello_input = QLineEdit()
        self.modello_input.setPlaceholderText("Inserisci modello...")
        search_layout.addWidget(self.modello_label, 0, 2)
        search_layout.addWidget(self.modello_input, 0, 3)

        self.matricola_label = QLabel("Matricola:")
        self.matricola_input = QLineEdit()
        self.matricola_input.setPlaceholderText("Inserisci matricola...")
        search_layout.addWidget(self.matricola_label, 0, 4)
        search_layout.addWidget(self.matricola_input, 0, 5)

        # Seconda riga: Calibro, Tipo Arma, Detentore
        self.calibro_label = QLabel("Calibro:")
        self.calibro_input = QLineEdit()
        self.calibro_input.setPlaceholderText("Inserisci calibro...")
        search_layout.addWidget(self.calibro_label, 1, 0)
        search_layout.addWidget(self.calibro_input, 1, 1)

        self.tipo_label = QLabel("Tipo Arma:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Tutti")
        self.tipo_combo.addItems(["Pistola", "Fucile", "Revolver", "Carabina", "Altro"])
        search_layout.addWidget(self.tipo_label, 1, 2)
        search_layout.addWidget(self.tipo_combo, 1, 3)

        self.detentore_label = QLabel("Cognome Detentore:")
        self.detentore_input = QLineEdit()
        self.detentore_input.setPlaceholderText("Inserisci cognome detentore...")
        search_layout.addWidget(self.detentore_label, 1, 4)
        search_layout.addWidget(self.detentore_input, 1, 5)

        # Terza riga: pulsanti di ricerca
        self.search_button = QPushButton("Cerca")
        self.search_button.setMinimumWidth(120)
        self.search_button.setIcon(QApplication.style().standardIcon(QApplication.style().SP_FileDialogContentsView))
        search_layout.addWidget(self.search_button, 2, 1)

        self.reset_button = QPushButton("Reimposta Filtri")
        self.reset_button.setMinimumWidth(120)
        self.reset_button.setIcon(QApplication.style().standardIcon(QApplication.style().SP_DialogResetButton))
        search_layout.addWidget(self.reset_button, 2, 3)

        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Tabella risultati
        result_label = QLabel("Risultati della ricerca")
        result_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(result_label)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels([
            "ID", "Marca", "Modello", "Matricola", "Calibro", "Tipo", "Detentore"
        ])
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setStyleSheet("QTableView::item {padding: 5px;}")

        # Imposta la larghezza delle colonne
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Marca
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Modello
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Matricola
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Calibro
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Detentore

        main_layout.addWidget(self.result_table, 1)  # Stretch factor 1

        # Pulsanti azione
        buttons_layout = QHBoxLayout()

        self.view_button = QPushButton("Visualizza Storico")
        self.view_button.setMinimumWidth(150)
        self.view_button.setIcon(QApplication.style().standardIcon(QApplication.style().SP_FileDialogDetailedView))
        self.view_button.setEnabled(False)  # Disabilitato finché non si seleziona un'arma
        buttons_layout.addWidget(self.view_button)

        buttons_layout.addStretch()

        self.close_button = QPushButton("Chiudi")
        self.close_button.setMinimumWidth(120)
        self.close_button.setIcon(QApplication.style().standardIcon(QApplication.style().SP_DialogCloseButton))
        buttons_layout.addWidget(self.close_button)

        main_layout.addLayout(buttons_layout)

        # Connessione segnali
        self.search_button.clicked.connect(self.search_armi)
        self.reset_button.clicked.connect(self.reset_filters)
        self.close_button.clicked.connect(self.reject)
        self.view_button.clicked.connect(self.show_storico)
        self.result_table.itemSelectionChanged.connect(self.toggle_view_button)
        self.result_table.itemDoubleClicked.connect(self.show_storico)

    def search_armi(self):
        """Cerca le armi nel database in base ai filtri specificati"""
        marca = self.marca_input.text().strip()
        modello = self.modello_input.text().strip()
        matricola = self.matricola_input.text().strip()
        calibro = self.calibro_input.text().strip()
        tipo = self.tipo_combo.currentText()
        detentore = self.detentore_input.text().strip()

        where_clauses = []
        params = []

        if marca:
            where_clauses.append("LOWER(a.MarcaArma) LIKE ?")
            params.append(f"%{marca.lower()}%")

        if modello:
            where_clauses.append("LOWER(a.ModelloArma) LIKE ?")
            params.append(f"%{modello.lower()}%")

        if matricola:
            where_clauses.append("LOWER(a.Matricola) LIKE ?")
            params.append(f"%{matricola.lower()}%")

        if calibro:
            where_clauses.append("LOWER(a.CalibroArma) LIKE ?")
            params.append(f"%{calibro.lower()}%")

        if tipo and tipo != "Tutti":
            where_clauses.append("a.TipoArma = ?")
            params.append(tipo)

        if detentore:
            where_clauses.append("LOWER(d.Cognome) LIKE ?")
            params.append(f"%{detentore.lower()}%")

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            query = f"""
                SELECT a.ID_ArmaDetenuta, a.MarcaArma, a.ModelloArma, a.Matricola, 
                       a.CalibroArma, a.TipoArma, d.Cognome || ' ' || d.Nome as Detentore
                FROM armi a
                LEFT JOIN detentori d ON a.ID_Detentore = d.ID_Detentore
                WHERE {where_clause}
                ORDER BY a.MarcaArma, a.ModelloArma
            """

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            # Popolamento tabella risultati
            self.result_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value or ''))
                    if col_idx == 0:  # ID colonna
                        item.setTextAlignment(Qt.AlignCenter)
                    self.result_table.setItem(row_idx, col_idx, item)

            if len(rows) == 0:
                QMessageBox.information(self, "Ricerca", "Nessuna arma trovata con i criteri specificati.")
                self.view_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca:\n{e}")

    def reset_filters(self):
        """Reimposta tutti i filtri di ricerca"""
        self.marca_input.clear()
        self.modello_input.clear()
        self.matricola_input.clear()
        self.calibro_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.detentore_input.clear()
        self.result_table.setRowCount(0)
        self.view_button.setEnabled(False)

    def toggle_view_button(self):
        """Abilita/disabilita il pulsante Visualizza Storico in base alla selezione"""
        self.view_button.setEnabled(len(self.result_table.selectedItems()) > 0)

    def show_storico(self):
        """Apre la finestra di storico movimenti per l'arma selezionata"""
        selected_rows = self.result_table.selectionModel().selectedRows()
        if not selected_rows:
            selected_items = self.result_table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
            else:
                QMessageBox.warning(self, "Attenzione", "Seleziona un'arma per visualizzare lo storico.")
                return
        else:
            row = selected_rows[0].row()

        # Recupera l'ID dell'arma selezionata
        id_arma = int(self.result_table.item(row, 0).text())

        # Apri la finestra di storico movimenti
        storico_dialog = StoricoMovimentiArmaDialog(id_arma, self)
        storico_dialog.exec_()