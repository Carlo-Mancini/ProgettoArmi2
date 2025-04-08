import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QComboBox, QLineEdit, QGroupBox, QHeaderView, QSplitter, QFrame,
    QMessageBox, QApplication, QStyleFactory, QGridLayout, QDateEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter


class StoricoMovimentiArmaDialog(QDialog):
    def __init__(self, id_arma, parent=None):
        super().__init__(parent)
        self.id_arma = id_arma
        self.arma_details = {}

        self.setWindowTitle("Storico Movimenti Arma")
        self.resize(1280, 720)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        self.setup_ui()
        self.load_arma_details()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Header - Dettagli dell'arma
        self.header_group = QGroupBox("Dettagli Arma")
        header_layout = QGridLayout()

        # Prima riga
        self.marcaLabel = QLabel("Marca:")
        self.marcaLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.marcaValue = QLabel()
        header_layout.addWidget(self.marcaLabel, 0, 0)
        header_layout.addWidget(self.marcaValue, 0, 1)

        self.modelloLabel = QLabel("Modello:")
        self.modelloLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.modelloValue = QLabel()
        header_layout.addWidget(self.modelloLabel, 0, 2)
        header_layout.addWidget(self.modelloValue, 0, 3)

        # Seconda riga
        self.matricolaLabel = QLabel("Matricola:")
        self.matricolaLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.matricolaValue = QLabel()
        header_layout.addWidget(self.matricolaLabel, 1, 0)
        header_layout.addWidget(self.matricolaValue, 1, 1)

        self.calibroLabel = QLabel("Calibro:")
        self.calibroLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.calibroValue = QLabel()
        header_layout.addWidget(self.calibroLabel, 1, 2)
        header_layout.addWidget(self.calibroValue, 1, 3)

        # Terza riga
        self.tipoArmaLabel = QLabel("Tipo Arma:")
        self.tipoArmaLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.tipoArmaValue = QLabel()
        header_layout.addWidget(self.tipoArmaLabel, 2, 0)
        header_layout.addWidget(self.tipoArmaValue, 2, 1)

        self.attualeDetenoreLabel = QLabel("Detentore Attuale:")
        self.attualeDetenoreLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.attualeDetenoreValue = QLabel()
        header_layout.addWidget(self.attualeDetenoreLabel, 2, 2)
        header_layout.addWidget(self.attualeDetenoreValue, 2, 3)

        self.header_group.setLayout(header_layout)
        main_layout.addWidget(self.header_group)

        # Filtri per la visualizzazione
        filter_group = QGroupBox("Filtri")
        filter_layout = QGridLayout()

        self.dataInizialeLabel = QLabel("Data Iniziale:")
        self.dataIniziale = QDateEdit(calendarPopup=True)
        self.dataIniziale.setDate(QDate.currentDate().addYears(-10))
        filter_layout.addWidget(self.dataInizialeLabel, 0, 0)
        filter_layout.addWidget(self.dataIniziale, 0, 1)

        self.dataFinaleLabel = QLabel("Data Finale:")
        self.dataFinale = QDateEdit(calendarPopup=True)
        self.dataFinale.setDate(QDate.currentDate())
        filter_layout.addWidget(self.dataFinaleLabel, 0, 2)
        filter_layout.addWidget(self.dataFinale, 0, 3)

        self.motivoLabel = QLabel("Motivo Trasferimento:")
        self.motivoCombo = QComboBox()
        self.motivoCombo.addItem("Tutti")
        self.motivoCombo.addItems(["Vendita", "Donazione", "Eredità", "Comodato", "Altro"])
        filter_layout.addWidget(self.motivoLabel, 1, 0)
        filter_layout.addWidget(self.motivoCombo, 1, 1)

        self.cercaLabel = QLabel("Cerca:")
        self.cercaInput = QLineEdit()
        self.cercaInput.setPlaceholderText("Cerca per cognome, nome, note...")
        filter_layout.addWidget(self.cercaLabel, 1, 2)
        filter_layout.addWidget(self.cercaInput, 1, 3)

        self.filterButton = QPushButton("Applica Filtri")
        self.filterButton.setIcon(QIcon.fromTheme("system-search"))
        self.resetButton = QPushButton("Reimposta")
        filter_layout.addWidget(self.filterButton, 2, 0)
        filter_layout.addWidget(self.resetButton, 2, 1)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # Tabella risultati
        table_label = QLabel("Storico Trasferimenti")
        table_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(table_label)

        # Creazione della tabella con stile migliorato
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableView::item {padding: 5px;}")

        # Definiamo le colonne per la tabella trasferimenti
        columns = [
            "ID", "Data Trasferimento", "Motivo",
            "Cedente", "Codice Fiscale Cedente",
            "Ricevente", "Codice Fiscale Ricevente",
            "Note"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Imposta la larghezza automatica delle colonne
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Motivo
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Cedente
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # CF Cedente
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Ricevente
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # CF Ricevente
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Note

        main_layout.addWidget(self.table, 1)  # La tabella prende più spazio (stretch factor 1)

        # Pulsanti azioni
        action_layout = QHBoxLayout()

        self.printButton = QPushButton("Stampa Report")
        self.printButton.setIcon(QIcon.fromTheme("document-print"))
        self.printButton.setMinimumWidth(150)
        action_layout.addWidget(self.printButton)

        self.exportButton = QPushButton("Esporta CSV")
        self.exportButton.setIcon(QIcon.fromTheme("document-save"))
        self.exportButton.setMinimumWidth(150)
        action_layout.addWidget(self.exportButton)

        action_layout.addStretch()

        self.closeButton = QPushButton("Chiudi")
        self.closeButton.setIcon(QIcon.fromTheme("window-close"))
        self.closeButton.setMinimumWidth(120)
        action_layout.addWidget(self.closeButton)

        main_layout.addLayout(action_layout)

        # Connessioni segnali
        self.closeButton.clicked.connect(self.accept)
        self.filterButton.clicked.connect(self.apply_filters)
        self.resetButton.clicked.connect(self.reset_filters)
        self.printButton.clicked.connect(self.print_report)
        self.exportButton.clicked.connect(self.export_csv)
        self.cercaInput.textChanged.connect(self.apply_filters)

    def load_arma_details(self):
        """Carica i dettagli dell'arma selezionata"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Query per ottenere i dettagli dell'arma
            cursor.execute("""
                SELECT a.MarcaArma, a.ModelloArma, a.Matricola, a.CalibroArma, a.TipoArma,
                       d.Cognome, d.Nome, d.CodiceFiscale
                FROM armi a
                LEFT JOIN detentori d ON a.ID_Detentore = d.ID_Detentore
                WHERE a.ID_ArmaDetenuta = ?
            """, (self.id_arma,))

            row = cursor.fetchone()
            if row:
                self.arma_details = {
                    'marca': row[0],
                    'modello': row[1],
                    'matricola': row[2],
                    'calibro': row[3],
                    'tipo': row[4],
                    'detentore_cognome': row[5],
                    'detentore_nome': row[6],
                    'detentore_cf': row[7]
                }

                # Popoliamo i campi dell'interfaccia
                self.marcaValue.setText(self.arma_details['marca'] or "")
                self.modelloValue.setText(self.arma_details['modello'] or "")
                self.matricolaValue.setText(self.arma_details['matricola'] or "")
                self.calibroValue.setText(self.arma_details['calibro'] or "")
                self.tipoArmaValue.setText(self.arma_details['tipo'] or "")

                detentore = f"{self.arma_details['detentore_cognome'] or ''} {self.arma_details['detentore_nome'] or ''}"
                if self.arma_details['detentore_cf']:
                    detentore += f" (CF: {self.arma_details['detentore_cf']})"
                self.attualeDetenoreValue.setText(detentore)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dettagli dell'arma:\n{e}")

    def load_data(self):
        """Carica i dati dei trasferimenti dalla tabella trasferimenti"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            # Ottieni i dati dalla tabella trasferimenti
            cursor.execute("""
                SELECT ID_Trasferimento, Data_Trasferimento, Motivo_Trasferimento,
                       Cedente_Cognome, Cedente_Nome, Cedente_CodiceFiscale,
                       Ricevente_Cognome, Ricevente_Nome, Ricevente_CodiceFiscale,
                       Note
                FROM trasferimenti
                WHERE ID_Arma = ?
                ORDER BY Data_Trasferimento DESC
            """, (self.id_arma,))

            rows = cursor.fetchall()
            conn.close()

            # Popoliamo la tabella
            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                id_item = QTableWidgetItem(str(row[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 0, id_item)

                data_item = QTableWidgetItem(str(row[1]))
                data_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 1, data_item)

                motivo_item = QTableWidgetItem(str(row[2]))
                motivo_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 2, motivo_item)

                # Cedente (unione cognome e nome)
                cedente = f"{row[3] or ''} {row[4] or ''}".strip()
                cedente_item = QTableWidgetItem(cedente)
                self.table.setItem(row_idx, 3, cedente_item)

                # CF Cedente
                cf_cedente_item = QTableWidgetItem(str(row[5] or ''))
                cf_cedente_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 4, cf_cedente_item)

                # Ricevente (unione cognome e nome)
                ricevente = f"{row[6] or ''} {row[7] or ''}".strip()
                ricevente_item = QTableWidgetItem(ricevente)
                self.table.setItem(row_idx, 5, ricevente_item)

                # CF Ricevente
                cf_ricevente_item = QTableWidgetItem(str(row[8] or ''))
                cf_ricevente_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 6, cf_ricevente_item)

                # Note
                note_item = QTableWidgetItem(str(row[9] or ''))
                self.table.setItem(row_idx, 7, note_item)

            if len(rows) == 0:
                QMessageBox.information(self, "Informazione",
                                        "Non ci sono trasferimenti registrati per questa arma.")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati dei trasferimenti:\n{e}")

    def apply_filters(self):
        """Applica i filtri alla tabella"""
        search_text = self.cercaInput.text().lower()
        selected_motivo = self.motivoCombo.currentText()
        data_iniziale = self.dataIniziale.date().toString("dd/MM/yyyy")
        data_finale = self.dataFinale.date().toString("dd/MM/yyyy")

        for row in range(self.table.rowCount()):
            show_row = True

            # Filtro per data
            data_trasferimento = self.table.item(row, 1).text()
            if data_trasferimento < data_iniziale or data_trasferimento > data_finale:
                show_row = False

            # Filtro per motivo
            if selected_motivo != "Tutti" and self.table.item(row, 2).text() != selected_motivo:
                show_row = False

            # Filtro per testo di ricerca
            if search_text:
                row_text = ""
                for col in [3, 4, 5, 6, 7]:  # Colonne con testo da cercare
                    row_text += self.table.item(row, col).text().lower() + " "

                if search_text not in row_text:
                    show_row = False

            self.table.setRowHidden(row, not show_row)

    def reset_filters(self):
        """Reimposta i filtri ai valori predefiniti"""
        self.dataIniziale.setDate(QDate.currentDate().addYears(-10))
        self.dataFinale.setDate(QDate.currentDate())
        self.motivoCombo.setCurrentIndex(0)  # "Tutti"
        self.cercaInput.clear()

        # Mostra tutte le righe
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)

    def print_report(self):
        """Visualizza l'anteprima di stampa del report"""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.print_preview)
        preview.exec_()

    def print_preview(self, printer):
        """Genera la visualizzazione di stampa"""
        document = self.create_report_document()
        document.print_(printer)

    def create_report_document(self):
        """Crea un documento HTML per il report"""
        from PyQt5.QtGui import QTextDocument

        doc = QTextDocument()
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { font-size: 18pt; color: #003366; text-align: center; }
                h2 { font-size: 14pt; color: #003366; margin-bottom: 5px; }
                table { border-collapse: collapse; width: 100%; margin-top: 10px; }
                th { background-color: #e0e0e0; padding: 8px; text-align: left; border: 1px solid #ddd; }
                td { padding: 8px; border: 1px solid #ddd; }
                .info { margin-bottom: 15px; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9; }
                .info p { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Storico Trasferimenti Arma</h1>
            <div class="info">
                <h2>Dettagli Arma</h2>
                <p><b>Marca:</b> %s</p>
                <p><b>Modello:</b> %s</p>
                <p><b>Matricola:</b> %s</p>
                <p><b>Calibro:</b> %s</p>
                <p><b>Tipo:</b> %s</p>
                <p><b>Detentore Attuale:</b> %s</p>
            </div>
            <h2>Trasferimenti</h2>
            <table>
                <tr>
                    <th>Data</th>
                    <th>Motivo</th>
                    <th>Cedente</th>
                    <th>Ricevente</th>
                    <th>Note</th>
                </tr>
        """ % (
            self.arma_details.get('marca', ''),
            self.arma_details.get('modello', ''),
            self.arma_details.get('matricola', ''),
            self.arma_details.get('calibro', ''),
            self.arma_details.get('tipo', ''),
            f"{self.arma_details.get('detentore_cognome', '')} {self.arma_details.get('detentore_nome', '')}"
        )

        # Aggiungi righe della tabella che non sono nascoste
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                data = self.table.item(row, 1).text()
                motivo = self.table.item(row, 2).text()
                cedente = self.table.item(row, 3).text()
                ricevente = self.table.item(row, 5).text()
                note = self.table.item(row, 7).text()

                html += f"""
                <tr>
                    <td>{data}</td>
                    <td>{motivo}</td>
                    <td>{cedente}</td>
                    <td>{ricevente}</td>
                    <td>{note}</td>
                </tr>
                """

        html += """
            </table>
            <p style="font-size: 8pt; text-align: right; margin-top: 20px;">
                Report generato il %s
            </p>
        </body>
        </html>
        """ % (datetime.now().strftime("%d/%m/%Y %H:%M"))

        doc.setHtml(html)
        return doc

    def export_csv(self):
        """Esporta i dati filtrati in formato CSV"""
        import csv
        from datetime import datetime
        from PyQt5.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self, "Salva Report CSV",
            f"storico_arma_{self.arma_details.get('matricola', '')}.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Scrivi l'intestazione con i dettagli dell'arma
                writer.writerow(["STORICO TRASFERIMENTI ARMA"])
                writer.writerow([f"Marca: {self.arma_details.get('marca', '')}",
                                 f"Modello: {self.arma_details.get('modello', '')}",
                                 f"Matricola: {self.arma_details.get('matricola', '')}"])
                writer.writerow([f"Data esportazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
                writer.writerow([])  # Riga vuota

                # Intestazioni colonne
                writer.writerow(["Data", "Motivo", "Cedente", "CF Cedente", "Ricevente", "CF Ricevente", "Note"])

                # Dati filtrati
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        writer.writerow([
                            self.table.item(row, 1).text(),
                            self.table.item(row, 2).text(),
                            self.table.item(row, 3).text(),
                            self.table.item(row, 4).text(),
                            self.table.item(row, 5).text(),
                            self.table.item(row, 6).text(),
                            self.table.item(row, 7).text()
                        ])

            QMessageBox.information(self, "Esportazione Completata",
                                    f"I dati sono stati esportati con successo nel file:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione:\n{e}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Applica uno stile moderno
    app.setStyle(QStyleFactory.create("Fusion"))

    dialog = StoricoMovimentiArmaDialog(1)
    dialog.exec_()