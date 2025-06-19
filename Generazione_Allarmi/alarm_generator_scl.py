"""
Widget riutilizzabile per l'interfaccia di Generazione Allarmi HMI.
Contiene i controlli UI e la logica per interagire con GeneratorThread.
"""

import sys
import os
import pandas as pd
import traceback
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QTextEdit, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont

# --- Constants (Copied from original script) ---
INPUT_FILE_SHEET_INDEX = 0
OBJECT_TYPE_COL = 'Object Type'
OFFSET_COL = 'Length (Byte) - SA'
ADDRESS_COL = 'Address'
ALARM_TEXT_COL_CANDIDATES = ['Alarm Text (EN)', 'Alarm Text']
CONFIG_FILENAME = 'last_file.cfg' # File to store the last used input path

# Define the structure of the output Excel file based on the example
OUTPUT_COLUMNS = [
    'ID', 'Name', 'Alarm text [en-US], Alarm text 1', 'FieldInfo [Alarm text 1]',
    'Class', 'Trigger tag', 'Trigger bit', 'Trigger mode', 'Acknowledgement tag',
    'Acknowledgement bit', 'PLC acknowledgement tag', 'PLC acknowledgement bit',
    'Priority', 'Info text [en-US], Info text', 'Additional text 1 [en-US], Alarm text 2',
    'FieldInfo [Alarm text 2]', 'Additional text 2 [en-US], Alarm text 3',
    'FieldInfo [Alarm text 3]', 'Additional text 3 [en-US], Alarm text 4',
    'FieldInfo [Alarm text 4]', 'Additional text 4 [EN-US], Alarm text 5',
    'FieldInfo [Alarm text 5]', 'Additional text 5 [en-US], Alarm text 6',
    'FieldInfo [Alarm text 6]', 'Additional text 6 [en-US], Alarm text 7',
    'FieldInfo [Alarm text 7]', 'Additional text 7 [en-US], Alarm text 8',
    'FieldInfo [Alarm text 8]', 'Additional text 8 [en-US], Alarm text 9',
    'FieldInfo [Alarm text 9]', 'Additional text 9 [en-US], Alarm text 10',
    'FieldInfo [Alarm text 10]', 'Alarm parameter 1', 'Alarm parameter 2',
    'Alarm parameter 3', 'Alarm parameter 4', 'Alarm parameter 5',
    'Alarm parameter 6', 'Alarm parameter 7', 'Alarm parameter 8',
    'Alarm parameter 9', 'Alarm parameter 10', 'Area', 'Origin'
]

# --- Worker Thread for Processing (Copied from original script) ---
class GeneratorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str) # Success (bool), Message (str)

    def __init__(self, input_file, output_dir, instance_counts):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.instance_counts = instance_counts
        self._is_running = True

    def generate_scl_region(self, object_type_full, alarm_details, alm_word_index_value):
        """Genera il contenuto SCL per una regione di allarmi.
        alarm_details is a list of dicts: [{'Name': '...', 'Description': '...'}] for alarms with text.
        """
        # Remove SV_ prefix if present and get clean name
        object_type_clean = object_type_full.replace('SV_', '')
        
        # Region name should be just the clean name
        region_name = f"{object_type_clean} Management"
        
        # Const name should be Const + clean name (uppercase) + Number, tra virgolette
        const_name = f'"Const{object_type_clean.upper()}Number"'

        # Determine the total number of alarms with text
        total_actual_alarms = len(alarm_details)

        # Prepara il contenuto della regione
        scl_content = f"""REGION {region_name} - Compact Alarms in Words\n\t#AlmBit := 0;\n\t#AlmWord := {alm_word_index_value};\n\n\tFOR #i := 1 TO {const_name} DO\n\t\t//Initialize auxiliaries array for alarms"""

        # Calcola quanti blocchi di 16 allarmi sono necessari
        num_blocks = (total_actual_alarms + 15) // 16  # Equivalente a ceil(total_actual_alarms / 16)

        for block_idx in range(num_blocks):
            start_idx = block_idx * 16
            end_idx = min(start_idx + 16, total_actual_alarms)
            alarms_in_block = alarm_details[start_idx:end_idx]
            used_alarms_count_in_block = len(alarms_in_block)

            # Genera le assegnazioni #AuxArray.AlmX per il blocco corrente
            for i in range(16):
                if i < used_alarms_count_in_block:
                    name_val = alarms_in_block[i]['Name']
                    desc_val = alarms_in_block[i]['Description']
                    name_val_str = str(name_val).strip() if pd.notna(name_val) else ""
                    desc_val_str = str(desc_val).strip() if pd.notna(desc_val) else ""
                    scl_content += f"\n\t\t#AuxArray.Alm{i} := \"SV_DB_{object_type_clean}_SA\".{object_type_clean}[#i].{name_val_str}; //{desc_val_str}"
                else:
                    scl_content += f"\n\t\t#AuxArray.Alm{i} := \"UpstreamDB-Globale\".Global_Data.AlwFalse;"
            # Aggiungi la chiamata alla funzione di compattazione per il blocco corrente
            scl_content += f"""
\t\t//Compact Alarms in common DB
\t\t\"LIB_Alarms_Compact\"(Alarms := #AuxArray,
\t\t                     UsedAlarms := {used_alarms_count_in_block},
\t\t                     LastBitUsed := #AlmBit,
\t\t                     LastWordIndex := #AlmWord,
\t\t                     DBAlm := \"DB_HMI_Alm\".AlmWord);"""
        scl_content += f"\n\tEND_FOR;\nEND_REGION ;\n\n"
        return scl_content

    def generate_scl_file(self, scl_content, output_dir):
        """Genera il file SCL con header e footer fissi e contenuto indentato di un tab dopo BEGIN."""
        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(output_dir)), "Output")
            hmi_alarms_dir = os.path.join(config_dir, "HMI_Alarms")
            os.makedirs(hmi_alarms_dir, exist_ok=True)
            scl_output_path = os.path.join(hmi_alarms_dir, "AlarmsCompactHMI.scl")

            scl_header = (
                'FUNCTION "AlarmsCompactHMI" : Void\n'
                '{ S7_Optimized_Access := \'TRUE\' }\n'
                'VERSION : 0.1\n'
                '   VAR_TEMP \n'
                '      i : Int;\n'
                '      AlmBit : ULInt;\n'
                '      AlmWord : Int;\n'
                '      AuxArray : "AlarmGenType_16";\n'
                '   END_VAR\n\n'
                'BEGIN\n'
            )
            scl_footer = 'END_FUNCTION\n'

            # Indenta tutto il contenuto di uno a destra (dopo BEGIN)
            scl_content_indented = '\n'.join(['\t' + line if line.strip() != '' else '' for line in scl_content.splitlines()])

            with open(scl_output_path, 'w', encoding='utf-8') as f:
                f.write(scl_header)
                f.write(scl_content_indented)
                f.write('\n' + scl_footer)
            self.progress_signal.emit(f"File SCL generato con successo in:\n{scl_output_path}")
            return True
        except Exception as e:
            self.progress_signal.emit(f"Errore durante la generazione del file SCL: {str(e)}")
            return False

    def run(self):
        all_scl_regions = []  # Lista per contenere tutte le regioni SCL
        try:
            self.progress_signal.emit(f"Leggendo il file di input: {os.path.basename(self.input_file)}...")
            with pd.ExcelFile(self.input_file) as xls:
                if not xls.sheet_names:
                    raise ValueError("Il file Excel non contiene fogli.")
                summary_sheet_name = xls.sheet_names[INPUT_FILE_SHEET_INDEX]
                summary_df = xls.parse(sheet_name=summary_sheet_name, header=0)
                self.progress_signal.emit(f"Foglio di riepilogo '{summary_sheet_name}' letto.")

                for object_type_full, count in self.instance_counts.items():
                    if count <= 0:
                        self.progress_signal.emit(f"Skipping {object_type_full} (numero istanze <= 0).")
                        continue

                    self.progress_signal.emit(f"Processing {object_type_full} ({count} istanze)...")

                    # Find offset and AlmWord index
                    offset_row = summary_df[summary_df[OBJECT_TYPE_COL] == object_type_full]
                    if offset_row.empty:
                        self.progress_signal.emit(f"WARN: Tipo oggetto '{object_type_full}' non trovato nel foglio di riepilogo. Skippato.")
                        continue
                    # Recupera il valore della quarta colonna (word index)
                    alm_word_index_value = None
                    try:
                        word_index_col_name = None
                        for col_name in offset_row.columns:
                            if "word index" in col_name.lower():
                                word_index_col_name = col_name
                                break
                        if word_index_col_name:
                            alm_word_index_value = int(offset_row[word_index_col_name].iloc[0])
                            self.progress_signal.emit(f"Trovato 'word index' dalla colonna '{word_index_col_name}': {alm_word_index_value}")
                        elif len(offset_row.columns) > 3:
                            alm_word_index_value = int(offset_row.iloc[0, 3])
                            self.progress_signal.emit(f"Trovato 'word index' dalla quarta colonna (indice 3): {alm_word_index_value}")
                        else:
                            raise ValueError("La quarta colonna (word index) non è disponibile o non è stata trovata.")
                    except (ValueError, TypeError, IndexError) as e:
                        self.progress_signal.emit(f"ERRORE: Impossibile recuperare il 'word index' per '{object_type_full}' dal foglio di riepilogo: {e}. Assicurati che la quarta colonna (word index) esista e contenga un numero intero valido.")
                        self.finished_signal.emit(False, f"Errore grave: {e}")
                        return
                    if OFFSET_COL not in offset_row.columns:
                         raise ValueError(f"Colonna '{OFFSET_COL}' non trovata nel foglio di riepilogo.")
                    offset_series = offset_row[OFFSET_COL].dropna()
                    if offset_series.empty:
                         self.progress_signal.emit(f"WARN: Offset '{OFFSET_COL}' non trovato o vuoto per '{object_type_full}'. Skippato.")
                         continue
                    try:
                        offset = int(offset_series.iloc[0])
                    except (ValueError, TypeError):
                         raise ValueError(f"Offset '{offset_series.iloc[0]}' per '{object_type_full}' non è un numero intero valido.")
                    # Check if sheet exists for the object type (case-insensitive check)
                    alarm_def_sheet_name = None
                    for name in xls.sheet_names:
                         if name.lower() == object_type_full.lower():
                            alarm_def_sheet_name = name
                            break
                    if alarm_def_sheet_name is None:
                         self.progress_signal.emit(f"WARN: Foglio '{object_type_full}' non trovato nel file Excel. Skippato.")
                         continue
                    alarm_def_df = xls.parse(sheet_name=alarm_def_sheet_name)
                    self.progress_signal.emit(f"Letto foglio '{alarm_def_sheet_name}' per {object_type_full}.")
                    if ADDRESS_COL not in alarm_def_df.columns:
                        raise ValueError(f"Colonna '{ADDRESS_COL}' non trovata nel foglio '{alarm_def_sheet_name}'.")
                    # Trova il nome effettivo della colonna Alarm Text
                    alarm_text_col = self._find_actual_column_name(ALARM_TEXT_COL_CANDIDATES, alarm_def_df.columns)
                    if not alarm_text_col:
                        self.progress_signal.emit(f"Colonna 'Alarm Text (EN)' o 'Alarm Text' non trovata nel foglio '{alarm_def_sheet_name}'.")
                        alarm_details_for_scl = []
                    elif 'Name' not in alarm_def_df.columns:
                        self.progress_signal.emit(f"WARN: Colonna 'Name' non trovata nel foglio '{alarm_def_sheet_name}'. Impossibile generare SCL dettagliato per gli allarmi.")
                        alarm_details_for_scl = []
                    elif 'Description' not in alarm_def_df.columns:
                        self.progress_signal.emit(f"WARN: Colonna 'Description' non trovata nel foglio '{alarm_def_sheet_name}'. Descrizioni degli allarmi SCL saranno vuote.")
                        alarm_details_for_scl = alarm_def_df[pd.notna(alarm_def_df[alarm_text_col]) & (alarm_def_df[alarm_text_col] != '')].apply(
                            lambda row: {'Name': row.get('Name', ''), 'Description': ''}, axis=1
                        ).tolist()
                    else:
                        alarm_details_for_scl = alarm_def_df[pd.notna(alarm_def_df[alarm_text_col]) & (alarm_def_df[alarm_text_col] != '')].apply(
                            lambda row: {'Name': row['Name'], 'Description': row['Description']}, axis=1
                        ).tolist()
                    # Genera una regione SCL solo se ci sono allarmi con testo
                    if alarm_details_for_scl:
                        scl_region = self.generate_scl_region(
                            object_type_full,  # Pass full name for processing
                            alarm_details_for_scl,  # Pass collected alarm details
                            alm_word_index_value # Passa il word index
                        )
                        all_scl_regions.append(scl_region)
            if all_scl_regions:
                scl_content = ''.join(all_scl_regions)
                self.generate_scl_file(scl_content, self.output_dir)
            final_message = "Generazione completata."
            if all_scl_regions:
                final_message = f"Generazione completata con successo! File SCL creato."
            else:
                final_message = "Generazione completata. Nessun file creato (nessun allarme valido)."
            self.finished_signal.emit(True, final_message)
        except FileNotFoundError:
             error_message = f"Errore: File di input non trovato:\n{self.input_file}"
             self.progress_signal.emit(error_message)
             self.finished_signal.emit(False, error_message)
        except ValueError as ve:
            error_message = f"Errore nei dati di input:\n{ve}"
            self.progress_signal.emit(error_message)
            self.finished_signal.emit(False, error_message)
        except Exception as e:
            error_message = f"Errore imprevisto:\n{e}\nControlla i log per dettagli."
            self.progress_signal.emit(error_message)
            self.progress_signal.emit(traceback.format_exc())
            self.finished_signal.emit(False, error_message)

    def stop(self):
        self._is_running = False

    def _find_actual_column_name(self, candidates, column_list):
        """Restituisce il nome effettivo della colonna tra i candidati, ignorando maiuscole/minuscole."""
        for candidate in candidates:
            for col in column_list:
                if col.strip().lower() == candidate.lower():
                    return col
        return None

# --- Alarm Generator Widget ---
class AlarmGeneratorWidget(QWidget):
    """Widget contenente l'UI per la generazione degli allarmi."""
    # Signal emitted when generation is requested
    # Arguments: input_file_path (str), output_dir_path (str), instance_counts (dict)
    generation_requested = pyqtSignal(str, str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file_path = None
        # Default output dir to a subfolder in the main project if possible
        # Or use current working directory as fallback
        self.output_dir_path = os.path.join(os.getcwd(), "Output", "HMI_Alarms")
        self.object_types = {} # Dictionary to store {object_type: offset}
        self._init_ui()
        self._load_last_input_file()

    def _init_ui(self):
        """Initializes the UI elements for the widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 15) # Reduced top margin to 0
        main_layout.setSpacing(10)

        # --- Input File Selection ---
        input_layout = QHBoxLayout()
        self.input_file_label = QLineEdit("Nessun file selezionato")
        self.input_file_label.setReadOnly(True)
        self.input_file_button = QPushButton("Seleziona File Input (.xlsx)")
        self.input_file_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(QLabel("File Master:"))
        input_layout.addWidget(self.input_file_label, 1) # Stretch line edit
        input_layout.addWidget(self.input_file_button)
        main_layout.addLayout(input_layout)

        # --- Object Types Table ---
        self.table_label = QLabel("Tipi Oggetto e Numero Istanze:")
        main_layout.addWidget(self.table_label)
        self.object_table = QTableWidget()
        self.object_table.setColumnCount(2)
        self.object_table.setHorizontalHeaderLabels(["Tipo Oggetto", "Numero Istanze"])
        self.object_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.object_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # Ensure vertical header is not too wide
        self.object_table.verticalHeader().setVisible(False)
        self.object_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.object_table.verticalHeader().setDefaultSectionSize(24) # Adjust row height
        main_layout.addWidget(self.object_table)

        # --- Output Directory Selection ---
        output_layout = QHBoxLayout()
        self.output_dir_label = QLineEdit(self.output_dir_path)
        self.output_dir_label.setReadOnly(True)
        self.output_dir_button = QPushButton("Seleziona Cartella Output")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(QLabel("Cartella Output:"))
        output_layout.addWidget(self.output_dir_label, 1)
        output_layout.addWidget(self.output_dir_button)
        main_layout.addLayout(output_layout)

        # --- Generate Button ---
        self.generate_button = QPushButton("Genera HMIAlarms.xlsx")
        self.generate_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.generate_button.setMinimumHeight(35)
        self.generate_button.clicked.connect(self._request_generation)
        self.generate_button.setEnabled(False) # Disabled initially
        main_layout.addWidget(self.generate_button, 0, Qt.AlignmentFlag.AlignCenter)

        # --- Log Area ---
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 9)) # Monospaced font for logs
        main_layout.addWidget(self.log_text_edit, 1)

    def _get_config_path(self):
        """Gets the path to the config file within the script's directory."""
        # Try to place config within the Generazione-Allarmi folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, CONFIG_FILENAME)

    def _save_last_input_file(self, file_path):
        """Saves the last used input file path to the config file."""
        try:
            config_path = self._get_config_path()
            with open(config_path, 'w') as f:
                f.write(file_path)
        except Exception as e:
            self.log_message(f"Errore nel salvataggio del percorso file: {e}")

    def _load_last_input_file(self):
        """Loads the last used input file path from the config file."""
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    last_file = f.read().strip()
                    if os.path.exists(last_file):
                        self.input_file_path = last_file
                        self.input_file_label.setText(os.path.basename(last_file))
                        self.input_file_label.setToolTip(last_file)
                        self.load_object_types() # Load types if file is valid
                        self.log_message(f"Caricato ultimo file: {os.path.basename(last_file)}")
                    else:
                        self.log_message(f"Ultimo file ({os.path.basename(last_file)}) non trovato. Selezionane uno nuovo.")
            except Exception as e:
                self.log_message(f"Errore nel caricamento del percorso file: {e}")
        else:
             self.log_message(f"File di configurazione ({CONFIG_FILENAME}) non trovato. Seleziona il file master.")

    def select_input_file(self):
        """Opens a dialog to select the input Excel file."""
        start_dir = os.path.dirname(self.input_file_path) if self.input_file_path else os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona File Input Master (.xlsx)",
            start_dir,
            "Excel Files (*.xlsx);;All Files (*.*)"
        )
        if file_path:
            self.input_file_path = file_path
            self.input_file_label.setText(os.path.basename(file_path))
            self.input_file_label.setToolTip(file_path)
            self.log_message(f"File master selezionato: {os.path.basename(file_path)}")
            self.load_object_types()
            self._save_last_input_file(file_path)

    def select_output_dir(self):
        """Opens a dialog to select the output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella Output",
            self.output_dir_path
        )
        if dir_path:
            self.output_dir_path = dir_path
            self.output_dir_label.setText(dir_path)
            self.log_message(f"Cartella output selezionata: {dir_path}")

    def log_message(self, message):
        """Appends a message to the log area."""
        self.log_text_edit.append(message)
        self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum()) # Auto-scroll

    def _find_actual_column_name(self, target_name, column_list):
        """Finds the actual column name, ignoring case."""
        for col_name in column_list:
            if col_name.strip().lower() == target_name.lower():
                return col_name
        return None # Not found

    def load_object_types(self):
        """Loads object types from the selected input file's summary sheet."""
        if not self.input_file_path or not os.path.exists(self.input_file_path):
            QMessageBox.warning(self, "File Mancante", "Seleziona prima un file master valido.")
            return

        self.object_table.setRowCount(0) # Clear existing rows
        self.object_types.clear()
        self.log_message("Caricamento tipi oggetto dal file master...")
        QApplication.processEvents() # Allow UI update

        try:
            with pd.ExcelFile(self.input_file_path) as xls:
                 # Read the first sheet directly
                if not xls.sheet_names:
                    raise ValueError("Il file Excel non contiene fogli.")
                summary_sheet_name = xls.sheet_names[INPUT_FILE_SHEET_INDEX] # Assume INPUT_FILE_SHEET_INDEX is 0 or defined elsewhere
                 # Find the correct summary sheet index (case-insensitive check)
                # summary_sheet_name = None
                # for i, name in enumerate(xls.sheet_names):
                    # Assume summary is the first sheet if name doesn't match common pattern
                    # or use a more specific check if needed
                #    if name.lower() == "summary" or i == INPUT_FILE_SHEET_INDEX:
                #        summary_sheet_name = name
                #        summary_sheet_index = i
                #        break
                # if summary_sheet_name is None:
                #     raise ValueError("Foglio di riepilogo non trovato (cercato 'Summary' o primo foglio).")

                df = xls.parse(sheet_name=summary_sheet_name)
                # Find actual column names (case-insensitive)
                actual_object_col = self._find_actual_column_name(OBJECT_TYPE_COL, df.columns)
                actual_offset_col = self._find_actual_column_name(OFFSET_COL, df.columns)

                if not actual_object_col:
                     raise ValueError(f"Colonna '{OBJECT_TYPE_COL}' non trovata nel foglio di riepilogo.")
                # Offset column is not strictly needed here, just for info
                if not actual_offset_col:
                     self.log_message(f"Nota: Colonna '{OFFSET_COL}' non trovata, non mostrata in tabella.")

                # Populate table
                for index, row in df.iterrows():
                    obj_type = row[actual_object_col]
                    if pd.notna(obj_type) and obj_type.strip(): # Check for valid object type
                        obj_type = obj_type.strip()
                        # Check if corresponding sheet exists (case-insensitive)
                        sheet_exists = any(sheet.lower() == obj_type.lower() for sheet in xls.sheet_names)
                        if sheet_exists:
                            self.add_object_type_to_table(obj_type)
                            # Store offset if found
                            if actual_offset_col and pd.notna(row[actual_offset_col]):
                                try:
                                     self.object_types[obj_type] = int(row[actual_offset_col])
                                except ValueError:
                                     self.log_message(f"WARN: Offset non valido per {obj_type}, sarà ignorato.")
                        else:
                             self.log_message(f"WARN: Foglio per '{obj_type}' non trovato, tipo oggetto ignorato.")

                self.log_message(f"Trovati {self.object_table.rowCount()} tipi oggetto validi con foglio corrispondente.")
                self.generate_button.setEnabled(self.object_table.rowCount() > 0)

        except FileNotFoundError:
            self.log_message(f"Errore: File non trovato: {self.input_file_path}")
            QMessageBox.critical(self, "Errore File", f"Impossibile trovare il file:\n{self.input_file_path}")
        except ValueError as ve:
             self.log_message(f"Errore lettura file Excel: {ve}")
             QMessageBox.critical(self, "Errore Dati Excel", f"Errore nel formato del file Excel:\n{ve}")
        except Exception as e:
            self.log_message(f"Errore imprevisto durante il caricamento dei tipi: {e}")
            QMessageBox.critical(self, "Errore Caricamento", f"Errore imprevisto:\n{e}")
            self.log_message(traceback.format_exc())

    def add_object_type_to_table(self, obj_type):
        """Adds a row to the object types table."""
        row_position = self.object_table.rowCount()
        self.object_table.insertRow(row_position)

        # Object Type Item (non-editable)
        type_item = QTableWidgetItem(obj_type)
        type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.object_table.setItem(row_position, 0, type_item)

        # Instance Count Item (SpinBox)
        spin_box = QSpinBox()
        spin_box.setRange(0, 999) # Set appropriate range
        spin_box.setValue(0)
        spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.object_table.setCellWidget(row_position, 1, spin_box)

    def get_instance_counts(self):
        """Retrieves the instance counts from the table."""
        counts = {}
        for row in range(self.object_table.rowCount()):
            type_item = self.object_table.item(row, 0)
            spin_box = self.object_table.cellWidget(row, 1)
            if type_item and spin_box:
                counts[type_item.text()] = spin_box.value()
        return counts

    def _request_generation(self):
        """Gathers data and emits the generation_requested signal."""
        if not self.input_file_path or not os.path.exists(self.input_file_path):
            QMessageBox.warning(self, "Input Mancante", "Seleziona un file master valido.")
            return
        if not self.output_dir_path or not os.path.isdir(os.path.dirname(self.output_dir_path)): # Check parent dir exists
             QMessageBox.warning(self, "Output Mancante", "Seleziona una cartella di output valida.")
             return

        instance_counts = self.get_instance_counts()
        if not instance_counts or all(v == 0 for v in instance_counts.values()):
            reply = QMessageBox.question(self, "Nessuna Istanza",
                                           "Nessuna istanza selezionata per nessun tipo oggetto. Generare comunque un file vuoto (se possibile)?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                 return
            # Allow generation with zero counts if user confirms

        # Disable button during processing (to be re-enabled by the controller)
        self.generate_button.setEnabled(False)
        self.log_message("Richiesta generazione inviata...")

        # Emit the signal with necessary data
        self.generation_requested.emit(
            self.input_file_path,
            self.output_dir_path,
            instance_counts
        )

    # --- Public Slots --- 
    def enable_generate_button(self, enabled=True):
        """Slot to enable/disable the generate button from outside."""
        self.generate_button.setEnabled(enabled)

# Example of how to use the widget standalone (for testing)
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply a simple dark theme for testing
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53,53,53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    app.setPalette(dark_palette)
    app.setStyleSheet("QPushButton { border: 1px solid #5A5A5A; border-radius: 4px; padding: 5px; } QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    # Create and show the widget
    test_widget = AlarmGeneratorWidget()
    test_widget.setWindowTitle("Test Alarm Generator Widget")
    test_widget.resize(700, 500)
    test_widget.show()

    # --- Example of connecting signals/slots for testing ---
    def handle_generation_request(input_f, output_d, counts):
        print("--- GENERATION REQUESTED (TEST) ---")
        print(f"Input: {input_f}")
        print(f"Output: {output_d}")
        print(f"Counts: {counts}")
        QMessageBox.information(test_widget, "Richiesta Ricevuta", "Segnale 'generation_requested' ricevuto!")
        # Simulate processing
        test_widget.log_message("Simulazione elaborazione...")
        # Re-enable button after simulated processing
        QTimer.singleShot(2000, lambda: test_widget.enable_generate_button(True))

    test_widget.generation_requested.connect(handle_generation_request)
    # --- End Test Connection ---

    sys.exit(app.exec()) 