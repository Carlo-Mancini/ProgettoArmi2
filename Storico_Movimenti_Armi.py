import sqlite3
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt


class StoricoMovimentiArmaDialog(QDialog):
    def __init__(self, id_arma, parent=None):
        super().__init__(parent)
        self.id_arma = id_arma
        self.setWindowTitle("Storico Movimenti Arma")
        self.resize(1200, 500)

        # Layout principale
        main_layout = QVBoxLayout(self)

        # Creazione della QTableWidget
        self.table = QTableWidget()
        # Definiamo le colonne (corrispondono ai campi presenti nel database)
        columns = [
            "DataMovimento", "TipoMovimento",
            "CognomeCedente", "NomeCedente", "DataNascitaCedente", "LuogoNascitaCedente",
            "CognomeDestinatario", "NomeDestinatario", "DataNascitaDestinatario", "LuogoNascitaDestinatario",
            "Note"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        # Pulsante per chiudere
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

        # Carica i dati dal database
        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            query = """
                SELECT 
                    DataMovimento, TipoMovimento,
                    CognomeCedente, NomeCedente, DataNascitaCedente, LuogoNascitaCedente,
                    CognomeDestinatario, NomeDestinatario, DataNascitaDestinatario, LuogoNascitaDestinatario,
                    Note
                FROM MovimentiArma
                WHERE ID_ArmaDetenuta = ?
                ORDER BY DataMovimento DESC
            """
            cursor.execute(query, (self.id_arma,))
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)
