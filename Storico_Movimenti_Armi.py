import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QComboBox, QLineEdit, QGroupBox, QHeaderView, QSplitter, QFrame,
    QMessageBox, QApplication, QStyleFactory, QGridLayout, QDateEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter


class StoricoMovimentiArmaDialog(QDialog):
    def __init__(self, id_arma, matricola=None, is_deleted=False, parent=None):
        super().__init__(parent)
        self.id_arma = id_arma
        self.matricola = matricola  # Parametro aggiunto per la ricerca per matricola
        self.is_deleted = is_deleted  # Flag per indicare se l'arma è cancellata
        self.arma_details = {}
        self.arma_exists = False

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

        # Aggiungiamo un label per lo stato dell'arma (cancellata o attiva)
        self.statoArmaLabel = QLabel("Stato:")
        self.statoArmaLabel.setFont(QFont("Arial", 10, QFont.Bold))
        self.statoArmaValue = QLabel()
        header_layout.addWidget(self.statoArmaLabel, 3, 0)
        header_layout.addWidget(self.statoArmaValue, 3, 1, 1, 3)  # Span across 3 columns

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
        self.motivoCombo.addItems(["VENDITA", "DONAZIONE", "EREDITÀ", "COMODATO D'USO", "ELIMINAZIONE", "ALTRO"])
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
        """Carica i dettagli dell'arma selezionata, gestendo anche le armi cancellate"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            if self.is_deleted and self.matricola:
                cursor.execute("""
                    SELECT t.MarcaArma, t.ModelloArma, t.Matricola, t.CalibroArma, t.TipoArma,
                           t.Motivo_Trasferimento, t.Data_Trasferimento, t.Note, t.ID_Arma
                    FROM trasferimenti t
                    INNER JOIN (
                        SELECT Matricola, MAX(Data_Trasferimento) as MaxData, MAX(Timestamp_Registrazione) as MaxTimestamp
                        FROM trasferimenti
                        WHERE Matricola = ? AND Motivo_Trasferimento = 'ELIMINAZIONE'
                        GROUP BY Matricola
                    ) latest ON t.Matricola = latest.Matricola 
                        AND t.Data_Trasferimento = latest.MaxData
                        AND t.Timestamp_Registrazione = latest.MaxTimestamp
                    WHERE t.Matricola = ?
                """, (self.matricola, self.matricola))
                row_trasf = cursor.fetchone()
                if row_trasf:
                    self.arma_exists = False
                    self.id_arma = row_trasf[8]
                    self.arma_details = {
                        'marca': row_trasf[0] or "",
                        'modello': row_trasf[1] or "",
                        'matricola': row_trasf[2] or "",
                        'calibro': row_trasf[3] or "",
                        'tipo': row_trasf[4] or "",
                        'motivo_eliminazione': row_trasf[5] or "ELIMINAZIONE",
                        'data_eliminazione': row_trasf[6] or "",
                        'note_eliminazione': row_trasf[7] or ""
                    }
                    self.marcaValue.setText(self.arma_details['marca'])
                    self.modelloValue.setText(self.arma_details['modello'])
                    self.matricolaValue.setText(self.arma_details['matricola'])
                    self.calibroValue.setText(self.arma_details['calibro'])
                    self.tipoArmaValue.setText(self.arma_details['tipo'])
                    self.attualeDetenoreValue.setText("ARMA NON PIÙ PRESENTE NEL DATABASE")
                    self.attualeDetenoreValue.setStyleSheet("color: red; font-weight: bold;")
                    stato_text = f"ELIMINATA in data {self.arma_details['data_eliminazione']}"
                    self.statoArmaValue.setText(stato_text)
                    self.statoArmaValue.setStyleSheet("color: red; font-weight: bold;")
                    conn.close()
                    return

            # Se l'arma non risulta cancellata, cerchiamo nella tabella armi
            cursor.execute("""
                SELECT a.MarcaArma, a.ModelloArma, a.Matricola, a.CalibroArma, a.TipoArma,
                       d.Cognome, d.Nome, d.CodiceFiscale
                FROM armi a
                LEFT JOIN detentori d ON a.ID_Detentore = d.ID_Detentore
                WHERE a.ID_ArmaDetenuta = ?
            """, (self.id_arma,))
            row = cursor.fetchone()
            if row:
                self.arma_exists = True
                self.matricola = row[2] or ""
                self.arma_details = {
                    'marca': row[0] or "",
                    'modello': row[1] or "",
                    'matricola': row[2] or "",
                    'calibro': row[3] or "",
                    'tipo': row[4] or "",
                    'detentore_cognome': row[5] or "",
                    'detentore_nome': row[6] or "",
                    'detentore_cf': row[7] or ""
                }
                self.marcaValue.setText(self.arma_details['marca'])
                self.modelloValue.setText(self.arma_details['modello'])
                self.matricolaValue.setText(self.arma_details['matricola'])
                self.calibroValue.setText(self.arma_details['calibro'])
                self.tipoArmaValue.setText(self.arma_details['tipo'])
                detentore = f"{self.arma_details['detentore_cognome']} {self.arma_details['detentore_nome']}".strip()
                if self.arma_details['detentore_cf']:
                    detentore += f" (CF: {self.arma_details['detentore_cf']})"
                self.attualeDetenoreValue.setText(detentore)
                self.statoArmaValue.setText("ATTIVA")
                self.statoArmaValue.setStyleSheet("color: green; font-weight: bold;")
            else:
                # Se non trovata per ID, proviamo a cercare per matricola
                if self.matricola:
                    cursor.execute("""
                        SELECT MarcaArma, ModelloArma, Matricola, CalibroArma, TipoArma, 
                               Motivo_Trasferimento, Data_Trasferimento, Note, ID_Arma
                        FROM trasferimenti
                        WHERE Matricola = ? AND Motivo_Trasferimento = 'ELIMINAZIONE'
                        ORDER BY Data_Trasferimento DESC, Timestamp_Registrazione DESC
                        LIMIT 1
                    """, (self.matricola,))
                    row_trasf = cursor.fetchone()
                    if row_trasf:
                        self.arma_exists = False
                        self.id_arma = row_trasf[8]
                        self.matricola = row_trasf[2]
                        self.arma_details = {
                            'marca': row_trasf[0] or "",
                            'modello': row_trasf[1] or "",
                            'matricola': row_trasf[2] or "",
                            'calibro': row_trasf[3] or "",
                            'tipo': row_trasf[4] or "",
                            'motivo_eliminazione': row_trasf[5] or "ELIMINAZIONE",
                            'data_eliminazione': row_trasf[6] or "",
                            'note_eliminazione': row_trasf[7] or ""
                        }
                        self.marcaValue.setText(self.arma_details['marca'])
                        self.modelloValue.setText(self.arma_details['modello'])
                        self.matricolaValue.setText(self.arma_details['matricola'])
                        self.calibroValue.setText(self.arma_details['calibro'])
                        self.tipoArmaValue.setText(self.arma_details['tipo'])
                        self.attualeDetenoreValue.setText("ARMA NON PIÙ PRESENTE NEL DATABASE")
                        self.attualeDetenoreValue.setStyleSheet("color: red; font-weight: bold;")
                        stato_text = f"ELIMINATA in data {self.arma_details['data_eliminazione']}"
                        self.statoArmaValue.setText(stato_text)
                        self.statoArmaValue.setStyleSheet("color: red; font-weight: bold;")
                    else:
                        QMessageBox.warning(self, "Arma non trovata",
                                            f"Non è stato possibile trovare l'arma con ID {self.id_arma} o matricola {self.matricola}.")
                        self.reject()
            conn.close()
        except Exception as e:
            print(f"Errore nel caricamento dei dettagli dell'arma: {e}")
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dettagli dell'arma:\n{e}")

    def load_data(self):
        """Carica i dati dei trasferimenti dalla tabella trasferimenti"""
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()

            if self.matricola:
                cursor.execute("""
                    SELECT ID_Trasferimento, Data_Trasferimento, Motivo_Trasferimento,
                           Cedente_Cognome, Cedente_Nome, Cedente_CodiceFiscale,
                           Ricevente_Cognome, Ricevente_Nome, Ricevente_CodiceFiscale,
                           Note
                    FROM trasferimenti
                    WHERE Matricola = ?
                    ORDER BY Data_Trasferimento DESC, Timestamp_Registrazione DESC
                """, (self.matricola,))
            else:
                cursor.execute("""
                    SELECT ID_Trasferimento, Data_Trasferimento, Motivo_Trasferimento,
                           Cedente_Cognome, Cedente_Nome, Cedente_CodiceFiscale,
                           Ricevente_Cognome, Ricevente_Nome, Ricevente_CodiceFiscale,
                           Note
                    FROM trasferimenti
                    WHERE ID_Arma = ?
                    ORDER BY Data_Trasferimento DESC, Timestamp_Registrazione DESC
                """, (self.id_arma,))
            rows = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                id_item = QTableWidgetItem(str(row[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 0, id_item)

                data_item = QTableWidgetItem(str(row[1] or ''))
                data_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 1, data_item)

                motivo_item = QTableWidgetItem(str(row[2] or ''))
                motivo_item.setTextAlignment(Qt.AlignCenter)
                if row[2] == "ELIMINAZIONE":
                    motivo_item.setForeground(QColor(255, 0, 0))
                    motivo_item.setFont(QFont("Arial", weight=QFont.Bold))
                self.table.setItem(row_idx, 2, motivo_item)

                cedente = f"{row[3] or ''} {row[4] or ''}".strip()
                cedente_item = QTableWidgetItem(cedente)
                self.table.setItem(row_idx, 3, cedente_item)

                cf_cedente_item = QTableWidgetItem(str(row[5] or ''))
                cf_cedente_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 4, cf_cedente_item)

                ricevente = f"{row[6] or ''} {row[7] or ''}".strip()
                ricevente_item = QTableWidgetItem(ricevente)
                self.table.setItem(row_idx, 5, ricevente_item)

                cf_ricevente_item = QTableWidgetItem(str(row[8] or ''))
                cf_ricevente_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, 6, cf_ricevente_item)

                note_item = QTableWidgetItem(str(row[9] or ''))
                self.table.setItem(row_idx, 7, note_item)

            if len(rows) == 0:
                QMessageBox.information(self, "Informazione",
                                        "Non ci sono trasferimenti registrati per questa arma.")
        except Exception as e:
            print(f"Errore nel caricamento dei trasferimenti: {e}")
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati dei trasferimenti:\n{e}")

    def apply_filters(self):
        """Applica i filtri alla tabella"""
        search_text = self.cercaInput.text().lower()
        selected_motivo = self.motivoCombo.currentText()
        data_iniziale = self.dataIniziale.date().toString("yyyy-MM-dd")
        data_finale = self.dataFinale.date().toString("yyyy-MM-dd")

        for row in range(self.table.rowCount()):
            show_row = True

            # Filtro per data
            data_trasferimento = self.table.item(row, 1).text()
            try:
                # Converti la data dal formato visualizzato al formato per confronto
                if data_trasferimento:
                    # Assumi che il formato nella tabella possa essere dd/MM/yyyy o yyyy-MM-dd
                    if "/" in data_trasferimento:
                        parts = data_trasferimento.split('/')
                        if len(parts) == 3:
                            data_trasferimento = f"{parts[2]}-{parts[1]}-{parts[0]}"

                    # Ora confronta
                    if data_trasferimento < data_iniziale or data_trasferimento > data_finale:
                        show_row = False
            except:
                # In caso di errore nel confronto date, mostra comunque la riga
                pass

            # Filtro per motivo
            motivo = self.table.item(row, 2).text()
            if selected_motivo != "Tutti" and motivo.upper() != selected_motivo.upper():
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

        # Determina se l'arma è attiva o eliminata
        stato_arma = "ATTIVA" if self.arma_exists else "ELIMINATA"
        stato_color = "green" if self.arma_exists else "red"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ font-size: 18pt; color: #003366; text-align: center; }}
                h2 {{ font-size: 14pt; color: #003366; margin-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th {{ background-color: #e0e0e0; padding: 8px; text-align: left; border: 1px solid #ddd; }}
                td {{ padding: 8px; border: 1px solid #ddd; }}
                .info {{ margin-bottom: 15px; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9; }}
                .info p {{ margin: 5px 0; }}
                .stato-arma {{ color: {stato_color}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Storico Trasferimenti Arma</h1>
            <div class="info">
                <h2>Dettagli Arma</h2>
                <p><b>Marca:</b> {self.arma_details.get('marca', '')}</p>
                <p><b>Modello:</b> {self.arma_details.get('modello', '')}</p>
                <p><b>Matricola:</b> {self.arma_details.get('matricola', '')}</p>
                <p><b>Calibro:</b> {self.arma_details.get('calibro', '')}</p>
                <p><b>Tipo:</b> {self.arma_details.get('tipo', '')}</p>
                <p><b>Stato:</b> <span class="stato-arma">{stato_arma}</span></p>
        """

        # Aggiungi informazioni specifiche in base allo stato dell'arma
        if self.arma_exists:
            detentore = f"{self.arma_details.get('detentore_cognome', '')} {self.arma_details.get('detentore_nome', '')}".strip()
            if self.arma_details.get('detentore_cf'):
                detentore += f" (CF: {self.arma_details.get('detentore_cf')})"
            html += f"<p><b>Detentore Attuale:</b> {detentore}</p>"
        else:
            html += f"""
                <p><b>Data Eliminazione:</b> {self.arma_details.get('data_eliminazione', '')}</p>
                <p><b>Motivo:</b> {self.arma_details.get('motivo_eliminazione', '')}</p>
                <p><b>Note:</b> {self.arma_details.get('note_eliminazione', '')}</p>
            """

        html += """
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
        """

        # Aggiungi righe della tabella che non sono nascoste
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                data = self.table.item(row, 1).text()
                motivo = self.table.item(row, 2).text()
                cedente = self.table.item(row, 3).text()
                ricevente = self.table.item(row, 5).text()
                note = self.table.item(row, 7).text()

                # Evidenzia in rosso le righe di eliminazione
                row_style = ' style="color: red; font-weight: bold;"' if motivo == "ELIMINAZIONE" else ""

                html += f"""
                <tr{row_style}>
                    <td>{data}</td>
                    <td>{motivo}</td>
                    <td>{cedente}</td>
                    <td>{ricevente}</td>
                    <td>{note}</td>
                </tr>
                """

        html += f"""
            </table>
            <p style="font-size: 8pt; text-align: right; margin-top: 20px;">
                Report generato il {datetime.now().strftime("%d/%m/%Y %H:%M")}
            </p>
        </body>
        </html>
        """

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

                # Aggiungi lo stato dell'arma
                stato = "ATTIVA" if self.arma_exists else "ELIMINATA"
                writer.writerow([f"Stato: {stato}"])

                if not self.arma_exists:
                    writer.writerow([f"Data eliminazione: {self.arma_details.get('data_eliminazione', '')}",
                                     f"Motivo: {self.arma_details.get('motivo_eliminazione', '')}"])

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
