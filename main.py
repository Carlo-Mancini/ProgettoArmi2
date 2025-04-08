import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QListWidget,
    QHBoxLayout, QMessageBox, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QCompleter
)
from PyQt5.QtCore import Qt

from Detentori import InserisciDetentoreDialog
from Storico_Movimenti_Armi import StoricoMovimentiArmaDialog
from Utility import cerca_arma_per_matricola  # se usato, altrimenti puoi rimuovere

# Dialog per visualizzare la lista dei Detentori
class DetentoriListDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lista Detentori")
        self.setMinimumWidth(400)
        self.detentori = []
        self.initUI()
        self.load_detentori_from_db()
        self.refreshList()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)

        # Pulsanti
        btn_layout = QHBoxLayout()
        self.newButton = QPushButton("Nuovo Detentore")
        self.updateButton = QPushButton("Aggiorna Detentore")
        self.deleteButton = QPushButton("Elimina Detentore")
        btn_layout.addWidget(self.newButton)
        btn_layout.addWidget(self.updateButton)
        btn_layout.addWidget(self.deleteButton)
        layout.addLayout(btn_layout)

        self.newButton.clicked.connect(self.newDetentore)
        self.updateButton.clicked.connect(self.updateDetentore)
        self.deleteButton.clicked.connect(self.deleteDetentore)
        self.listWidget.itemDoubleClicked.connect(self.editDetentore)

    def load_detentori_from_db(self):
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM detentori")
            rows = cursor.fetchall()
            conn.close()
            # Ordine dei campi deve corrispondere al database
            columns = ["id", "nome", "cognome", "fascicoloPersonale", "dataNascita", "luogoNascita",
                       "siglaProvinciaNascita", "sesso", "codiceFiscale", "comuneResidenza", "siglaProvinciaResidenza",
                       "tipoVia", "via", "civico", "telefono", "tipologiaTitolo", "enteRilascio", "provinciaEnteRilascio",
                       "dataRilascio", "numeroPortoArmi", "tipoLuogoDetenzione", "comuneDetenzione", "siglaProvinciaDetenzione",
                       "tipoViaDetenzione", "viaDetenzione", "civicoDetenzione", "tipoDocumento", "numeroDocumento",
                       "dataRilascioDocumento", "enteRilascioDocumento", "comuneEnteRilascioDocumento"]
            self.detentori = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei detentori:\n{e}")

    def refreshList(self):
        self.listWidget.clear()
        for det in self.detentori:
            self.listWidget.addItem(f"{det['nome']} {det['cognome']}")

    def getSelectedDetentore(self):
        selected_items = self.listWidget.selectedItems()
        if selected_items:
            index = self.listWidget.row(selected_items[0])
            return self.detentori[index]
        return None

    def newDetentore(self):
        dialog = InserisciDetentoreDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_detentori_from_db()
            self.refreshList()

    def updateDetentore(self):
        selected = self.getSelectedDetentore()
        if selected:
            dialog = InserisciDetentoreDialog(detentore_data=selected)
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.refreshList()

    def deleteDetentore(self):
        selected = self.getSelectedDetentore()
        if selected:
            reply = QMessageBox.question(
                self,
                "Conferma Eliminazione",
                "Sei sicuro di voler eliminare questo detentore?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    conn = sqlite3.connect("gestione_armi.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM detentori WHERE ID_Detentore = ?", (selected['id'],))
                    conn.commit()
                    conn.close()
                    self.load_detentori_from_db()
                    self.refreshList()
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile eliminare il detentore:\n{e}")

    def editDetentore(self, item):
        index = self.listWidget.row(item)
        det = self.detentori[index]
        dialog = InserisciDetentoreDialog(detentore_data=det)
        if dialog.exec_() == QDialog.Accepted:
            self.load_detentori_from_db()
            self.refreshList()


# Dialog per la ricerca dello storico trasferimenti (basato sulla matricola)
class RicercaStoricoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ricerca Storico Trasferimenti")
        self.resize(800, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Layout di ricerca
        search_layout = QHBoxLayout()
        self.matricolaEdit = QLineEdit()
        self.matricolaEdit.setPlaceholderText("Inserisci matricola dell'arma...")
        self.btnRicerca = QPushButton("Ricerca")
        search_layout.addWidget(self.matricolaEdit)
        search_layout.addWidget(self.btnRicerca)
        layout.addLayout(search_layout)

        # Tabella per visualizzare i trasferimenti
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Data", "Tipo Movimento", "Cedente", "Destinatario", "Note", "Altro"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.btnRicerca.clicked.connect(self.ricerca_storico)

    def ricerca_storico(self):
        matricola = self.matricolaEdit.text().strip()
        if not matricola:
            QMessageBox.warning(self, "Attenzione", "Inserisci la matricola per la ricerca.")
            return
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            query = """
                SELECT DataMovimento, TipoMovimento, 
                       CognomeCedente || ' ' || NomeCedente AS Cedente,
                       CognomeDestinatario || ' ' || NomeDestinatario AS Destinatario,
                       Note, AltroCampo
                FROM MovimentiArma
                WHERE UPPER(Matricola) = ?
                ORDER BY DataMovimento DESC
            """
            cursor.execute(query, (matricola.upper(),))
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile eseguire la ricerca:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)
        if not rows:
            QMessageBox.information(self, "Nessun risultato", "Nessun trasferimento trovato per la matricola inserita.")


# Finestra principale
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Armi - Main")
        self.resize(400, 200)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        btnDetentori = QPushButton("Detentori")
        btnStorico = QPushButton("Storico Trasferimenti Armi")
        layout.addWidget(btnDetentori)
        layout.addWidget(btnStorico)

        btnDetentori.clicked.connect(self.openDetentoriList)
        btnStorico.clicked.connect(self.apriRicercaStorico)

    def openDetentoriList(self):
        dialog = DetentoriListDialog()
        dialog.exec_()

    def apriRicercaStorico(self):
        dialog = RicercaStoricoDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
