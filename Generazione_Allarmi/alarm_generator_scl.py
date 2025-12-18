"""
Widget riutilizzabile per l'interfaccia di Generazione Allarmi HMI.
Contiene i controlli UI e la logica per interagire con GeneratorThread.
"""

import sys
import os
import pandas as pd
import traceback
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTextEdit, QApplication, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont

# --- Constants (Copied from original script) ---
INPUT_FILE_SHEET_INDEX = 0
OBJECT_TYPE_COL = 'Object Type'
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
        # Special case: SV_DB_PANEL uses a fixed block instead of generated code
        # Check for PANEL in various formats (SV_DB_PANEL, PANEL, etc.)
        # Must check BEFORE removing SV_ prefix
        object_type_upper = str(object_type_full).strip().upper()
        object_type_clean_check = object_type_full.replace('SV_', '').replace('DB_', '').strip().upper()
        if object_type_upper == 'SV_DB_PANEL' or object_type_upper == 'PANEL' or object_type_clean_check == 'PANEL':
            # Return the fixed PANEL block as provided by the user (matching the corrected file format)
            scl_content = """REGION PANEL Management - Compact Alarms in Words
\t#AlmBit := 0;
\t#AlmWord := 0;
\t
\t\t//Initialize auxiliaries array for alarms
\t#AuxArray.Alm0 := "SV_DB_PANEL_SA".MCP1.ALL_BUS_COM_GEN; //
\t#AuxArray.Alm1 := "SV_DB_PANEL_SA".MCP1.ALL_VENT; //Cabinet cooling fan fault
\t#AuxArray.Alm2 := "SV_DB_PANEL_SA".MCP1.ALL_TEMP; //Cabinet overtemperature failure
\t#AuxArray.Alm3 := "SV_DB_PANEL_SA".MCP1.ALL_EOK24; //Failure power supply 24Vdc cabinet
\t#AuxArray.Alm4 := "SV_DB_PANEL_SA".MCP1.ALL_EAL24; //Machine board 24Vdc power supply failure
\t#AuxArray.Alm5 := "SV_DB_PANEL_SA".MCP1.ALL_EAL24I; //Failure power supply input 24Vdc cabinet
\t#AuxArray.Alm6 := "SV_DB_PANEL_SA".MCP1.ALL_EAL24O; //Failure power supply output 24Vdc cabinet
\t#AuxArray.Alm7 := "SV_DB_PANEL_SA".MCP1.ALL_GEN; //General switch fuse intervention
\t#AuxArray.Alm8 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm9 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm10 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm11 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm12 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm13 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm14 := "DbGlobale".GlobalData.AlwFalse;
\t#AuxArray.Alm15 := "DbGlobale".GlobalData.AlwFalse;
\t//Compact Alarms in common DB
\t"LIB_Alarms_Compact"(Alarms := #AuxArray,
\t\t\t\t\t\t\t\t UsedAlarms := 8,
\t\t\t\t\t\t\t\t LastBitUsed := #AlmBit,
\t\t\t\t\t\t\t\t LastWordIndex := #AlmWord,
\t\t\t\t\t\t\t\t DBAlm := "DB_HMI_SafeCompactAlm".AlmWord);
END_REGION ;

"""
            return scl_content
        
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
                    scl_content += f"\n\t\t#AuxArray.Alm{i} := \"DbGlobale\".GlobalData.AlwFalse;"
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
        self.instance_counts_from_excel = {} # Dictionary to store {object_type: count} read from Excel Count column
        self.generator_thread = None
        self._init_ui()
        self._load_last_input_file()

    def _init_ui(self):
        """Initializes the UI elements for the widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15) # Match margins with first column
        main_layout.setSpacing(15) # Match spacing with first column

        # Use FormLayout for better alignment
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(15)

        # --- Input File Selection ---
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        self.input_file_label = QLineEdit("Nessun file selezionato")
        self.input_file_label.setReadOnly(True)
        self.input_file_label.setFont(QFont("Segoe UI", 10))
        self.input_file_label.setMinimumHeight(32)
        self.input_file_button = QPushButton("Seleziona File Input (.xlsx)")
        self.input_file_button.setFont(QFont("Segoe UI", 10))
        self.input_file_button.setMinimumHeight(32)
        self.input_file_button.setMinimumWidth(80)
        self.input_file_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_file_label, 1) # Stretch line edit
        input_layout.addWidget(self.input_file_button)
        form_layout.addRow("File Master:", input_layout)

        # --- Output Directory Selection ---
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        self.output_dir_label = QLineEdit(self.output_dir_path)
        self.output_dir_label.setReadOnly(True)
        self.output_dir_label.setFont(QFont("Segoe UI", 10))
        self.output_dir_label.setMinimumHeight(32)
        self.output_dir_button = QPushButton("Seleziona Cartella Output")
        self.output_dir_button.setFont(QFont("Segoe UI", 10))
        self.output_dir_button.setMinimumHeight(32)
        self.output_dir_button.setMinimumWidth(80)
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_label, 1)
        output_layout.addWidget(self.output_dir_button)
        form_layout.addRow("Cartella Output:", output_layout)

        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)

        # --- Generate Button ---
        self.generate_button = QPushButton("Genera HMIAlarms.xlsx")
        self.generate_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.generate_button.setMinimumHeight(42) # Match height with first column button
        self.generate_button.clicked.connect(self._request_generation)
        self.generate_button.setEnabled(False) # Disabled initially
        button_h_layout = QHBoxLayout()
        button_h_layout.addStretch()
        button_h_layout.addWidget(self.generate_button)
        button_h_layout.addStretch()
        main_layout.addLayout(button_h_layout)
        main_layout.addStretch()  # Push content to top

        # --- Log Area --- (will be extracted and moved to main window)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 9)) # Monospaced font for logs
        # Don't add to layout here - will be extracted

    def _get_config_path(self):
        """Gets the path to the config file within the script's directory."""
        # Try to place config within the Generazione-Allarmi folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, CONFIG_FILENAME)

    def _save_last_input_file(self, file_path):
        """Saves the given file path to the config file."""
        try:
            config_data = {
                'last_input_file': file_path
            }
            with open(CONFIG_FILENAME, 'w') as f:
                json.dump(config_data, f, indent=4)
            self.log_message(f"Percorso file salvato: {file_path}")
        except IOError as e:
            self.log_message(f"Errore durante il salvataggio del percorso file ({CONFIG_FILENAME}): {e}")

    def _load_last_input_file(self):
        """Loads the last used input file path and instance counts from the config file."""
        try:
            if os.path.exists(CONFIG_FILENAME):
                with open(CONFIG_FILENAME, 'r') as f:
                    config_data = json.load(f)
                    if 'last_input_file' in config_data:
                        file_path = config_data['last_input_file']
                        if os.path.exists(file_path):
                            self.input_file_path = file_path
                            self.input_file_label.setText(os.path.basename(file_path))
                            self.log_message(f"Caricato l'ultimo file master: {os.path.basename(file_path)}")
                            # Load object types (counts are read from Excel Count column)
                            self.load_object_types()

                            if len(self.instance_counts_from_excel) > 0:
                                self.generate_button.setEnabled(True)
                            else:
                                self.generate_button.setEnabled(False)
                        else:
                            self.log_message(f"File salvato in {CONFIG_FILENAME} non trovato: {file_path}. Rimuovo il riferimento.")
                            os.remove(CONFIG_FILENAME) # Clean up invalid config
                            self.input_file_path = None
                            self.input_file_label.setText("Nessun file selezionato")
                            self.generate_button.setEnabled(False)
                    else:
                        self.log_message(f"Nessun percorso file trovato in {CONFIG_FILENAME}.")
            else:
                self.log_message(f"File di configurazione {CONFIG_FILENAME} non trovato.")
        except json.JSONDecodeError as e:
            self.log_message(f"Errore di lettura del file di configurazione {CONFIG_FILENAME}: {e}. Il file potrebbe essere corrotto. Lo elimino.")
            if os.path.exists(CONFIG_FILENAME):
                os.remove(CONFIG_FILENAME) # Corrupted file, delete it
            self.input_file_path = None
            self.input_file_label.setText("Nessun file selezionato")
            self.generate_button.setEnabled(False)
        except IOError as e:
            self.log_message(f"Errore di I/O durante il caricamento del file di configurazione {CONFIG_FILENAME}: {e}")
            self.input_file_path = None
            self.input_file_label.setText("Nessun file selezionato")
            self.generate_button.setEnabled(False)

    def select_input_file(self):
        # Suggest starting directory based on last used file or desktop
        start_dir = os.path.dirname(self.input_file_path) if self.input_file_path else os.path.join(os.path.expanduser("~"), "Desktop")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona File Master HMI Structures",
            start_dir, # Start from last directory or desktop
            "Excel Files (*.xlsx)"
        )
        if file_path:
            self.input_file_path = file_path
            self.input_file_label.setText(os.path.basename(file_path))
            self.log_message(f"File selezionato: {file_path}")
            self.load_object_types()
            
            # Enable button only if types were loaded successfully
            if len(self.instance_counts_from_excel) > 0:
                 self.generate_button.setEnabled(True)
            else:
                 self.generate_button.setEnabled(False)
        else:
            self.log_message("Selezione file annullata.")

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella Output",
            self.output_dir_path
        )
        if dir_path:
            self.output_dir_path = dir_path
            self.output_dir_label.setText(dir_path)
            self.log_message(f"Cartella output selezionata: {dir_path}")
        else:
             self.log_message("Selezione cartella output annullata.")

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

        self.object_types.clear()
        self.instance_counts_from_excel.clear()
        self.log_message("Caricamento tipi oggetto dal file master...")
        QApplication.processEvents() # Allow UI update

        try:
            with pd.ExcelFile(self.input_file_path) as xls:
                 # Read the first sheet directly
                if not xls.sheet_names:
                    raise ValueError("Il file Excel non contiene fogli.")
                summary_sheet_name = xls.sheet_names[INPUT_FILE_SHEET_INDEX]

                df = xls.parse(sheet_name=summary_sheet_name)
                # Find actual column names, ignoring leading/trailing spaces
                actual_obj_type_col = self._find_actual_column_name(OBJECT_TYPE_COL, df.columns)
                actual_count_col = self._find_actual_column_name('Count', df.columns)

                # Check if columns were found
                if actual_obj_type_col is None:
                    raise ValueError(f"Colonna '{OBJECT_TYPE_COL}' (o variante con spazi) non trovata nel primo foglio. Colonne trovate: {df.columns.tolist()}")
                
                if actual_count_col is None:
                    raise ValueError(f"Colonna 'Count' non trovata nel primo foglio. Colonne trovate: {df.columns.tolist()}")

                # Clear previous data
                self.object_types.clear()
                self.instance_counts_from_excel.clear()

                # Use the actual column names found
                processed_types = set()
                for index, row in df.iterrows():
                    # Use actual column names found earlier
                    obj_type = row[actual_obj_type_col]
                    count_value = row[actual_count_col] if actual_count_col in row else None

                    # Check if object type is valid (not NaN, not empty)
                    if pd.notna(obj_type) and str(obj_type).strip():
                         obj_type_str = str(obj_type).strip()
                         if obj_type_str in processed_types:
                             continue # Already processed this type

                         # Read count value from Excel (default to 0 if not found or invalid)
                         count = 0
                         if pd.notna(count_value):
                             try:
                                 count = int(count_value)
                             except (ValueError, TypeError):
                                 self.log_message(f"WARN: Valore Count non valido per '{obj_type_str}': {count_value}. Uso 0.")
                                 count = 0
                         
                         # Store the count value
                         self.instance_counts_from_excel[obj_type_str] = count

                         # Check if a sheet with this name exists
                         with pd.ExcelFile(self.input_file_path) as xls_check:
                             sheet_exists = obj_type_str in xls_check.sheet_names

                         if sheet_exists:
                            try:
                                # Store the object type
                                self.object_types[obj_type_str] = 0 # No offset needed here
                                processed_types.add(obj_type_str)
                            except ValueError:
                                 self.log_message(f"WARN: Errore durante l'elaborazione del tipo oggetto '{obj_type_str}', tipo ignorato.")
                         else:
                             self.log_message(f"INFO: Tipo oggetto '{obj_type_str}' trovato nel riepilogo, ma nessun foglio corrispondente trovato. Ignorato.")

                self.log_message(f"Trovati {len(processed_types)} tipi oggetto validi con foglio corrispondente.")
                self.generate_button.setEnabled(len(processed_types) > 0)

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

    def get_instance_counts(self):
        """Reads instance counts from the Excel file Count column."""
        return self.instance_counts_from_excel.copy()

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
                                           "Nessun tipo di oggetto con istanze > 0 trovato nella colonna 'Count' del file Excel. Generare comunque un file vuoto (se possibile)?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                 return
            # Allow generation with zero counts if user confirms

        # Disable button during processing (to be re-enabled by the controller)
        self.generate_button.setEnabled(False)
        self.log_message("Richiesta generazione inviata...")

        # Save the current input file path and instance counts before generating
        self._save_last_input_file(self.input_file_path)

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