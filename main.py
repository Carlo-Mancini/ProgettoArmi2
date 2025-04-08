import sys
import traceback
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QListWidget,
    QHBoxLayout, QMessageBox, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QCompleter, QLabel, QStyleFactory
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

try:
    from Detentori import InserisciDetentoreDialog
except Exception as e:
    print(f"Errore nell'importare InserisciDetentoreDialog: {e}")


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
                       "tipoVia", "via", "civico", "telefono", "tipologiaTitolo", "enteRilascio",
                       "provinciaEnteRilascio",
                       "dataRilascio", "numeroPortoArmi", "tipoLuogoDetenzione", "comuneDetenzione",
                       "siglaProvinciaDetenzione",
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
        try:
            dialog = InserisciDetentoreDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.refreshList()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aprire il form di inserimento:\n{e}")

    def updateDetentore(self):
        selected = self.getSelectedDetentore()
        if selected:
            try:
                dialog = InserisciDetentoreDialog(detentore_data=selected)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_detentori_from_db()
                    self.refreshList()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nell'aprire il form di modifica:\n{e}")

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
        try:
            dialog = InserisciDetentoreDialog(detentore_data=det)
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.refreshList()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aprire il form di modifica:\n{e}")


# Semplice dialog per la ricerca dell'arma
class SimpleRicercaArmaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Ricerca Arma per Storico")
        self.resize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Titolo
        title_label = QLabel("Ricerca Arma per Visualizzare lo Storico")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Istruzioni
        instructions = QLabel("Inserisci una matricola o parte di essa per cercare un'arma.")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Campo di ricerca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Inserisci matricola...")
        self.search_button = QPushButton("Cerca")
        self.search_button.setMinimumWidth(100)

        search_layout.addWidget(QLabel("Matricola:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Tabella risultati
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "ID", "Marca", "Modello", "Matricola", "Calibro"
        ])
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        layout.addWidget(self.result_table)

        # Pulsanti azione
        button_layout = QHBoxLayout()
        self.view_button = QPushButton("Visualizza Storico")
        self.view_button.setEnabled(False)
        self.close_button = QPushButton("Chiudi")

        button_layout.addWidget(self.view_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        # Connessione segnali
        self.search_button.clicked.connect(self.search_arma)
        self.close_button.clicked.connect(self.reject)
        self.view_button.clicked.connect(self.show_storico)
        self.result_table.itemSelectionChanged.connect(self.toggle_view_button)
        self.result_table.itemDoubleClicked.connect(self.show_storico)

    def search_arma(self):
        matricola = self.search_input.text().strip()
        if not matricola:
            QMessageBox.warning(self, "Attenzione", "Inserisci una matricola per la ricerca")
            return

        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID_ArmaDetenuta, MarcaArma, ModelloArma, Matricola, CalibroArma
                FROM armi
                WHERE Matricola LIKE ?
                ORDER BY MarcaArma, ModelloArma
            """, (f"%{matricola}%",))
            rows = cursor.fetchall()
            conn.close()

            self.result_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value or "")))

            if len(rows) == 0:
                QMessageBox.information(self, "Informazione", "Nessuna arma trovata con la matricola specificata.")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")

    def toggle_view_button(self):
        self.view_button.setEnabled(len(self.result_table.selectedItems()) > 0)

    def show_storico(self):
        selected = self.result_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona un'arma per visualizzare lo storico.")
            return

        row = selected[0].row()
        id_arma = int(self.result_table.item(row, 0).text())

        try:
            # Import qui per evitare import circolari
            from Storico_Movimenti_Armi import StoricoMovimentiArmaDialog
            dialog = StoricoMovimentiArmaDialog(id_arma, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aprire lo storico:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")


# Finestra principale
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Armi - Programma Principale")
        self.resize(600, 400)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Titolo
        title = QLabel("Sistema di Gestione Armi")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Descrizione
        desc = QLabel("Seleziona una delle operazioni disponibili")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Pulsanti principali
        btn_layout = QVBoxLayout()

        self.btn_detentori = QPushButton("Gestione Detentori")
        self.btn_detentori.setMinimumHeight(50)
        self.btn_detentori.setIcon(QIcon.fromTheme("system-users"))

        self.btn_storico = QPushButton("Storico Trasferimenti Armi")
        self.btn_storico.setMinimumHeight(50)
        self.btn_storico.setIcon(QIcon.fromTheme("document-properties"))

        btn_layout.addWidget(self.btn_detentori)
        btn_layout.addWidget(self.btn_storico)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Connessione segnali
        self.btn_detentori.clicked.connect(self.open_detentori)
        self.btn_storico.clicked.connect(self.open_ricerca_storico)

    def open_detentori(self):
        try:
            dialog = DetentoriListDialog()
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'apertura della gestione detentori:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")

    def open_ricerca_storico(self):
        try:
            # Utilizziamo la classe semplificata inclusa in questo file
            dialog = SimpleRicercaArmaDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'apertura della ricerca storico:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        print("Avvio dell'applicazione...")
        app = QApplication(sys.argv)

        # Utilizziamo il tema Fusion che è più moderno e professionale
        app.setStyle(QStyleFactory.create("Fusion"))

        print("Creazione della finestra principale...")
        window = MainWindow()
        print("Visualizzazione della finestra principale...")
        window.show()

        print("Avvio del ciclo di eventi...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Errore critico durante l'avvio dell'applicazione: {e}")
        print(traceback.format_exc())
        QMessageBox.critical(None, "Errore di Avvio",
                             f"Si è verificato un errore durante l'avvio dell'applicazione:\n\n{e}")