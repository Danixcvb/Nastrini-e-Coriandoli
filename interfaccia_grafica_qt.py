"""
Questo modulo contiene la classe e le funzioni per l'interfaccia grafica
dell'applicazione "Configuratore Nastri Trasportatori" utilizzando PyQt6.
"""

import sys
import os
import pandas as pd
import subprocess
import random
import math
import re # <-- Import re module

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QComboBox,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QStatusBar,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem,
    QGraphicsPolygonItem, QSizePolicy, QStackedLayout, QScrollArea, QTabWidget,
    QFrame, QFormLayout
)
from PyQt6.QtGui import QPalette, QColor, QFont, QPolygonF, QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, QPointF, QTimer, QRectF, QPropertyAnimation, QPoint, QEasingCurve, pyqtProperty

# Importa funzioni e configurazioni dal progetto
import config
from elaborazione_principale import process_excel # Importa la funzione principale
# Importa il widget e il thread per la generazione degli allarmi
from Generazione_Allarmi.alarm_generator_scl import AlarmGeneratorWidget, GeneratorThread
from Generazione_Allarmi.alarm_generator_excel import GeneratorThread as ExcelGeneratorThread
from Generazione_Allarmi.alarm_generator_scl import GeneratorThread as SclGeneratorThread
# Assicurati che le altre funzioni necessarie siano importate o riscritte qui
# from funzioni_elaborazione import ... # Se necessario

class NastriApp(QMainWindow):
    """
    Finestra principale dell'applicazione basata su PyQt6.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuratore Nastri Trasportatori")
        self.setGeometry(100, 100, 950, 900) # Increased height further
        self.setMinimumSize(800, 750) # Increased minimum height

        self.excel_file_path = None # Percorso del file excel selezionato
        self.cab_plc_options = ["Seleziona un file Excel..."]
        self.alarm_gen_thread = None # Inizializza l'attributo del thread

        self._init_ui()
        self._load_initial_config()

    def _init_ui(self):
        """Inizializza l'interfaccia utente con layout riorganizzato."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25) # Slightly reduced margins
        main_layout.setSpacing(15) # Reduced main spacing

        # --- Sezione 1: Configurazione Nastri (using QFormLayout) ---
        config_group_layout = QVBoxLayout() # Layout for this section

        nastri_title_label = QLabel("Strumento incredibile per progetti nastri")
        nastri_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nastri_title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        config_group_layout.addWidget(nastri_title_label)

        config_group_layout.addSpacing(10) # Add some space after title

        # Form Layout for Inputs
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)

        # Excel Selection
        excel_input_layout = QHBoxLayout()
        self.excel_path_lineedit = QLineEdit("Nessun file selezionato")
        self.excel_path_lineedit.setReadOnly(True)
        self.excel_path_lineedit.setFont(QFont("Segoe UI", 10))
        excel_input_layout.addWidget(self.excel_path_lineedit, 1)
        excel_button = QPushButton("Sfoglia...")
        excel_button.setFont(QFont("Segoe UI", 10))
        excel_button.clicked.connect(self.select_excel_file)
        excel_input_layout.addWidget(excel_button)
        form_layout.addRow("File Excel:", excel_input_layout)

        # CAB PLC Selection
        self.cab_plc_combobox = QComboBox()
        self.cab_plc_combobox.setFont(QFont("Segoe UI", 10))
        self.cab_plc_combobox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cab_plc_combobox.addItems(self.cab_plc_options)
        self.cab_plc_combobox.setCurrentIndex(-1)
        self.cab_plc_combobox.currentIndexChanged.connect(self._update_button_states)
        form_layout.addRow("CAB_PLC:", self.cab_plc_combobox)

        config_group_layout.addLayout(form_layout) # Add form to section layout

        # Config Generate Button (Blue)
        self.generate_config_button = QPushButton("Genera Configurazioni Nastri")
        self.generate_config_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.generate_config_button.setMinimumHeight(38)
        self.generate_config_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; /* Blue */
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #A9CCE3; /* Lighter blue when disabled */
                color: #F2F2F2;
            }
            QPushButton:hover {
                 background-color: #2E86C1;
            }
            QPushButton:pressed {
                 background-color: #2874A6;
            }
        """)
        self.generate_config_button.clicked.connect(self._start_configuration_generation)
        # Add button centered within its own horizontal layout to control centering
        button_h_layout = QHBoxLayout()
        button_h_layout.addStretch()
        button_h_layout.addWidget(self.generate_config_button)
        button_h_layout.addStretch()
        config_group_layout.addLayout(button_h_layout)

        main_layout.addLayout(config_group_layout) # Add config section to main layout

        # --- Sezione 2: Generazione Allarmi HMI ---
        self.alarm_gen_widget = AlarmGeneratorWidget()
        self.alarm_gen_widget.generation_requested.connect(self._handle_alarm_generation_request)

        # Color the button INSIDE the alarm generator widget (Red)
        # Assuming the button inside is accessible as 'generate_button'
        try:
            alarm_generate_button = self.alarm_gen_widget.generate_button
            alarm_generate_button.setMinimumHeight(38) # Match height
            alarm_generate_button.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C; /* Red */
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:disabled {
                    background-color: #F5B7B1; /* Lighter red when disabled */
                    color: #F2F2F2;
                }
                 QPushButton:hover {
                    background-color: #CB4335;
                }
                QPushButton:pressed {
                    background-color: #B03A2E;
                }
            """)
        except AttributeError:
            print("WARN: Could not find 'generate_button' in AlarmGeneratorWidget to apply red style.")

        main_layout.addWidget(self.alarm_gen_widget, 1) # Keep stretch factor = 1

        # --- Barra di Stato (Comune) ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(QFont("Segoe UI", 9))
        self.status_bar.showMessage("Pronto. Seleziona un file Excel per iniziare.")

        self._update_button_states() # Initial state update

    def select_excel_file(self):
        """Apre una finestra di dialogo per selezionare il file Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona il file Excel Master",
            config.get_last_excel_path() or os.path.expanduser("~"), # Directory iniziale
            "File Excel (*.xlsx);;Tutti i file (*.*)"
        )
        if file_path:
            self.excel_file_path = file_path
            self.excel_path_lineedit.setText(os.path.basename(file_path)) # Mostra solo il nome file
            self.excel_path_lineedit.setToolTip(file_path) # Mostra percorso completo al passaggio del mouse
            config.save_last_excel_path(file_path)
            self.status_bar.showMessage(f"File selezionato: {os.path.basename(file_path)}. Caricamento CAB/PLC...", 3000)
            self._load_cab_plc_options() # Carica opzioni dopo selezione file
            # No need to call _update_button_states here, _load_cab_plc_options does it

    def _load_cab_plc_options(self):
        """Carica le opzioni CAB_PLC dal file Excel selezionato e aggiorna il ComboBox."""
        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
            self.cab_plc_options = ["Seleziona un file Excel..."]
            self.status_bar.showMessage("Errore: File Excel non valido o non trovato.", 5000)
        else:
            try:
                df = pd.read_excel(self.excel_file_path)
                if 'CAB_PLC' in df.columns:
                    # Ordina per le ultime tre cifre, gestendo non-stringhe
                    def sort_key(x):
                        s = str(x)
                        return s[-3:] if len(s) >= 3 else s
                    self.cab_plc_options = sorted(df['CAB_PLC'].astype(str).unique(), key=sort_key)
                    if not self.cab_plc_options:
                       self.cab_plc_options = ["Nessun CAB_PLC trovato"]
                    self.status_bar.showMessage("Opzioni CAB/PLC caricate.", 3000)
                else:
                    self.cab_plc_options = ["Errore: Colonna CAB_PLC mancante"]
                    QMessageBox.warning(self, "Avviso", "La colonna 'CAB_PLC' non è presente nel file Excel.")
                    self.status_bar.showMessage("Errore: Colonna CAB_PLC mancante nel file Excel.", 5000)
            except Exception as e:
                self.cab_plc_options = ["Errore caricamento file"]
                QMessageBox.critical(self, "Errore", f"""Errore nel caricamento del file Excel:
{e}""") # Use triple quotes for multi-line f-string
                self.status_bar.showMessage(f"Errore caricamento Excel: {e}", 5000)

        # Update the QComboBox
        self.cab_plc_combobox.clear()
        self.cab_plc_combobox.addItems(self.cab_plc_options)

        if self.cab_plc_options and \
           "Errore" not in self.cab_plc_options[0] and \
           "Seleziona" not in self.cab_plc_options[0] and \
           "Nessun" not in self.cab_plc_options[0]:
            self.cab_plc_combobox.setCurrentIndex(0) # Select the first valid item
            self.cab_plc_combobox.setEnabled(True)
        else:
             self.cab_plc_combobox.setCurrentIndex(-1) # No valid selection / show placeholder
             self.cab_plc_combobox.setEnabled(False) # Disable if no valid options

        # Update button state after loading options
        self._update_button_states()

    def _load_initial_config(self):
        """Carica la configurazione iniziale (es. ultimo file usato)."""
        last_file = config.get_last_excel_path()
        if last_file and os.path.exists(last_file):
            self.excel_file_path = last_file
            self.excel_path_lineedit.setText(os.path.basename(last_file))
            self.excel_path_lineedit.setToolTip(last_file)
            self.status_bar.showMessage(f"Caricato ultimo file: {os.path.basename(last_file)}. Caricamento CAB/PLC...", 3000)
            self._load_cab_plc_options()
        elif last_file:
             self.status_bar.showMessage(f"Ultimo file non trovato: {os.path.basename(last_file)}. Selezionane uno nuovo.", 5000)
        self._update_button_states() # Update state after initial load attempt

    def _update_button_states(self):
        """Abilita/Disabilita i pulsanti di generazione."""
        # Config Generation Button State
        valid_file = self.excel_file_path is not None and os.path.exists(self.excel_file_path)
        valid_cab_plc_index = self.cab_plc_combobox.currentIndex() >= 0
        cab_plc_text = self.cab_plc_combobox.currentText()  
        valid_cab_plc_text = not ("Errore" in cab_plc_text or "Seleziona" in cab_plc_text or "Nessun" in cab_plc_text)
        can_generate_config = valid_file and valid_cab_plc_index and valid_cab_plc_text

        # Check if any generation process is running
        # config_gen_running = self.generate_config_button.text().endswith("...") # Simple check
        # alarm_gen_active = self.alarm_gen_thread is not None and self.alarm_gen_thread.isRunning()
        # process_running = config_gen_running or alarm_gen_active

        # self.generate_config_button.setEnabled(can_generate_config and not process_running)
        self.generate_config_button.setEnabled(can_generate_config)

        # Enable/disable alarm gen button
        if hasattr(self, 'alarm_gen_widget') and hasattr(self.alarm_gen_widget, 'generate_button'): # Added check for generate_button
             # Check internal state of alarm widget (e.g., if input file is loaded)
             # The alarm widget itself handles enabling/disabling based on its state (e.g., file loaded, types loaded)
             # We just ensure it's not disabled due to the *other* process running.
             # can_generate_alarms_internally = self.alarm_gen_widget.generate_button.isEnabled() # Check if its button would be enabled
             # self.alarm_gen_widget.enable_generate_button(can_generate_alarms_internally and not process_running)
             # Let the alarm widget manage its own state based on its internal logic (file loaded etc.)
             # We don't need to explicitly enable/disable it from here based on the config process state.
             pass # Let the widget manage its own enabled state

    def _start_configuration_generation(self):
        """Avvia il processo di generazione della configurazione."""
        selected_cab_plc = self.cab_plc_combobox.currentText()

        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
             QMessageBox.warning(self, "File Mancante", "Seleziona un file Excel valido prima di procedere.")
             return
        if not selected_cab_plc or "Errore" in selected_cab_plc or "Seleziona" in selected_cab_plc or "Nessun" in selected_cab_plc:
            QMessageBox.warning(self, "Selezione Mancante", "Seleziona un CAB_PLC valido prima di procedere.")
            return

        # Update button text to indicate processing
        self.generate_config_button.setText("Generazione Nastri in corso...")
        # self._update_button_states() # Disable both buttons - REMOVED
        self.status_bar.showMessage(f"Lettura file Excel per {selected_cab_plc}...", 0)
        QApplication.processEvents()

        try:
            df = pd.read_excel(self.excel_file_path)
            # Verifica colonne necessarie (semplificato, assumiamo esistano per ora)
            required_columns = ['ITEM_ID_CUSTOM', 'CAB_PLC', 'ITEM_TRUNK'] # Minimal check
            if not all(col in df.columns for col in required_columns):
                 raise ValueError("Colonne richieste (ITEM_ID_CUSTOM, CAB_PLC, ITEM_TRUNK) mancanti nel file Excel.")

            # Filtra per CAB_PLC selezionato
            cab_plc_data = df[df['CAB_PLC'].astype(str) == selected_cab_plc].copy()

            if cab_plc_data.empty:
                raise ValueError(f"Nessun dato trovato per il CAB_PLC {selected_cab_plc} nel file Excel.")

            # Filtra righe non desiderate (come nella versione Tkinter)
            cab_plc_data = cab_plc_data[~cab_plc_data['ITEM_ID_CUSTOM'].str.contains('OG|SD|RS|CX|CN|CH|XR|SO|LC|IN', case=False, na=False)]
            if cab_plc_data.empty:
                 raise ValueError(f"Nessun dato valido trovato per {selected_cab_plc} dopo il filtraggio iniziale.")

            # Estrai prefissi unici
            unique_prefixes = sorted(cab_plc_data['ITEM_ID_CUSTOM'].str[:4].str.lower().unique())

            if not unique_prefixes:
                 raise ValueError(f"Nessun prefisso di linea valido trovato per {selected_cab_plc}.")

            if len(unique_prefixes) == 1:
                single_order = [f"1. {unique_prefixes[0]}"]
                self._process_excel_with_order(selected_cab_plc, single_order)
            else:
                # Mostra la finestra di dialogo per l'ordine
                order_dialog = OrderDialog(unique_prefixes, self)
                if order_dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_order = order_dialog.get_selected_order()
                    if selected_order:
                        self._process_excel_with_order(selected_cab_plc, selected_order)
                    else:
                        QMessageBox.warning(self, "Ordine Mancante", "Nessun ordine di generazione selezionato.")
                        self.status_bar.showMessage("Generazione annullata (nessun ordine).", 5000)
                else:
                    self.status_bar.showMessage("Generazione annullata dall'utente.", 5000)

        except FileNotFoundError:
            QMessageBox.critical(self, "Errore File", f"File Excel non trovato:\n{self.excel_file_path}")
            self.status_bar.showMessage("Errore: File Excel non trovato.", 5000)
        except ValueError as ve:
            QMessageBox.critical(self, "Errore Dati", f"Errore nei dati del file Excel:\n{ve}")
            self.status_bar.showMessage(f"Errore dati Excel: {ve}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Errore Elaborazione", f"Errore imprevisto durante l'elaborazione:\n{e}")
            self.status_bar.showMessage(f"Errore imprevisto: {e}", 5000)
            import traceback
            print(traceback.format_exc()) # Log traceback for debugging
        finally:
             # Restore button text AFTER potential update in _update_button_states
             self.generate_config_button.setText("Genera Configurazioni Nastri")
             # Re-enable buttons based on final state
             self._update_button_states() # Update state based on file/PLC selection

    def _process_excel_with_order(self, selected_cab_plc, selected_order):
        """Chiama la funzione di elaborazione principale e gestisce il risultato."""
        self.status_bar.showMessage(f"Generazione Configurazione Nastri per {selected_cab_plc} in corso...", 0)
        QApplication.processEvents()

        try:
            # Qui chiamiamo la funzione originale dal modulo elaborazione_principale
            # Passiamo None per root e status_var tk, perchè non servono più
            # process_excel() dovrà essere adattato o useremo una funzione wrapper se necessario
            # per ora, assumiamo che process_excel possa funzionare senza gli argomenti tk
            # NOTA: process_excel attualmente usa messagebox tk e crea directory.
            # Dovremo forse riscrivere process_excel per separare logica e UI.
            # >>> MODIFICA TEMPORANEA: Chiamo la funzione, ma potrebbe fallire o usare tk messagebox <<<\
            # TODO: Refactor process_excel or create a Qt-compatible processing logic
            success, message = process_excel(selected_cab_plc, None, None, selected_order, self.excel_file_path)

            if success:
                self.status_bar.showMessage(f"Generazione completata per {selected_cab_plc}!", 5000)
                # Mostra finestra di completamento (da implementare)
                completion_dialog = CompletionDialog(selected_cab_plc, self)
                completion_dialog.exec()
            else:
                QMessageBox.critical(self, "Errore Generazione", f"Errore durante la generazione dei file:\n{message}")
                self.status_bar.showMessage(f"Errore durante la generazione: {message}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Errore Generazione", f"Errore durante la generazione dei file:\n{e}")
            self.status_bar.showMessage(f"Errore durante la generazione: {e}", 5000)
            import traceback
            print(traceback.format_exc()) # Log traceback for debugging

    def _handle_alarm_generation_request(self, input_file, output_dir, instance_counts):
        """Starts the alarm generation threads for both Excel and SCL."""
        self.status_bar.showMessage("Avvio generazione allarmi HMI (Excel e SCL)...", 0)
        QApplication.processEvents()
        self.alarm_gen_widget.log_text_edit.clear()
        # Avvia thread per Excel
        self.excel_gen_thread = ExcelGeneratorThread(input_file, output_dir, instance_counts)
        self.excel_gen_thread.progress_signal.connect(self.alarm_gen_widget.log_message)
        self.excel_gen_thread.finished_signal.connect(lambda success, msg: self.status_bar.showMessage(f"Excel: {msg}", 5000))
        self.excel_gen_thread.start()
        # Avvia thread per SCL
        self.scl_gen_thread = SclGeneratorThread(input_file, output_dir, instance_counts)
        self.scl_gen_thread.progress_signal.connect(self.alarm_gen_widget.log_message)
        self.scl_gen_thread.finished_signal.connect(lambda success, msg: self.status_bar.showMessage(f"SCL: {msg}", 5000))
        self.scl_gen_thread.start()

    def _on_alarm_generation_finished(self):
        """Handles the completion of the alarm generation process."""
        self.status_bar.showMessage("Generazione allarmi HMI completata.", 5000)
        # TODO: Potresti voler controllare l'esito (success/failure) dal segnale finished_signal
        #       se il segnale lo passasse, e mostrare messaggi diversi.
        # Riabilita il pulsante del widget di generazione allarmi
        self.alarm_gen_widget.enable_generate_button(True) # RIPRISTINATO
        # Riabilita potenzialmente anche il pulsante di generazione configurazione
        # se nessun altro processo è in corso (potrebbe essere necessario un controllo più robusto)
        self._update_button_states() # Update button states based on current selections

# --- Dialog Classes ---
class OrderDialog(QDialog):
    """Finestra di dialogo per definire l'ordine di generazione delle linee."""
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ordine di Generazione")
        self.setMinimumSize(600, 450)
        # Store original items and a map from UPPERCASE to original case
        self.original_items_map = {item.upper(): item for item in items}
        self.display_items = sorted(self.original_items_map.keys()) # Sorted UPPERCASE items for display

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Titolo
        title_label = QLabel("Definisci l'Ordine di Generazione (Visualizzazione Maiuscola)")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Layout Orizzontale per le liste e i pulsanti
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)

        # Colonna Sinistra: Linee Disponibili (UPPERCASE)
        left_v_layout = QVBoxLayout()
        left_v_layout.addWidget(QLabel("Linee Disponibili:"))
        self.available_list = QListWidget()
        self.available_list.addItems(self.display_items) # Add sorted UPPERCASE items
        self.available_list.itemDoubleClicked.connect(self._move_to_ordered)
        left_v_layout.addWidget(self.available_list)
        h_layout.addLayout(left_v_layout, 1)

        # Colonna Centrale: Pulsanti di Spostamento
        center_v_layout = QVBoxLayout()
        center_v_layout.addStretch(1)
        move_right_button = QPushButton(">>")
        move_right_button.setToolTip("Aggiungi all'ordine")
        move_right_button.clicked.connect(self._move_to_ordered)
        center_v_layout.addWidget(move_right_button)
        move_left_button = QPushButton("<<")
        move_left_button.setToolTip("Rimuovi dall'ordine")
        move_left_button.clicked.connect(self._move_to_available)
        center_v_layout.addWidget(move_left_button)
        # TODO: Add Up/Down buttons if needed
        center_v_layout.addStretch(1)
        h_layout.addLayout(center_v_layout)

        # Colonna Destra: Linee Ordinate (UPPERCASE)
        right_v_layout = QVBoxLayout()
        right_v_layout.addWidget(QLabel("Linee Ordinate:"))
        self.ordered_list = QListWidget()
        self.ordered_list.itemDoubleClicked.connect(self._move_to_available)
        right_v_layout.addWidget(self.ordered_list)
        h_layout.addLayout(right_v_layout, 1)

        main_layout.addLayout(h_layout)

        # Istruzioni
        instructions_label = QLabel("Doppio click o usa i pulsanti per spostare le linee.")
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setFont(QFont("Segoe UI", 9))
        main_layout.addWidget(instructions_label)

        # Pulsanti OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def _move_to_ordered(self):
        selected_items = self.available_list.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        row = self.available_list.row(item)
        # Add UPPERCASE item with number
        count = self.ordered_list.count()
        new_item_text = f"{count + 1}. {item.text()}" # Item text is already UPPERCASE
        self.ordered_list.addItem(new_item_text)
        self.available_list.takeItem(row)

    def _move_to_available(self):
        selected_items = self.ordered_list.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        row = self.ordered_list.row(item)
        # Extract UPPERCASE text part
        uppercase_text = item.text().split('. ', 1)[1]
        self.available_list.addItem(uppercase_text) # Add UPPERCASE back
        self.available_list.sortItems() # Keep available list sorted (alphabetically, UPPERCASE)
        self.ordered_list.takeItem(row)
        self._renumber_ordered_list()

    def _renumber_ordered_list(self):
        for i in range(self.ordered_list.count()):
            item = self.ordered_list.item(i)
            current_text = item.text()
            if '. ' in current_text:
                # Text part is already UPPERCASE
                original_text = current_text.split('. ', 1)[1]
                item.setText(f"{i + 1}. {original_text}")
            else: # Should not happen if added correctly
                 item.setText(f"{i + 1}. {current_text}") # Ensure numbering

    def _on_accept(self):
        if self.ordered_list.count() == 0:
            QMessageBox.warning(self, "Ordine Vuoto", "Devi definire un ordine per almeno una linea.")
            return
        self.accept()

    def get_selected_order(self):
        """Restituisce la lista degli elementi nell'ordine definito,
           ma con i prefissi nel loro case originale (minuscolo)."""
        order_with_original_case = []
        for i in range(self.ordered_list.count()):
            item_text = self.ordered_list.item(i).text() # e.g., "1. AC21"
            # Extract the UPPERCASE prefix part
            uppercase_prefix = item_text.split('. ', 1)[1]
            # Find the original (lowercase) prefix from the map
            original_prefix = self.original_items_map.get(uppercase_prefix, uppercase_prefix) # Fallback if not found
            # Format with original case
            order_with_original_case.append(f"{i + 1}. {original_prefix}")
        return order_with_original_case

class ConfettiItem(QGraphicsPolygonItem): # Or could use Ellipse/Rect
    """Represents a single piece of confetti in the scene."""
    def __init__(self, x, y, size, color):
        super().__init__()
        self.setPos(x, y)
        self.size = size
        self.color = QColor(color)
        self.rotation_angle = random.uniform(0, 360)
        self.setRotation(self.rotation_angle)

        # Create shape (e.g., rectangle)
        rect = QRectF(-size / 2, -size / 2, size, size)
        self.setPolygon(QPolygonF(rect))
        self.setBrush(QBrush(self.color))
        self.setPen(QPen(Qt.PenStyle.NoPen))

        # Physics properties
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(-4, -1) # Start moving upwards slightly/slowly falling
        self.rotation_speed = random.uniform(-4, 4)
        self.gravity = 0.08 # Adjusted gravity

    def advance_state(self):
        """Update confetti position and rotation."""
        # Apply gravity
        self.dy += self.gravity

        # Update position
        self.setPos(self.x() + self.dx, self.y() + self.dy)

        # Update rotation
        self.rotation_angle += self.rotation_speed
        self.setRotation(self.rotation_angle)

class CompletionDialog(QDialog):
    """Finestra di dialogo mostrata al completamento della generazione."""
    def __init__(self, cab_plc, parent=None):
        super().__init__(parent)
        self.cab_plc = cab_plc
        self.confetti_items = []
        self.timer = QTimer(self)

        self.setWindowTitle("Generazione Completata")
        self.setMinimumSize(700, 550)

        self._init_ui()
        self._start_confetti_animation()

    def _init_ui(self):
        # Use QStackedLayout as the main layout for layering
        self.main_stacked_layout = QStackedLayout(self) # Use QStackedLayout
        self.main_stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.main_stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # --- Graphics View for Confetti (Layer 0 - Background) ---
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setStyleSheet("background: transparent; border: none;")
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setInteractive(False)
        self.graphics_view.viewport().setAutoFillBackground(False)
        # Insert view at index 0
        self.main_stacked_layout.insertWidget(0, self.graphics_view)

        # --- Foreground Content Widget (Layer 1 - Top) ---
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget) # QVBoxLayout FOR the content
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        # Title
        title = QLabel("Elaborazione completata con successo!")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(f"File generati per {self.cab_plc}:")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(subtitle)

        # --- Scroll Area for File List ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_content_widget = QWidget()
        files_layout = QHBoxLayout(scroll_content_widget)
        files_layout.setContentsMargins(5, 5, 5, 5)
        files_layout.setSpacing(15)
        try:
            config_folder = os.path.join('Configurazioni', self.cab_plc)
            if os.path.isdir(config_folder):
                # Get subfolders
                subfolders_raw = [d for d in os.listdir(config_folder) if os.path.isdir(os.path.join(config_folder, d))]
                print("--- DEBUG: Subfolders PRIMA dell'ordinamento ---")
                print(subfolders_raw)

                # Natural sort key function with error checking
                def natural_keys_debug(text):
                    try:
                        return [ int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text) ]
                    except Exception as e:
                        print(f"--- DEBUG: Errore natural_keys per '{text}': {e} ---")
                        # Fallback to simple lowercase sort if key fails
                        return [c.lower() for c in re.split('([0-9]+)', text) if c]

                # Apply natural sort
                all_subfolders = sorted(
                    subfolders_raw,
                    key=natural_keys_debug
                )
                print("--- DEBUG: Subfolders DOPO l'ordinamento ---")
                print(all_subfolders)

                num_cols = 3
                if not all_subfolders:
                     files_layout.addWidget(QLabel("Nessuna sottocartella generata."))
                else:
                    files_layout.addStretch(1)
                    items_per_col = (len(all_subfolders) + num_cols - 1) // num_cols
                    col_index = 0
                    current_col_layout = None
                    for i, subfolder in enumerate(all_subfolders):
                        if i % items_per_col == 0:
                            current_col_layout = QVBoxLayout()
                            current_col_layout.setSpacing(5)
                            files_layout.insertLayout(col_index, current_col_layout)
                            col_index += 1
                        subfolder_label = QLabel(subfolder)
                        subfolder_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                        current_col_layout.addWidget(subfolder_label)
                        subfolder_path = os.path.join(config_folder, subfolder)
                        try:
                            files = sorted(os.listdir(subfolder_path))
                            if not files:
                                current_col_layout.addWidget(QLabel("  (Nessun file)"))
                            else:
                                for file in files:
                                    file_label = QLabel(f"  • {file}")
                                    file_label.setFont(QFont("Segoe UI", 9))
                                    file_label.setWordWrap(False)
                                    file_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
                                    current_col_layout.addWidget(file_label)
                        except OSError:
                            current_col_layout.addWidget(QLabel("  (Errore lettura files)"))
                        current_col_layout.addStretch(1)
            else:
                files_layout.addWidget(QLabel("Cartella configurazioni non trovata."))
        except Exception as e:
            files_layout.addWidget(QLabel(f"Errore lettura cartelle: {e}"))

        scroll_area.setWidget(scroll_content_widget)
        content_layout.addWidget(scroll_area, 1)
        # --- End Scroll Area Setup ---

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        content_layout.addWidget(button_box, 0, Qt.AlignmentFlag.AlignCenter)

        # Insert content widget at index 1
        self.main_stacked_layout.insertWidget(1, content_widget)

        # Set the QStackedLayout as the dialog's main layout
        self.setLayout(self.main_stacked_layout)

        # Set the content widget (index 1) to be the active/visible one
        self.main_stacked_layout.setCurrentIndex(1)

        # Set initial scene rect AFTER layout is set
        self.graphics_scene.setSceneRect(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        """Handle dialog resize to update scene rect and content position."""
        super().resizeEvent(event)
        self.graphics_scene.setSceneRect(0, 0, self.graphics_view.width(), self.graphics_view.height())
        # Keep content centered/sized (approximate)
        content_widget = self.graphics_view.findChild(QWidget)
        if content_widget:
             content_widget.setGeometry(0, 0, self.width(), self.height())

    def _start_confetti_animation(self):
        scene_width = self.width()
        colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F", "#9B59B6", "#1ABC9C"]

        for _ in range(150): # Number of confetti pieces
            x = random.uniform(0, scene_width)
            y = random.uniform(-100, -20) # Start above the view
            size = random.uniform(6, 12)
            color = random.choice(colors)
            confetti = ConfettiItem(x, y, size, color)
            self.graphics_scene.addItem(confetti)
            self.confetti_items.append(confetti)

        self.timer.timeout.connect(self._animate_confetti)
        self.timer.start(20) # Animation speed (milliseconds)

    def _animate_confetti(self):
        scene_height = self.graphics_view.height()
        items_to_remove = []

        for item in self.confetti_items:
            item.advance_state()
            if item.y() > scene_height + 50: # Check if item is well below the view
                items_to_remove.append(item)

        for item in items_to_remove:
            self.graphics_scene.removeItem(item)
            self.confetti_items.remove(item)

        if not self.confetti_items:
            self.timer.stop()
            # print("Confetti animation stopped.")

    def closeEvent(self, event):
        """Stop the timer when the dialog is closed."""
        self.timer.stop()
        super().closeEvent(event)

# --- Entry point if run directly (for testing) ---
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     # Apply styles here if testing independently
#     main_window = NastriApp()
#     main_window.show()
#     sys.exit(app.exec()) 