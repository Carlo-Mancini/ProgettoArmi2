# GeneraDenuncia.py (VERSIONE DI DEBUG SEMPLIFICATA)

import sqlite3
from datetime import datetime
import os
import sys
import traceback  # Import per la stampa dettagliata degli errori
import subprocess  # Import per aprire file su Mac/Linux

# Importa i widget PyQt5 necessari per i dialoghi
from PyQt5.QtWidgets import QMessageBox, QFileDialog

# Importa la libreria per gestire i template Word
from docxtpl import DocxTemplate


def crea_documento_denuncia(detentore_id, parent_widget=None):
    """
    [VERSIONE DI DEBUG] Esegue le query e stampa l'output.
    La generazione del documento è TEMPORANEAMENTE DISATTIVATA.
    """
    if not detentore_id:
        QMessageBox.warning(parent_widget, "Attenzione", "ID detentore non valido.")
        return

    print(f"--- GeneraDenuncia [DEBUG]: Avvio per ID_Detentore = {detentore_id} ---")

    try:
        # Connessione al database
        with sqlite3.connect("gestione_armi.db") as conn:
            cursor = conn.cursor()

            # 1. Recupera i dati del detentore (la lasciamo per ora)
            query_detentore = """
                SELECT 
                    Cognome, Nome, CodiceFiscale, DataNascita, LuogoNascita, SiglaProvinciaNascita,
                    ComuneResidenza, SiglaProvinciaResidenza, TipoVia, Via, Civico, Telefono,
                    TipologiaTitolo, NumeroPortoArmi, DataRilascio, EnteRilascio,
                    ComuneDetenzione, TipoViaDetenzione, ViaDetenzione, CivicoDetenzione 
                FROM detentori 
                WHERE ID_Detentore = ?
            """
            print("\n--- DEBUG ---")
            print("Eseguo query detentore:")
            print(query_detentore)
            print("Parametri:", (detentore_id,))
            print("-------------")
            cursor.execute(query_detentore, (detentore_id,))
            detentore = cursor.fetchone()
            print("Query detentore eseguita.")

            if not detentore:
                QMessageBox.warning(parent_widget, "Attenzione", "Detentore non trovato nel database.")
                return

            # 2. Recupera le armi (QUERY SEMPLIFICATA)
            query_armi = """
                SELECT Matricola 
                FROM armi 
                WHERE ID_Detentore = ?
            """
            print("\n--- DEBUG ---")
            print("Eseguo query armi (SEMPLIFICATA):")
            print(query_armi)
            print("Parametri:", (detentore_id,))
            print("-------------")
            cursor.execute(query_armi, (detentore_id,))
            print("Query armi ESEGUITA con successo.")  # Messaggio dopo l'esecuzione
            armi_db = cursor.fetchall()
            print(f"Dati armi recuperati ({len(armi_db)} righe). Contenuto:", armi_db)
            print("-------------")

            # 3. --- SEZIONE GENERAZIONE DOCUMENTO (TEMPORANEAMENTE DISATTIVATA) ---
            print("\n--- DEBUG ---")
            print("La generazione del documento Word è temporaneamente disattivata per il debug.")
            print("Se le query sopra non hanno dato errori, il problema potrebbe essere qui.")
            print("Per riattivarla, rimuovi il commento /* ... */ sotto.")
            print("-------------")

            # SE LE QUERY FUNZIONANO, DECOMMENTA QUESTA PARTE E PROVA A 
            # USARE LA QUERY ARMI COMPLETA (MA SENZA COMMENTO SQL INTERNO)

            armi_formattate = []
            for arma in armi_db:
                # Dovrai ADATTARE questo se usi la query SEMPLIFICATA!
                # Altrimenti usa la query completa e adatta gli indici [0], [1]...
                armi_formattate.append({
                    'tipo': "N/D", # arma[0] or "N/D",
                    'marca': "N/D", # arma[1] or "N/D",
                    'modello': "N/D", # arma[2] or "N/D",
                    'matricola': arma[0], # Se usi la query semplificata, ora è indice 0
                    'calibro': "N/D", # arma[4] or "N/D",
                    'note': "N/D", # arma[5] or "",
                    'categoria': "N/D", # arma[6] or "N/D",
                    'lung_canna': "N/D", # arma[7] or "N/D",
                    'num_canne': "N/D", # arma[8] or "N/D",
                    'catalogo': "N/D", 
                })

            data_corrente = datetime.now().strftime('%d/%m/%Y')

            context = {
                'comando_stazione': "NOME STAZIONE", 
                'cognome': detentore[0], 'nome': detentore[1], 'codice_fiscale': detentore[2],
                'data_nascita': detentore[3], 'luogo_nascita': detentore[4], 'provincia_nascita': detentore[5],
                'comune_residenza': detentore[6], 'provincia_residenza': detentore[7],
                'tipo_via': detentore[8] or "", 'via': detentore[9] or "", 'civico': detentore[10] or "",
                'telefono': detentore[11] or "N/D", 'tipologia_titolo': detentore[12] or "N/D",
                'numero_porto_armi': detentore[13] or "N/D", 'data_rilascio': detentore[14] or "N/D",
                'ente_rilascio': detentore[15] or "N/D", 'comune_detenzione': detentore[16],
                'tipo_via_detenzione': detentore[17] or "", 'via_detenzione': detentore[18] or "",
                'civico_detenzione': detentore[19] or "", 'armi': armi_formattate, 'data_documento': data_corrente,
            }

            template_name = "denuncia_professionale_template.docx"
            current_dir = os.getcwd()
            template_path = os.path.join(current_dir, "templates", template_name)

            if not os.path.exists(template_path):
                base_dir = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else current_dir
                template_path = os.path.join(base_dir, "templates", template_name)
                if not os.path.exists(template_path):
                    QMessageBox.critical(parent_widget, "Errore", f"Template '{template_name}' non trovato!")
                    return

            print(f"Uso template: {template_path}")
            doc = DocxTemplate(template_path)
            print("Rendering del documento...")
            doc.render(context)
            print("Rendering completato.")

            nome_file_default = f"Denuncia_Armi_{detentore[0]}_{detentore[1]}_{data_corrente.replace('/', '_')}.docx"
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Salva documento", nome_file_default, "Documenti Word (*.docx);;Tutti i file (*)"
            )

            if file_path:
                print(f"Salvataggio in: {file_path}")
                doc.save(file_path)
                QMessageBox.information(parent_widget, "Documento generato", f"Il documento è stato salvato con successo:\n{file_path}")
                reply = QMessageBox.question(parent_widget, "Aprire documento?", "Vuoi aprire il documento generato?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    print("Apertura documento...")
                    if sys.platform == "win32": os.startfile(file_path)
                    elif sys.platform == "darwin": subprocess.call(('open', file_path))
                    else: subprocess.call(('xdg-open', file_path))

            # --- FINE SEZIONE DISATTIVATA ---

            print("--- GeneraDenuncia [DEBUG]: Fine ---")

    except Exception as e:
        # Stampa l'errore completo sulla console per il debug
        print("\n!!! ERRORE DURANTE LA GENERAZIONE DELLA DENUNCIA !!!")
        traceback.print_exc()
        QMessageBox.critical(parent_widget, "Errore Critico", f"Si è verificato un errore imprevisto:\n{str(e)}")