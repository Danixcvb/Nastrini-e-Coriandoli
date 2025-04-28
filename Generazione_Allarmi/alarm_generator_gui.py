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

# --- Constants ---
INPUT_FILE_SHEET_INDEX = 0
OBJECT_TYPE_COL = 'Object Type'
OFFSET_COL = 'Length (Byte) - SA'
ADDRESS_COL = 'Address'
ALARM_TEXT_COL = 'Alarm Text'
OUTPUT_FILENAME = 'HMIAlarms.xlsx'
OUTPUT_SHEET_NAME = 'DiscreteAlarms'
CONFIG_FILENAME = 'last_file.cfg' # File to store the last used input path

# Define the structure of the output Excel file based on the example
OUTPUT_COLUMNS = [
    'ID', 'Name', 'Alarm text [en-US], Alarm text 1', 'FieldInfo [Alarm text 1]',
    'Class', 'Trigger tag', 'Trigger bit', 'Trigger mode', 'Acknowledgement tag',
    'Acknowledgement bit', 'PLC acknowledgement tag', 'PLC acknowledgement bit',
    'Priority', 'Info text [en-US], Info text', 'Additional text 1 [en-US], Alarm text 2',
    'FieldInfo [Alarm text 2]', 'Additional text 2 [en-US], Alarm text 3',
    'FieldInfo [Alarm text 3]', 'Additional text 3 [en-US], Alarm text 4',
    'FieldInfo [Alarm text 4]', 'Additional text 4 [EN-US], Alarm text 5', # Corrected typo EN-US
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

    def run(self):
        all_alarms = []
        current_id = 1
        try:
            self.progress_signal.emit(f"Leggendo il file di input: {os.path.basename(self.input_file)}...")
            with pd.ExcelFile(self.input_file) as xls:
                summary_df = xls.parse(sheet_name=xls.sheet_names[INPUT_FILE_SHEET_INDEX], header=0)
                self.progress_signal.emit("Foglio di riepilogo letto.")

                for object_type, count in self.instance_counts.items():
                    if count <= 0:
                        self.progress_signal.emit(f"Skipping {object_type} (numero istanze <= 0).")
                        continue

                    self.progress_signal.emit(f"Processing {object_type} ({count} istanze)...")

                    # Find offset
                    offset_row = summary_df[summary_df[OBJECT_TYPE_COL] == object_type]
                    if offset_row.empty:
                        raise ValueError(f"Tipo oggetto '{object_type}' non trovato nel foglio di riepilogo.")
                    if OFFSET_COL not in offset_row.columns:
                         raise ValueError(f"Colonna '{OFFSET_COL}' non trovata nel foglio di riepilogo.")

                    # Handle potential multiple rows or missing values for offset
                    offset_series = offset_row[OFFSET_COL].dropna()
                    if offset_series.empty:
                        raise ValueError(f"Offset '{OFFSET_COL}' non trovato o vuoto per '{object_type}'.")

                    try:
                        offset = int(offset_series.iloc[0])
                    except ValueError:
                         raise ValueError(f"Offset '{offset_series.iloc[0]}' per '{object_type}' non è un numero intero valido.")


                    # Check if sheet exists for the object type
                    if object_type not in xls.sheet_names:
                         raise ValueError(f"Foglio '{object_type}' non trovato nel file Excel.")

                    alarm_def_df = xls.parse(sheet_name=object_type)
                    self.progress_signal.emit(f"Letto foglio definizione allarmi per {object_type}.")

                    if ADDRESS_COL not in alarm_def_df.columns:
                        raise ValueError(f"Colonna '{ADDRESS_COL}' non trovata nel foglio '{object_type}'.")
                    if ALARM_TEXT_COL not in alarm_def_df.columns:
                         raise ValueError(f"Colonna '{ALARM_TEXT_COL}' non trovata nel foglio '{object_type}'.")

                    for i in range(1, count + 1):
                        instance_offset_bytes = offset * (i - 1)
                        for _, row in alarm_def_df.iterrows():
                            alarm_text_template = row[ALARM_TEXT_COL]
                            address_str = str(row[ADDRESS_COL]).strip() # Ensure it's a string and remove whitespace

                            # Skip rows with empty or invalid address/alarm text
                            if pd.isna(alarm_text_template) or not alarm_text_template or not address_str:
                                continue

                            # Parse address (e.g., "0.1" or "2.0") using '.' as separator
                            try:
                                rel_byte_str, bit_str = address_str.split('.') # Changed separator from ',' to '.'
                                rel_byte = int(rel_byte_str.strip())
                                bit = int(bit_str.strip())
                            except ValueError:
                                self.progress_signal.emit(f"WARN: Indirizzo '{address_str}' non valido (formato atteso: Byte.Bit) nel foglio '{object_type}', riga ignorata.")
                                continue # Skip this row if address format is wrong

                            abs_byte = rel_byte + instance_offset_bytes
                            trigger_tag = f"{object_type}[{abs_byte}]"
                            alarm_text = str(alarm_text_template).replace('#', str(i))

                            # Create row for output DataFrame
                            # Default to None (empty cell), not '<No value>'
                            alarm_row = {col: None for col in OUTPUT_COLUMNS}

                            # Set specific values
                            alarm_row['ID'] = current_id
                            alarm_row['Name'] = f"Discrete alarm_{current_id}"
                            alarm_row['Alarm text [en-US], Alarm text 1'] = alarm_text
                            alarm_row['Class'] = 'Alarm'
                            alarm_row['Trigger tag'] = trigger_tag
                            alarm_row['Trigger bit'] = bit
                            alarm_row['Trigger mode'] = 'On rising edge'
                            alarm_row['Priority'] = 0 # Default or could be read from input if needed
                            alarm_row['Acknowledgement bit'] = 0
                            alarm_row['PLC acknowledgement bit'] = 0
                            alarm_row['Origin'] = 'HMI_RT_1::Alarming' # Or make this configurable
                            # Set Area to match Origin as a default
                            alarm_row['Area'] = 'HMI_RT_1::Alarming'

                            # Explicitly set columns that should contain the literal '<No value>' string
                            no_value_cols = [
                                'Acknowledgement tag', 'PLC acknowledgement tag', 'Info text [en-US], Info text',
                                'Alarm parameter 1', 'Alarm parameter 2', 'Alarm parameter 3', 'Alarm parameter 4',
                                'Alarm parameter 5', 'Alarm parameter 6', 'Alarm parameter 7', 'Alarm parameter 8',
                                'Alarm parameter 9', 'Alarm parameter 10'
                                # NOTE: FieldInfo and Additional Text columns will remain None (empty)
                            ]
                            for col in no_value_cols:
                                if col in alarm_row:
                                    alarm_row[col] = '<No value>'

                            all_alarms.append(alarm_row)
                            current_id += 1

            if not all_alarms:
                 self.progress_signal.emit("Nessun allarme valido trovato o generato. Il file di output non verrà creato.")
                 # Ensure we emit finished signal even if no file is written
                 self.finished_signal.emit(True, "Nessun allarme generato. File non creato.")
                 return

            output_df = pd.DataFrame(all_alarms, columns=OUTPUT_COLUMNS)
            # Check again before writing, just to be safe, although the previous check should suffice.
            if output_df.empty:
                self.progress_signal.emit("DataFrame vuoto, nessun file verrà creato.")
                self.finished_signal.emit(True, "Nessun allarme generato. File non creato.")
                return

            output_path = os.path.join(self.output_dir, OUTPUT_FILENAME)

            self.progress_signal.emit(f"Scrivendo il file di output: {output_path}...")
            output_df.to_excel(output_path, index=False, sheet_name=OUTPUT_SHEET_NAME)

            self.progress_signal.emit("Generazione completata con successo!")
            # Use a multi-line f-string or concatenate strings
            success_message = f"File '{OUTPUT_FILENAME}' generato con successo in:\n{self.output_dir}"
            self.finished_signal.emit(True, success_message)

        except FileNotFoundError:
             self.progress_signal.emit(f"Errore: File di input non trovato: {self.input_file}")
             # Create multi-line message separately
             error_message = f"Errore: File di input non trovato:\n{self.input_file}"
             self.finished_signal.emit(False, error_message)
        except ValueError as ve:
            self.progress_signal.emit(f"Errore nei dati: {ve}")
            # Create multi-line message separately
            error_message = f"Errore nei dati di input:\n{ve}"
            self.finished_signal.emit(False, error_message)
        except Exception as e:
            self.progress_signal.emit(f"Errore imprevisto durante la generazione: {e}")
            # Create multi-line message separately
            error_message = f"Errore imprevisto:\n{e}\nControlla i log per dettagli."
            self.finished_signal.emit(False, error_message)
            import traceback
            self.progress_signal.emit(traceback.format_exc()) # Log traceback for debugging

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