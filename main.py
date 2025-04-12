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

# Importa le funzioni per la cache
from Utility import get_comuni, get_province


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
                       "provinciaEnteRilascio", "dataRilascio", "numeroPortoArmi", "tipoLuogoDetenzione",
                       "comuneDetenzione", "siglaProvinciaDetenzione", "tipoViaDetenzione", "viaDetenzione",
                       "civicoDetenzione", "tipoDocumento", "numeroDocumento", "dataRilascioDocumento",
                       "enteRilascioDocumento", "comuneEnteRilascioDocumento"]
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
            from DetentoriListDialog import DetentoriListDialog
            dialog = DetentoriListDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'apertura della gestione detentori:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")

    def open_ricerca_storico(self):
        try:
            from RicercaArmaDialog import RicercaArmaDialog
            dialog = RicercaArmaDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'apertura della ricerca armi:\n{e}")
            print(f"Dettaglio errore: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        print("Avvio dell'applicazione...")
        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create("Fusion"))

        # Carica in anticipo i dati statici dalla cache
        comuni = get_comuni()
        province = get_province()
        print("Caricati", len(comuni), "comuni e", len(province), "province.")

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
