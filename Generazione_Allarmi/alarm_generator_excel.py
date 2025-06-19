import sys
import os
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QTextEdit, QMainWindow, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
import traceback

# --- Constants ---
INPUT_FILE_SHEET_INDEX = 0
OBJECT_TYPE_COL = 'Object Type'
OFFSET_COL = 'Length (Byte) - SA'
ADDRESS_COL = 'Address'
ALARM_TEXT_COL_CANDIDATES = ['Alarm Text (EN)', 'Alarm Text']
OUTPUT_FILENAME = 'HMIAlarms.xlsx'
OUTPUT_SHEET_NAME = 'DiscreteAlarms'
CONFIG_FILENAME = 'last_file.cfg' # File to store the last used input path

# Define the structure of the output Excel file based on the example
OUTPUT_COLUMNS = [
    'ID',
    'Name',
    'Alarm text [en-US], Alarm text',
    'FieldInfo [Alarm text]',
    'Class',
    'Trigger tag',
    'Trigger bit',
    'Acknowledgement tag',
    'Acknowledgement bit',
    'PLC acknowledgement tag',
    'PLC acknowledgement bit',
    'Group',
    'Report',
    'Info text [en-US], Info text'
]

OUTPUT_COLUMNS_FR = [col.replace('en-US', 'fr-FR') for col in OUTPUT_COLUMNS]

# --- Worker Thread for Processing ---
class GeneratorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str) # Success (bool), Message (str)

    def __init__(self, input_file, output_dir, instance_counts):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.instance_counts = instance_counts
        self._is_running = True

    def _find_actual_column_name(self, candidates, column_list):
        """Restituisce il nome effettivo della colonna tra i candidati, ignorando maiuscole/minuscole."""
        for candidate in candidates:
            for col in column_list:
                if col.strip().lower() == candidate.lower():
                    return col
        return None

    def generate_scl_region(self, object_type, alarm_texts, alm_word_index_value):
        """Genera il contenuto SCL per una regione di allarmi."""
        # Remove SV_ prefix if present and get clean name
        object_type_clean = object_type.replace('SV_', '')
        
        # Region name should be just the clean name
        region_name = f"{object_type_clean} Management"
        
        # Const name should be Const + clean name (uppercase) + Number
        const_name = f"Const{object_type_clean.upper()}Number"

        # UsedAlarms is the number of actual alarms with text (max 16)
        used_alarms_count = min(len(alarm_texts), 16)
        
        # Prepara il contenuto della regione
        scl_content = f"""REGION {region_name} - Compact Alarms in Words
    #AlmBit := 0;
    #AlmWord := {alm_word_index_value};
    
    FOR #i := 0 TO {const_name} - 1 DO
        //Initialize auxiliaries array for alarms"""

        # Aggiungi gli allarmi basati sui testi forniti, fino a 16
        for i in range(16):
            if i < used_alarms_count:
                alarm_text = alarm_texts[i]
                scl_content += f"""
        #AuxArray.Alm{i} := "SV_DB_{object_type_clean}_SA".{object_type_clean}[#i].{alarm_text}; //"""
            else:
                # Fill remaining lines with AlwFalse
                scl_content += f"""
        #AuxArray.Alm{i} := "UpstreamDB-Globale".Global_Data.AlwFalse;"""
        
        # Aggiungi la chiamata alla funzione di compattazione
        scl_content += f"""
        //Compact Alarms in common DB
        "LIB_Alarms_Compact"(Alarms := #AuxArray,
                             UsedAlarms := {used_alarms_count},
                             LastBitUsed := #AlmBit,
                             LastWordIndex := #AlmWord);
    END_FOR;
END_REGION ;\n\n"""
        return scl_content

    def generate_scl_file(self, scl_content, output_dir):
        """Genera il file SCL con il contenuto fornito"""
        try:
            # Percorso completo del file SCL (nella stessa directory del file Excel)
            scl_output_path = os.path.join(output_dir, "AlarmRegion.scl")
            
            # Scrivi il contenuto nel file
            with open(scl_output_path, 'w', encoding='utf-8') as f:
                f.write(scl_content)
            
            # Emetti il segnale di progresso con il percorso completo
            self.progress_signal.emit(f"File SCL generato con successo in:\n{scl_output_path}")
            return True
        except Exception as e:
            self.progress_signal.emit(f"Errore durante la generazione del file SCL: {str(e)}")
            return False

    def run(self):
        all_alarms_en = []
        all_alarms_fr = []
        current_id = 1
        all_scl_regions = []  # Lista per contenere tutte le regioni SCL
        
        try:
            self.progress_signal.emit(f"Leggendo il file di input: {os.path.basename(self.input_file)}...")
            with pd.ExcelFile(self.input_file) as xls:
                if not xls.sheet_names:
                    raise ValueError("Il file Excel non contiene fogli.")
                summary_sheet_name = xls.sheet_names[INPUT_FILE_SHEET_INDEX]
                summary_df = xls.parse(sheet_name=summary_sheet_name, header=0)
                self.progress_signal.emit(f"Foglio di riepilogo '{summary_sheet_name}' letto.")

                for object_type, count in self.instance_counts.items():
                    if count <= 0:
                        self.progress_signal.emit(f"Skipping {object_type} (numero istanze <= 0).")
                        continue

                    self.progress_signal.emit(f"Processing {object_type} ({count} istanze)...")

                    # Find offset and AlmWord index
                    offset_row = summary_df[summary_df[OBJECT_TYPE_COL] == object_type]
                    if offset_row.empty:
                        self.progress_signal.emit(f"WARN: Tipo oggetto '{object_type}' non trovato nel foglio di riepilogo. Skippato.")
                        continue
                    
                    # Recupera il valore della quarta colonna (word index)
                    alm_word_index_value = None
                    try:
                        # Cerca una colonna che contenga "word index" nel nome
                        word_index_col_name = None
                        for col_name in offset_row.columns:
                            if "word index" in col_name.lower():
                                word_index_col_name = col_name
                                break

                        if word_index_col_name:
                            alm_word_index_value = int(offset_row[word_index_col_name].iloc[0])
                            self.progress_signal.emit(f"Trovato 'word index' dalla colonna '{word_index_col_name}': {alm_word_index_value}")
                        elif len(offset_row.columns) > 3: # Se non trovo un nome specifico, uso l'indice 3
                            alm_word_index_value = int(offset_row.iloc[0, 3])
                            self.progress_signal.emit(f"Trovato 'word index' dalla quarta colonna (indice 3): {alm_word_index_value}")
                        else:
                            raise ValueError("La quarta colonna (word index) non è disponibile o non è stata trovata.")
                        
                    except (ValueError, TypeError, IndexError) as e:
                        self.progress_signal.emit(f"ERRORE: Impossibile recuperare il 'word index' per '{object_type}' dal foglio di riepilogo: {e}. Assicurati che la quarta colonna (word index) esista e contenga un numero intero valido.")
                        self.finished_signal.emit(False, f"Errore grave: {e}")
                        return # Termina l'esecuzione se non riesco a recuperare il word index

                    if OFFSET_COL not in offset_row.columns:
                         raise ValueError(f"Colonna '{OFFSET_COL}' non trovata nel foglio di riepilogo.")

                    offset_series = offset_row[OFFSET_COL].dropna()
                    if offset_series.empty:
                         self.progress_signal.emit(f"WARN: Offset '{OFFSET_COL}' non trovato o vuoto per '{object_type}'. Skippato.")
                         continue

                    try:
                        offset = int(offset_series.iloc[0])
                    except (ValueError, TypeError):
                         raise ValueError(f"Offset '{offset_series.iloc[0]}' per '{object_type}' non è un numero intero valido.")

                    # Check if sheet exists for the object type (case-insensitive check)
                    alarm_def_sheet_name = None
                    for name in xls.sheet_names:
                         if name.lower() == object_type.lower():
                            alarm_def_sheet_name = name
                            break
                    if alarm_def_sheet_name is None:
                         self.progress_signal.emit(f"WARN: Foglio '{object_type}' non trovato nel file Excel. Skippato.")
                         continue

                    alarm_def_df = xls.parse(sheet_name=alarm_def_sheet_name)
                    self.progress_signal.emit(f"Letto foglio '{alarm_def_sheet_name}' per {object_type}.")

                    if ADDRESS_COL not in alarm_def_df.columns:
                        raise ValueError(f"Colonna '{ADDRESS_COL}' non trovata nel foglio '{alarm_def_sheet_name}'.")

                    # Trova il nome effettivo della colonna Alarm Text
                    alarm_text_col_en = self._find_actual_column_name(ALARM_TEXT_COL_CANDIDATES, alarm_def_df.columns)
                    alarm_text_col_fr = self._find_actual_column_name(['Alarm Text (FR)'], alarm_def_df.columns)
                    if not alarm_text_col_en:
                        raise ValueError(f"Colonna 'Alarm Text (EN)' o 'Alarm Text' non trovata nel foglio '{alarm_def_sheet_name}'.")
                    if not alarm_text_col_fr:
                        self.progress_signal.emit(f"Colonna 'Alarm Text (FR)' non trovata nel foglio '{alarm_def_sheet_name}'. Verrà generato solo il file EN.")

                    # Collect unique alarms with text
                    unique_alarms = set()
                    for _, row in alarm_def_df.iterrows():
                        alarm_text = row[alarm_text_col_en]
                        if pd.notna(alarm_text) and alarm_text.strip():
                            unique_alarms.add(alarm_text.strip())

                    # Genera una regione SCL solo se ci sono allarmi con testo
                    if unique_alarms:
                        scl_region = self.generate_scl_region(
                            object_type,  # Pass full name for processing
                            sorted(list(unique_alarms)),  # Pass sorted list of unique alarms
                            alm_word_index_value # Passa il word index
                        )
                        all_scl_regions.append(scl_region)

                    # --- Existing logic for Excel output (keep this) ---
                    bit_index = 0  # Reset per ogni tipo oggetto
                    almword_index = alm_word_index_value  # Parte dal Word Index del tipo
                    for i in range(1, count + 1):
                        instance_offset_bytes = offset * (i - 1)
                        for _, row in alarm_def_df.iterrows():
                            alarm_text_en = row[alarm_text_col_en] if alarm_text_col_en in row else None
                            alarm_text_fr = row[alarm_text_col_fr] if alarm_text_col_fr and alarm_text_col_fr in row else None
                            address_str = str(row[ADDRESS_COL]).strip()

                            if pd.isna(alarm_text_en) or not alarm_text_en or not address_str:
                                continue

                            try:
                                rel_byte_str, bit_str = address_str.split('.')
                                rel_byte = int(rel_byte_str.strip())
                                bit = int(bit_str.strip())
                            except ValueError:
                                self.progress_signal.emit(f"WARN: Indirizzo '{address_str}' non valido (formato atteso: Byte.Bit) nel foglio '{alarm_def_sheet_name}', riga ignorata.")
                                continue

                            abs_byte = rel_byte + instance_offset_bytes
                            trigger_tag = f'AlmWord[{almword_index}]'
                            # EN
                            alarm_row_en = {col: None for col in OUTPUT_COLUMNS}
                            alarm_row_en['ID'] = current_id
                            alarm_row_en['Name'] = f"Discrete alarm_{current_id}"
                            alarm_row_en['Alarm text [en-US], Alarm text'] = str(alarm_text_en).replace('#', str(i))
                            alarm_row_en['FieldInfo [Alarm text]'] = ''
                            alarm_row_en['Class'] = 'Alarm'
                            alarm_row_en['Trigger tag'] = f'"{trigger_tag}"'
                            alarm_row_en['Trigger bit'] = bit_index
                            alarm_row_en['Acknowledgement tag'] = '<No value>'
                            alarm_row_en['Acknowledgement bit'] = 0
                            alarm_row_en['PLC acknowledgement tag'] = '<No value>'
                            alarm_row_en['PLC acknowledgement bit'] = 0
                            alarm_row_en['Group'] = '<No value>'
                            alarm_row_en['Report'] = 'False'
                            alarm_row_en['Info text [en-US], Info text'] = '<No value>'
                            all_alarms_en.append(alarm_row_en)
                            # FR
                            if alarm_text_col_fr and pd.notna(alarm_text_fr) and str(alarm_text_fr).strip():
                                alarm_row_fr = {col: None for col in OUTPUT_COLUMNS_FR}
                                alarm_row_fr['ID'] = current_id
                                alarm_row_fr['Name'] = f"Discrete alarm_{current_id}"
                                alarm_row_fr['Alarm text [fr-FR], Alarm text'] = str(alarm_text_fr).replace('#', str(i))
                                alarm_row_fr['FieldInfo [Alarm text]'] = ''
                                alarm_row_fr['Class'] = 'Alarm'
                                alarm_row_fr['Trigger tag'] = f'"{trigger_tag}"'
                                alarm_row_fr['Trigger bit'] = bit_index
                                alarm_row_fr['Acknowledgement tag'] = '<No value>'
                                alarm_row_fr['Acknowledgement bit'] = 0
                                alarm_row_fr['PLC acknowledgement tag'] = '<No value>'
                                alarm_row_fr['PLC acknowledgement bit'] = 0
                                alarm_row_fr['Group'] = '<No value>'
                                alarm_row_fr['Report'] = 'False'
                                alarm_row_fr['Info text [fr-FR], Info text'] = '<No value>'
                                all_alarms_fr.append(alarm_row_fr)
                            current_id += 1
                            bit_index += 1
                            if bit_index > 15:
                                bit_index = 0
                                almword_index += 1
                    # --- End existing logic for Excel output ---

            if not all_alarms_en and not all_alarms_fr:
                 self.progress_signal.emit("Nessun allarme valido trovato o generato. Il file di output non verrà creato.")
                 self.finished_signal.emit(True, "Nessun allarme generato. File non creato.")
                 return

            # Scrivi file EN
            if all_alarms_en:
                output_df_en = pd.DataFrame(all_alarms_en, columns=OUTPUT_COLUMNS)
                output_path_en = os.path.join(self.output_dir, 'HMIAlarms_EN.xlsx')
                self.progress_signal.emit(f"Scrivendo il file di output: {output_path_en}...")
                os.makedirs(self.output_dir, exist_ok=True)
                output_df_en.to_excel(output_path_en, index=False, sheet_name=OUTPUT_SHEET_NAME)
            # Scrivi file FR
            if all_alarms_fr:
                output_df_fr = pd.DataFrame(all_alarms_fr, columns=OUTPUT_COLUMNS_FR)
                output_path_fr = os.path.join(self.output_dir, 'HMIAlarms_FR.xlsx')
                self.progress_signal.emit(f"Scrivendo il file di output: {output_path_fr}...")
                os.makedirs(self.output_dir, exist_ok=True)
                output_df_fr.to_excel(output_path_fr, index=False, sheet_name=OUTPUT_SHEET_NAME)

            self.progress_signal.emit("Generazione completata con successo!")
            success_message = f"File EN/FR generati con successo in:\n{self.output_dir}"
            self.finished_signal.emit(True, success_message)

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

# --- Main Application Window ---
class AlarmGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file_path = None
        self.output_dir_path = os.getcwd() # Default to current dir
        self.object_types = {} # Dictionary to store {object_type: offset}
        self.generator_thread = None

        self.setWindowTitle("Generatore Allarmi TIA Portal")
        self.setGeometry(100, 100, 800, 600)

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Input File Selection ---
        input_layout = QHBoxLayout()
        self.input_file_label = QLineEdit("Nessun file selezionato")
        self.input_file_label.setReadOnly(True)
        self.input_file_button = QPushButton("Seleziona File Input (.xlsx)")
        self.input_file_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(QLabel("File Master:"))
        input_layout.addWidget(self.input_file_label)
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
        main_layout.addWidget(self.object_table)

        # --- Output Directory Selection ---
        output_layout = QHBoxLayout()
        self.output_dir_label = QLineEdit(self.output_dir_path)
        self.output_dir_label.setReadOnly(True)
        self.output_dir_button = QPushButton("Seleziona Cartella Output")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(QLabel("Cartella Output:"))
        output_layout.addWidget(self.output_dir_label)
        output_layout.addWidget(self.output_dir_button)
        main_layout.addLayout(output_layout)

        # --- Generate Button ---
        self.generate_button = QPushButton("Genera HMIAlarms.xlsx")
        self.generate_button.clicked.connect(self.start_generation)
        self.generate_button.setEnabled(False) # Disabled until file is selected
        main_layout.addWidget(self.generate_button)

        # --- Log Area ---
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(QLabel("Log:"))
        main_layout.addWidget(self.log_area)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto.")

        self.log_message("Applicazione avviata.")
        self._load_last_input_file() # Try loading the last used file on startup

    def _save_last_input_file(self, file_path):
        """Saves the given file path to the config file."""
        try:
            with open(CONFIG_FILENAME, 'w') as f:
                f.write(file_path)
            self.log_message(f"Percorso file salvato: {file_path}")
        except IOError as e:
            self.log_message(f"Errore durante il salvataggio del percorso file ({CONFIG_FILENAME}): {e}")

    def _load_last_input_file(self):
        """Loads the last used input file path from the config file if it exists and is valid."""
        if os.path.exists(CONFIG_FILENAME):
            try:
                with open(CONFIG_FILENAME, 'r') as f:
                    last_file_path = f.read().strip()

                if last_file_path and os.path.exists(last_file_path):
                    self.log_message(f"Trovato ultimo file valido: {last_file_path}. Caricamento...")
                    self.input_file_path = last_file_path
                    self.input_file_label.setText(os.path.basename(last_file_path))
                    self.load_object_types() # Load types if file is valid
                    if self.object_table.rowCount() > 0:
                        self.generate_button.setEnabled(True)
                        self.status_bar.showMessage(f"Ultimo file caricato: {os.path.basename(last_file_path)}")
                    else:
                        # If loading types failed for the saved file, reset
                        self.input_file_path = None
                        self.input_file_label.setText("Nessun file selezionato")
                        self.status_bar.showMessage("Ultimo file non valido o errore caricamento tipi.")
                else:
                    self.log_message("Percorso salvato non trovato o non valido.")
                    self.status_bar.showMessage("Pronto. Seleziona il file master.")
            except IOError as e:
                self.log_message(f"Errore durante la lettura del percorso file ({CONFIG_FILENAME}): {e}")
                self.status_bar.showMessage("Errore lettura configurazione.")
        else:
            self.log_message(f"File di configurazione ({CONFIG_FILENAME}) non trovato. Seleziona il file master.")
            self.status_bar.showMessage("Pronto. Seleziona il file master.")

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
            self.status_bar.showMessage(f"File selezionato: {os.path.basename(file_path)}")
            self.load_object_types()
            # Enable button only if types were loaded successfully
            if self.object_table.rowCount() > 0:
                 self.generate_button.setEnabled(True)
                 self._save_last_input_file(file_path) # Save the valid path
            else:
                 self.generate_button.setEnabled(False)
        else:
            self.log_message("Selezione file annullata.")
            self.status_bar.showMessage("Selezione file annullata.")

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella di Output",
            self.output_dir_path # Start from current selection
        )
        if dir_path:
            self.output_dir_path = dir_path
            self.output_dir_label.setText(dir_path)
            self.log_message(f"Cartella di output impostata: {dir_path}")
            self.status_bar.showMessage(f"Cartella output: {os.path.basename(dir_path)}")
        else:
             self.log_message("Selezione cartella output annullata.")

    def log_message(self, message):
        self.log_area.append(message)
        print(message) # Also print to console for debugging

    def _find_actual_column_name(self, target_name, column_list):
        """Finds the actual column name matching target_name, ignoring leading/trailing spaces."""
        for col in column_list:
            if str(col).strip() == target_name:
                return col
        return None

    def load_object_types(self):
        if not self.input_file_path:
            return

        try:
            self.log_message(f"Caricamento tipi oggetto da: {os.path.basename(self.input_file_path)}")
            # Use 'with' for reading object types as well
            with pd.ExcelFile(self.input_file_path) as xls:
                # Explicitly state that the header is in the first row (index 0)
                if not xls.sheet_names:
                     raise ValueError("Il file Excel non contiene fogli.")
                summary_df = xls.parse(sheet_name=xls.sheet_names[INPUT_FILE_SHEET_INDEX], header=0)

            # Find actual column names, ignoring leading/trailing spaces
            actual_obj_type_col = self._find_actual_column_name(OBJECT_TYPE_COL, summary_df.columns)
            actual_offset_col = self._find_actual_column_name(OFFSET_COL, summary_df.columns)

            # Check if columns were found
            if actual_obj_type_col is None:
                raise ValueError(f"Colonna '{OBJECT_TYPE_COL}' (o variante con spazi) non trovata nel primo foglio. Colonne trovate: {summary_df.columns.tolist()}")
            if actual_offset_col is None:
                raise ValueError(f"Colonna '{OFFSET_COL}' (o variante con spazi) non trovata nel primo foglio. Colonne trovate: {summary_df.columns.tolist()}")

            # Clear previous data
            self.object_types.clear()
            self.object_table.setRowCount(0)

            # Use the actual column names found
            processed_types = set() # Avoid adding duplicates if type appears multiple times
            for index, row in summary_df.iterrows():
                # Use actual column names found earlier
                obj_type = row[actual_obj_type_col]
                offset = row[actual_offset_col]

                # Check if object type is valid (not NaN, not empty) and offset is valid
                if pd.notna(obj_type) and str(obj_type).strip() and pd.notna(offset):
                     obj_type_str = str(obj_type).strip()
                     if obj_type_str in processed_types:
                         continue # Already processed this type

                     # Check if a sheet with this name exists
                     # Re-open ExcelFile here needed because the previous 'with' block closed it
                     # This is slightly inefficient, consider refactoring if performance is critical
                     with pd.ExcelFile(self.input_file_path) as xls_check:
                         sheet_exists = obj_type_str in xls_check.sheet_names

                     if sheet_exists:
                        try:
                            # Store the object type and its offset
                            self.object_types[obj_type_str] = int(offset)
                            self.add_object_type_to_table(obj_type_str)
                            processed_types.add(obj_type_str)
                        except ValueError:
                             self.log_message(f"WARN: Offset '{offset}' per '{obj_type_str}' non è un numero intero valido, tipo ignorato.")
                     else:
                         self.log_message(f"INFO: Tipo oggetto '{obj_type_str}' trovato nel riepilogo, ma nessun foglio corrispondente trovato. Ignorato.")

            self.log_message(f"Trovati {self.object_table.rowCount()} tipi oggetto validi con foglio corrispondente.")
            self.status_bar.showMessage(f"Tipi oggetto caricati da {os.path.basename(self.input_file_path)}")


        except FileNotFoundError:
            QMessageBox.critical(self, "Errore", f"File non trovato: {self.input_file_path}")
            self.log_message(f"Errore: File non trovato: {self.input_file_path}")
            self.status_bar.showMessage("Errore: File non trovato.")
            self.input_file_path = None
            self.input_file_label.setText("Nessun file selezionato")
            self.generate_button.setEnabled(False)
        except ValueError as ve:
             # Create message separately for multi-line f-string
             error_message = f"Errore nel formato del file Excel:\n{ve}"
             QMessageBox.critical(self, "Errore Dati Input", error_message)
             self.log_message(f"Errore dati input: {ve}")
             self.status_bar.showMessage("Errore nel formato del file Excel.")
             # Don't clear input file path, allow user to retry generation after fixing file maybe?
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore imprevisto durante la lettura del file:\n{e}")
            self.log_message(f"Errore imprevisto lettura file: {e}")
            self.status_bar.showMessage("Errore imprevisto.")
            import traceback
            self.log_message(traceback.format_exc()) # Log traceback for debugging

    def add_object_type_to_table(self, obj_type):
        row_position = self.object_table.rowCount()
        self.object_table.insertRow(row_position)

        # Column 0: Object Type (read-only)
        item_type = QTableWidgetItem(obj_type)
        item_type.setFlags(item_type.flags() & ~Qt.ItemFlag.ItemIsEditable) # Make read-only
        self.object_table.setItem(row_position, 0, item_type)

        # Column 1: Instance Count (SpinBox)
        spin_box = QSpinBox()
        spin_box.setMinimum(0)
        spin_box.setMaximum(999) # Set a reasonable maximum
        spin_box.setValue(0) # Default to 0 instances
        spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.object_table.setCellWidget(row_position, 1, spin_box)

    def get_instance_counts(self):
        counts = {}
        for row in range(self.object_table.rowCount()):
            type_item = self.object_table.item(row, 0)
            spin_box = self.object_table.cellWidget(row, 1)
            if type_item and spin_box:
                obj_type = type_item.text()
                count = spin_box.value()
                counts[obj_type] = count
        return counts

    def start_generation(self):
        if not self.input_file_path:
            QMessageBox.warning(self, "File Mancante", "Seleziona prima un file di input.")
            return

        instance_counts = self.get_instance_counts()
        if not instance_counts or all(v == 0 for v in instance_counts.values()):
             QMessageBox.warning(self, "Nessuna Istanza", "Inserisci il numero di istanze per almeno un tipo di oggetto.")
             return

        self.log_message("Avvio generazione allarmi...")
        self.generate_button.setEnabled(False)
        self.input_file_button.setEnabled(False) # Disable file selection during generation
        self.output_dir_button.setEnabled(False) # Disable output dir selection
        self.status_bar.showMessage("Generazione in corso...")

        # Run generation in a separate thread
        self.generator_thread = GeneratorThread(self.input_file_path, self.output_dir_path, instance_counts)
        self.generator_thread.progress_signal.connect(self.log_message)
        self.generator_thread.progress_signal.connect(self.status_bar.showMessage)
        self.generator_thread.finished_signal.connect(self.on_generation_finished)
        self.generator_thread.start()

    def on_generation_finished(self, success, message):
        self.generate_button.setEnabled(True)
        self.input_file_button.setEnabled(True)
        self.output_dir_button.setEnabled(True)
        self.status_bar.showMessage(message.split('\n')[0], 5000) # Show first line in status bar for 5s

        if success:
            QMessageBox.information(self, "Completato", message)
        else:
            QMessageBox.critical(self, "Errore Generazione", message)
        self.generator_thread = None # Clean up thread reference


# --- Main Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply a modern-ish style (Fusion)
    app.setStyle("Fusion")

    # Optional: Dark Theme Palette
    # palette = QPalette()
    # palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    # palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    # palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    # palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    # palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    # palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    # palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    # palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    # palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    # palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    # palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    # app.setPalette(palette)


    window = AlarmGeneratorApp()
    window.show()
    sys.exit(app.exec()) 