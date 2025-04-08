import sys
import sqlite3
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QComboBox, QHeaderView, QGroupBox, QCheckBox, QFileDialog,
    QMessageBox, QSplitter, QFrame, QGridLayout, QToolButton, QMenu, QAction,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter


class DetentoriListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Detentori")
        self.resize(1200, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        self.detentori = []
        self.filtered_detentori = []
        self.current_sort_column = 1  # Default ordinamento per cognome
        self.sort_order = Qt.AscendingOrder

        self.setup_ui()
        self.load_detentori_from_db()
        self.populate_table()

    def setup_ui(self):
        # Layout principale
        main_layout = QVBoxLayout(self)

        # Titolo
        title_widget = QLabel("Gestione Anagrafica Detentori")
        title_widget.setAlignment(Qt.AlignCenter)
        title_widget.setFont(QFont("Arial", 14, QFont.Bold))
        title_widget.setStyleSheet("margin-bottom: 10px;")
        main_layout.addWidget(title_widget)

        # Sezione Filtri
        filter_group = QGroupBox("Filtri di Ricerca")
        filter_layout = QGridLayout()

        # Prima riga di filtri
        self.search_cognome_label = QLabel("Cognome:")
        self.search_cognome = QLineEdit()
        self.search_cognome.setPlaceholderText("Cerca per cognome...")
        filter_layout.addWidget(self.search_cognome_label, 0, 0)
        filter_layout.addWidget(self.search_cognome, 0, 1)

        self.search_nome_label = QLabel("Nome:")
        self.search_nome = QLineEdit()
        self.search_nome.setPlaceholderText("Cerca per nome...")
        filter_layout.addWidget(self.search_nome_label, 0, 2)
        filter_layout.addWidget(self.search_nome, 0, 3)

        # Seconda riga di filtri
        self.search_cf_label = QLabel("Codice Fiscale:")
        self.search_cf = QLineEdit()
        self.search_cf.setPlaceholderText("Cerca per codice fiscale...")
        filter_layout.addWidget(self.search_cf_label, 1, 0)
        filter_layout.addWidget(self.search_cf, 1, 1)

        self.search_comune_label = QLabel("Comune:")
        self.search_comune = QLineEdit()
        self.search_comune.setPlaceholderText("Cerca per comune di residenza...")
        filter_layout.addWidget(self.search_comune_label, 1, 2)
        filter_layout.addWidget(self.search_comune, 1, 3)

        # Pulsanti per filtri
        self.btn_apply_filters = QPushButton("Applica Filtri")
        self.btn_apply_filters.setIcon(QIcon.fromTheme("system-search"))
        self.btn_reset_filters = QPushButton("Reimposta Filtri")
        self.btn_reset_filters.setIcon(QIcon.fromTheme("edit-clear"))

        filter_layout.addWidget(self.btn_apply_filters, 2, 1)
        filter_layout.addWidget(self.btn_reset_filters, 2, 3)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # Tabella detentori
        table_header = QHBoxLayout()
        self.results_count_label = QLabel("Detentori trovati: 0")
        self.results_count_label.setFont(QFont("Arial", 10, QFont.Bold))
        table_header.addWidget(self.results_count_label)
        table_header.addStretch()

        # Combobox per campi visualizzati
        self.view_mode_label = QLabel("Visualizza campi:")
        self.view_mode = QComboBox()
        self.view_mode.addItem("Base (Nome, Cognome, CF)")
        self.view_mode.addItem("Anagrafica completa")
        self.view_mode.addItem("Solo titolari porto d'armi")
        self.view_mode.addItem("Personalizzato...")
        table_header.addWidget(self.view_mode_label)
        table_header.addWidget(self.view_mode)

        main_layout.addLayout(table_header)

        # Tabella
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eaeaea;
            }
        """)

        # Impostazione colonne
        self.setup_table_columns()

        main_layout.addWidget(self.table)

        # Pulsanti azioni
        actions_layout = QHBoxLayout()

        # Pulsante Nuovo con menu a discesa
        self.new_button_container = QHBoxLayout()
        self.new_button = QPushButton("Nuovo Detentore")
        self.new_button.setMinimumWidth(150)
        self.new_button.setIcon(QIcon.fromTheme("list-add"))

        self.new_button_container.addWidget(self.new_button)
        actions_layout.addLayout(self.new_button_container)

        # Pulsanti di modifica e cancellazione
        self.edit_button = QPushButton("Modifica")
        self.edit_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_button.setEnabled(False)
        actions_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Elimina")
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_button.setEnabled(False)
        actions_layout.addWidget(self.delete_button)

        actions_layout.addStretch()

        # Pulsanti aggiuntivi
        self.export_button = QPushButton("Esporta")
        self.export_button.setIcon(QIcon.fromTheme("document-save-as"))
        self.export_button.setToolTip("Esporta i detentori selezionati in CSV")
        actions_layout.addWidget(self.export_button)

        self.print_button = QPushButton("Stampa")
        self.print_button.setIcon(QIcon.fromTheme("document-print"))
        actions_layout.addWidget(self.print_button)

        self.close_button = QPushButton("Chiudi")
        self.close_button.setIcon(QIcon.fromTheme("window-close"))
        actions_layout.addWidget(self.close_button)

        main_layout.addLayout(actions_layout)

        # Barra di stato
        status_layout = QHBoxLayout()
        self.status_label = QLabel("")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        # Collegamenti segnali
        self.btn_apply_filters.clicked.connect(self.apply_filters)
        self.btn_reset_filters.clicked.connect(self.reset_filters)
        self.view_mode.currentIndexChanged.connect(self.change_view_mode)
        self.table.itemSelectionChanged.connect(self.update_button_states)
        self.table.itemDoubleClicked.connect(self.edit_detentore)

        self.new_button.clicked.connect(self.new_detentore)
        self.edit_button.clicked.connect(self.edit_selected_detentore)
        self.delete_button.clicked.connect(self.delete_selected_detentore)
        self.export_button.clicked.connect(self.export_csv)
        self.print_button.clicked.connect(self.print_preview)
        self.close_button.clicked.connect(self.accept)

    def setup_table_columns(self):
        # Definiamo le colonne della tabella in modalità base
        columns = ["ID", "Cognome", "Nome", "Codice Fiscale", "Comune Residenza", "Telefono"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Imposta la larghezza delle colonne
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Cognome
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CF
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Comune
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Telefono

        self.table.verticalHeader().setVisible(False)

    def load_detentori_from_db(self):
        try:
            conn = sqlite3.connect("gestione_armi.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM detentori ORDER BY Cognome, Nome")
            rows = cursor.fetchall()
            conn.close()

            # Nomi delle colonne dal database
            columns = ["id", "nome", "cognome", "fascicoloPersonale", "dataNascita", "luogoNascita",
                       "siglaProvinciaNascita", "sesso", "codiceFiscale", "comuneResidenza", "siglaProvinciaResidenza",
                       "tipoVia", "via", "civico", "telefono", "tipologiaTitolo", "enteRilascio",
                       "provinciaEnteRilascio",
                       "dataRilascio", "numeroPortoArmi", "tipoLuogoDetenzione", "comuneDetenzione",
                       "siglaProvinciaDetenzione",
                       "tipoViaDetenzione", "viaDetenzione", "civicoDetenzione", "tipoDocumento", "numeroDocumento",
                       "dataRilascioDocumento", "enteRilascioDocumento", "comuneEnteRilascioDocumento"]

            self.detentori = []
            for row in rows:
                self.detentori.append(dict(zip(columns, row)))

            self.filtered_detentori = self.detentori.copy()
            self.update_status(f"Caricati {len(self.detentori)} detentori")
            self.results_count_label.setText(f"Detentori trovati: {len(self.detentori)}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei detentori:\n{e}")

    def populate_table(self):
        self.table.setRowCount(0)  # Resetta la tabella
        self.table.setSortingEnabled(False)  # Disabilita temporaneamente il sorting

        # Popola la tabella in base alla modalità di visualizzazione corrente
        view_index = self.view_mode.currentIndex()

        for row_idx, det in enumerate(self.filtered_detentori):
            self.table.insertRow(row_idx)

            # Campi base sempre presenti
            id_item = QTableWidgetItem(str(det['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            self.table.setItem(row_idx, 1, QTableWidgetItem(det['cognome'] or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(det['nome'] or ""))

            cf_item = QTableWidgetItem(det['codiceFiscale'] or "")
            cf_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, cf_item)

            comune_item = QTableWidgetItem(det['comuneResidenza'] or "")
            if det['siglaProvinciaResidenza']:
                comune_item.setText(f"{det['comuneResidenza']} ({det['siglaProvinciaResidenza']})")
            self.table.setItem(row_idx, 4, comune_item)

            tel_item = QTableWidgetItem(det['telefono'] or "")
            tel_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, tel_item)

            # Aggiunge icone o indicazioni visive in base a determinate proprietà
            if det['numeroPortoArmi']:
                id_item.setForeground(QColor(0, 128, 0))  # Verde per detentori con porto d'armi

            # Colora di grigio i detentori senza codice fiscale o dati incompleti
            if not det['codiceFiscale'] or not det['comuneResidenza']:
                for col in range(self.table.columnCount()):
                    cell = self.table.item(row_idx, col)
                    cell.setForeground(QColor(128, 128, 128))

        self.table.setSortingEnabled(True)
        self.update_button_states()

    def apply_filters(self):
        cognome_filter = self.search_cognome.text().lower()
        nome_filter = self.search_nome.text().lower()
        cf_filter = self.search_cf.text().lower()
        comune_filter = self.search_comune.text().lower()

        self.filtered_detentori = []
        for det in self.detentori:
            if (cognome_filter == "" or cognome_filter in (det['cognome'] or "").lower()) and \
                    (nome_filter == "" or nome_filter in (det['nome'] or "").lower()) and \
                    (cf_filter == "" or cf_filter in (det['codiceFiscale'] or "").lower()) and \
                    (comune_filter == "" or comune_filter in (det['comuneResidenza'] or "").lower()):
                self.filtered_detentori.append(det)

        self.populate_table()
        self.results_count_label.setText(f"Detentori trovati: {len(self.filtered_detentori)}")

        if len(self.filtered_detentori) == 0:
            self.update_status("Nessun detentore corrisponde ai criteri di ricerca")
        else:
            self.update_status(f"Trovati {len(self.filtered_detentori)} detentori")

    def reset_filters(self):
        self.search_cognome.clear()
        self.search_nome.clear()
        self.search_cf.clear()
        self.search_comune.clear()
        self.filtered_detentori = self.detentori.copy()
        self.populate_table()
        self.results_count_label.setText(f"Detentori trovati: {len(self.detentori)}")
        self.update_status("Filtri reimpostati")

    def change_view_mode(self, index):
        # Cambia le colonne visualizzate in base alla modalità selezionata
        if index == 0:  # Base
            self.setup_table_columns()
        elif index == 1:  # Completa
            columns = ["ID", "Cognome", "Nome", "Codice Fiscale", "Data Nascita", "Luogo Nascita",
                       "Comune Residenza", "Indirizzo", "Telefono", "Porto d'Armi", "Scadenza"]
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
        elif index == 2:  # Solo porto d'armi
            self.filtered_detentori = [det for det in self.detentori if det['numeroPortoArmi']]
            self.setup_table_columns()
            self.results_count_label.setText(f"Detentori trovati: {len(self.filtered_detentori)}")

        self.populate_table()

    def update_button_states(self):
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def new_detentore(self):
        try:
            from Detentori import InserisciDetentoreDialog
            dialog = InserisciDetentoreDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.reset_filters()
                self.update_status("Nuovo detentore aggiunto con successo")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'apertura del form di inserimento:\n{e}")

    def edit_selected_detentore(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_detentore = int(self.table.item(row, 0).text())
        detentore = next((det for det in self.filtered_detentori if det['id'] == id_detentore), None)

        if not detentore:
            QMessageBox.warning(self, "Attenzione", "Detentore non trovato")
            return

        try:
            from Detentori import InserisciDetentoreDialog
            dialog = InserisciDetentoreDialog(detentore_data=detentore)
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.apply_filters()  # Mantieni i filtri attivi
                self.update_status("Detentore aggiornato con successo")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'apertura del form di modifica:\n{e}")

    def edit_detentore(self, item):
        row = item.row()
        id_detentore = int(self.table.item(row, 0).text())
        detentore = next((det for det in self.filtered_detentori if det['id'] == id_detentore), None)

        if not detentore:
            QMessageBox.warning(self, "Attenzione", "Detentore non trovato")
            return

        try:
            from Detentori import InserisciDetentoreDialog
            dialog = InserisciDetentoreDialog(detentore_data=detentore)
            if dialog.exec_() == QDialog.Accepted:
                self.load_detentori_from_db()
                self.apply_filters()
                self.update_status("Detentore aggiornato con successo")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'apertura del form di modifica:\n{e}")

    def delete_selected_detentore(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_detentore = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 2).text()
        cognome = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Sei sicuro di voler eliminare il detentore {nome} {cognome}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("gestione_armi.db")
                cursor = conn.cursor()

                # Verifica se il detentore ha armi associate
                cursor.execute("""
                    SELECT COUNT(*) FROM armi WHERE ID_Detentore = ?
                """, (id_detentore,))

                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Attenzione",
                                        "Non è possibile eliminare questo detentore perché ha delle armi associate.")
                    conn.close()
                    return

                cursor.execute("DELETE FROM detentori WHERE ID_Detentore = ?", (id_detentore,))
                conn.commit()
                conn.close()

                self.load_detentori_from_db()
                self.apply_filters()
                self.update_status(f"Detentore {nome} {cognome} eliminato con successo")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile eliminare il detentore:\n{e}")

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Esporta Detentori", "", "File CSV (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Intestazioni
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)

                # Dati
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        row_data = []
                        for col in range(self.table.columnCount()):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

            self.update_status(f"Dati esportati con successo in {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione:\n{e}")

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintPreviewDialog(printer, self)
        dialog.paintRequested.connect(self.print_table)
        dialog.exec_()

    def print_table(self, printer):
        from PyQt5.QtGui import QTextDocument

        document = QTextDocument()

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { font-size: 18pt; color: #333; text-align: center; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th { background-color: #f2f2f2; padding: 10px; text-align: left; border: 1px solid #ddd; }
                td { padding: 8px; border: 1px solid #ddd; }
                .footer { font-size: 9pt; text-align: center; margin-top: 20px; color: #777; }
            </style>
        </head>
        <body>
            <h1>Lista Detentori</h1>
        """

        # Aggiunge la tabella
        html += "<table>"

        # Intestazioni
        html += "<tr>"
        for col in range(1, self.table.columnCount()):  # Salta la colonna ID
            header_item = self.table.horizontalHeaderItem(col)
            html += f"<th>{header_item.text()}</th>"
        html += "</tr>"

        # Dati
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                html += "<tr>"
                for col in range(1, self.table.columnCount()):  # Salta la colonna ID
                    item = self.table.item(row, col)
                    html += f"<td>{item.text() if item else ''}</td>"
                html += "</tr>"

        html += "</table>"

        # Footer con data e ora
        now = datetime.now()
        html += f"""
        <div class='footer'>
            Stampato il {now.strftime('%d/%m/%Y')} alle {now.strftime('%H:%M')}
        </div>
        </body>
        </html>
        """

        document.setHtml(html)
        document.print_(printer)

    def update_status(self, message):
        self.status_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))