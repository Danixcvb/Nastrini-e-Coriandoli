"""
Questo modulo contiene la funzione principale di elaborazione che gestisce la generazione
delle configurazioni per i nastri trasportatori. Include la logica per l'elaborazione dei dati
e la creazione dei file di configurazione.
"""

import os
import pandas as pd
import re
from PyQt6.QtWidgets import QMessageBox, QApplication
import sys
from funzioni_elaborazione import (
    get_last_three_digits,
    count_ca_occurrences,
    get_value_or_default,
    extract_numeric_part,
    _get_item_details,
    calculate_tracking_slot_length,
    format_datalogic_hwid, # Added new import
    # generate_power_supply_breaker_status_ref # Rimosso per usare un valore fisso
)
from creazione_file import (
    create_txt_files,
    create_data_block_file,
    create_datalogic_file,
    create_linea_files,
    create_main_file,
    create_trunk_file,
    create_main_structure_file,
    create_conf_file,
    _is_valid_component_for_chain,
    generate_gen_line_file,
    create_dig_in_file, # Added new import
    generate_zones_input_scl, # Added new import for zones generation
    generate_pce_input_scl, # Added new import for PCE generation
    create_dig_out_file,
    generate_pce_output_scl
)
import random
import math

def process_excel(selected_cab_plc, status_var, root, order, excel_file_path):
    """
    Elabora il file Excel e genera le configurazioni per il CAB_PLC selezionato.
    
    Args:
        selected_cab_plc (str): CAB_PLC selezionato
        status_var: Variabile per lo stato dell'operazione
        root: Finestra principale
        order (list): Ordine selezionato per la generazione dei file
        excel_file_path (str): Percorso del file Excel da elaborare
        
    Returns:
        bool: True se l'elaborazione è completata con successo, False altrimenti
    """
    try:
        # Import show_completion_message here to avoid circular import
        # from interfaccia_grafica import show_completion_message
        
        # Inizializza il dizionario per mappare il tipo di linea (normale o carousel)
        line_type_mapping = {}
        # Inizializza il dizionario per mappare i trunk alle linee
        trunk_to_line_mapping = {}

        # status_var.set("Elaborazione in corso...")
        print("process_excel: Elaborazione in corso...")
        
        # Verifica se il file Excel è stato selezionato
        if not excel_file_path:
            # messagebox.showerror("Errore", "Nessun file Excel selezionato. Seleziona un file Excel prima di procedere.")
            print("Errore: nessun file selezionato")
            # status_var.set("Errore: nessun file selezionato")
            # Show error using QMessageBox if possible (requires QApplication instance)
            if QApplication.instance():
                 QMessageBox.critical(None, "Errore File", "Nessun file Excel selezionato. Seleziona un file Excel prima di procedere.")
            return False, "Nessun file Excel selezionato"
        
        if not os.path.exists(excel_file_path):
            # messagebox.showerror("Errore", f"Il file {excel_file_path} non esiste.")
            print(f"Errore: file non trovato: {excel_file_path}")
            # status_var.set("Errore: file non trovato")
            if QApplication.instance():
                 QMessageBox.critical(None, "Errore File", f"Il file Excel specificato non esiste:\n{excel_file_path}")
            return False, "File Excel non trovato"
            
        # Verifica se l'ordine è stato selezionato
        if not order:
            # messagebox.showerror("Errore", "Nessun ordine selezionato. Seleziona l'ordine di generazione prima di procedere.")
            print("Errore: nessun ordine selezionato")
            # status_var.set("Errore: nessun ordine selezionato")
            if QApplication.instance():
                 QMessageBox.critical(None, "Errore Ordine", "Nessun ordine di generazione selezionato. Seleziona l'ordine prima di procedere.")
            return False, "Nessun ordine selezionato"
        
        # Carica il file Excel
        df = pd.read_excel(excel_file_path)
        print(f"DataFrame caricato con {len(df)} righe")
        
        # Verifica le colonne richieste
        required_columns = ['ITEM_ID_CUSTOM', 'CAB_PLC', 'ITEM_TRUNK', 'ITEM_SPEED_TRANSPORT', 
                          'ITEM_SPEED_LAUNCH', 'ITEM_SPEED_MAX', 'ITEM_ACCELERATION', 'ITEM_L']
        if not all(col in df.columns for col in required_columns):
            # messagebox.showerror("Errore", "Alcune colonne richieste sono mancanti nel file Excel.")
            print("Errore: colonne mancanti nel file Excel")
            # status_var.set("Errore: colonne mancanti")
            if QApplication.instance():
                 QMessageBox.critical(None, "Errore Colonne", "Alcune colonne richieste sono mancanti nel file Excel.")
            return False, "Colonne mancanti nel file Excel"
        
        # Filtra le righe escludendo ITEM_ID_CUSTOM contenenti "RS", "CH", "XR", "SO", "IN",
        # Note: LC is now treated as SC (Datalogic) with "ATR Bottom" instead of "ATR 360"
        df = df[~df['ITEM_ID_CUSTOM'].str.contains('RS|CH|XR|SO|IN', case=False, na=False)]

        # Valori predefiniti per celle vuote
        default_speed_transport = 1.5
        default_speed_launch = 0.0
        default_speed_max = 2.0
        default_acceleration = 2.5
        default_item_l = 1600
        
        # Filtra il DataFrame per il CAB_PLC selezionato
        cab_plc_data = df[df['CAB_PLC'] == selected_cab_plc]
        
        # Verifica se ci sono dati per il CAB_PLC selezionato
        if cab_plc_data.empty:
            # messagebox.showerror("Errore", f"Nessun dato trovato per il CAB_PLC {selected_cab_plc} nel file Excel.")
            print(f"Errore: nessun dato trovato per {selected_cab_plc}")
            # status_var.set(f"Errore: nessun dato per {selected_cab_plc}")
            if QApplication.instance():
                 QMessageBox.critical(None, "Errore Dati", f"Nessun dato trovato per il CAB_PLC {selected_cab_plc} nel file Excel.")
            return False, f"Nessun dato per {selected_cab_plc}"
        
        # Controlla e pulisci la cartella del CAB_PLC se esiste
        output_folder = os.path.join('Configurazioni', selected_cab_plc)
        api_folder = f'API0{selected_cab_plc[-2:]}'
        api_output_folder = os.path.join(output_folder, api_folder)
        
        # Elimina file .scl vecchi di DbiLine e DbiTrunkLN prima di generare i nuovi .db
        if os.path.exists(api_output_folder):
            for file in os.listdir(api_output_folder):
                if (file.startswith('DbiLine') or file.startswith('DbiTrunkLN')) and file.endswith('.scl'):
                    old_file_path = os.path.join(api_output_folder, file)
                    try:
                        os.remove(old_file_path)
                        print(f"DEBUG - Rimosso file vecchio: {file}")
                    except Exception as e:
                        print(f"DEBUG - Impossibile rimuovere {file}: {e}")
        
        if os.path.exists(output_folder):
            # --- Replace Tkinter confirmation with QMessageBox --- 
            print(f"Trovata cartella preesistente: {output_folder}")
            confirmed = False
            # Check if QApplication instance exists before showing MessageBox
            app = QApplication.instance()
            if app:
                reply = QMessageBox.question(None, # No parent window specified
                                           "Conferma Eliminazione",
                                           f"La cartella di configurazione per '{selected_cab_plc}' esiste già:\n{output_folder}\n\nVuoi eliminare la cartella esistente e procedere con la nuova generazione?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No) # Default button
                if reply == QMessageBox.StandardButton.Yes:
                    confirmed = True
            else:
                 # Fallback to console confirmation if no GUI available
                 # Se siamo in modalità non interattiva (es. script di test), elimina automaticamente
                 import sys
                 try:
                     if not sys.stdin.isatty():
                         # Non interattivo: elimina automaticamente
                         confirmed = True
                         print(f"Modalità non interattiva: eliminazione automatica della cartella '{output_folder}'")
                     else:
                         reply_console = input(f"ATTENZIONE: La cartella '{output_folder}' esiste già. Eliminarla e procedere? (s/n): ").lower()
                         if reply_console == 's':
                             confirmed = True
                 except (EOFError, OSError):
                     # Se non possiamo leggere l'input, assumiamo modalità non interattiva
                     confirmed = True
                     print(f"Modalità non interattiva rilevata: eliminazione automatica della cartella '{output_folder}'")
            
            if confirmed:
                try:
                    import shutil
                    print(f"Eliminazione cartella: {output_folder}...")
                    shutil.rmtree(output_folder)
                    print(f"Cartella '{output_folder}' eliminata con successo.")
                except Exception as e:
                    print(f"Errore durante la pulizia della cartella: {e}")
                    print(f"Procedo comunque sovrascrivendo i file esistenti...")
                    # Non bloccare l'esecuzione se non si può eliminare la cartella
                    confirmed = True  # Procedi comunque
            # --- End of replacement ---

            if not confirmed:
                print("Operazione annullata dall'utente (non eliminazione cartella).")
                return False, "Operazione annullata dall'utente"
        
        # Crea i file .txt basati sui prefissi ITEM_ID_CUSTOM
        create_txt_files(cab_plc_data, selected_cab_plc, order)
        
        # Calcolo somma ITEM_L per elementi con doppio CA
        double_ca_items = cab_plc_data[cab_plc_data['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2].copy()
        
        if not double_ca_items.empty:
            double_ca_items['last_three_digits'] = double_ca_items['ITEM_ID_CUSTOM'].apply(get_last_three_digits)
            total_item_l_sum = double_ca_items['ITEM_L'].sum()
            min_digit_item = double_ca_items.loc[double_ca_items['last_three_digits'].idxmin()]
            min_item_id = min_digit_item['ITEM_ID_CUSTOM']
            
            df.loc[(df['ITEM_ID_CUSTOM'] == min_item_id) & (df['CAB_PLC'] == selected_cab_plc), 'ITEM_L'] = total_item_l_sum
            df.loc[(df['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2) & 
                  (df['CAB_PLC'] == selected_cab_plc) & 
                  (df['ITEM_ID_CUSTOM'] != min_item_id), 'ITEM_L'] = 0
            
            df = df[~((df['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2) & (df['ITEM_L'] == 0))]
        
        # Filtra nuovamente il DataFrame per il CAB_PLC selezionato
        df = df[df['CAB_PLC'] == selected_cab_plc]
        
        # Aggiunge colonna per il valore numerico per l'ordinamento
        df['NumericValue'] = df['ITEM_ID_CUSTOM'].apply(extract_numeric_part)
        
        # Aggiunge colonna per le ultime tre cifre
        df['LastThreeDigits'] = df['ITEM_ID_CUSTOM'].apply(get_last_three_digits)
        
        # Estrae i primi 4 caratteri di ITEM_ID_CUSTOM per il raggruppamento
        df['Prefix'] = df['ITEM_ID_CUSTOM'].astype(str).str[:4].str.lower()
        
        # Riordina il dataframe in base all'ordine selezionato dall'utente
        if order:
            order_mapping = {item.split('. ')[1] if '. ' in item else item: i for i, item in enumerate(order)}
            df['OrderPosition'] = df['Prefix'].map(lambda x: order_mapping.get(x[:4], 999))
            df = df.sort_values(by='OrderPosition')
        
        # Contatori per numeri Utenza e Carousel unici
        global_utenza_counter = 1
        global_carousel_counter = 1
        global_shutter_counter = 1 # Added global counter for SHUTTER

        
        # Estrai i prefissi ordinati direttamente dall'ordine selezionato
        ordered_prefixes = []
        prefix_order = {}
        if order:
            for i, item in enumerate(order):
                prefix = item.split('. ')[1] if '. ' in item else item
                prefix = prefix[:4].lower()  # Prendi solo i primi 4 caratteri
                ordered_prefixes.append(prefix)
                prefix_order[prefix] = i
        
        # Per ogni prefisso nell'ordine selezionato
        for prefix in ordered_prefixes:
            prefix_data = df[df['Prefix'] == prefix].copy()
            
            # Ordina il gruppo per le ultime tre cifre
            prefix_data = prefix_data.sort_values(by='LastThreeDigits')
            
            # Assegna numeri Utenza e Carousel
            for index, row in prefix_data.iterrows():
                item_id = str(row['ITEM_ID_CUSTOM'])
                
                if count_ca_occurrences(item_id) == 2:
                    df.at[index, 'GlobalCarouselNumber'] = global_carousel_counter
                    global_carousel_counter += 1
                    df.at[index, 'GlobalUtenzaNumber'] = None
                elif "ST" in item_id.upper() or "CN" in item_id.upper() or "CX" in item_id.upper():
                    df.at[index, 'GlobalUtenzaNumber'] = global_utenza_counter
                    global_utenza_counter += 1
                    df.at[index, 'GlobalCarouselNumber'] = None
                elif "SD" in item_id.upper(): # Added logic for SHUTTER
                    df.at[index, 'GlobalShutterNumber'] = global_shutter_counter
                    global_shutter_counter += 1
                    df.at[index, 'GlobalUtenzaNumber'] = None
                    df.at[index, 'GlobalCarouselNumber'] = None
                else:
                    df.at[index, 'GlobalUtenzaNumber'] = None
                    df.at[index, 'GlobalCarouselNumber'] = None
                    df.at[index, 'GlobalShutterNumber'] = None # Ensure shutter number is None for other types
        
        # Contatore globale per la numerazione progressiva dei file CONFT
        global_trunk_counter = 1
        
        # Identifica quale tronco contiene il carosello PRIMA del loop principale
        carousel_trunk_position = None
        temp_counter = 1
        for prefix in ordered_prefixes:
            prefix_data = df[df['Prefix'] == prefix]
            trunk_groups = prefix_data.groupby('ITEM_TRUNK')
            for trunk_name, trunk_group in trunk_groups:
                # Verifica se questo tronco contiene un carosello
                condition_ca2 = trunk_group['ITEM_ID_CUSTOM'].apply(lambda x: count_ca_occurrences(str(x)) == 2)
                if condition_ca2.any():
                    carousel_trunk_position = temp_counter
                    break
                temp_counter += 1
            if carousel_trunk_position is not None:
                break
        
        # Dizionario per memorizzare le configurazioni per numero di tronco
        configurations_by_trunk = {}
        # Dizionario per memorizzare i dati per i file MAIN
        main_data_by_trunk = {} 
        # Dizionario per memorizzare le configurazioni SIDE_INPUT per il tronco precedente
        side_input_configs_to_inject = {}
        # Lista per memorizzare i dati dei conveyor per la generazione del file DigIn.scl
        conveyor_data_for_dig_in = []
        # Lista per memorizzare i dati dei carousel per la generazione del file DigIn.scl
        carousel_data_for_dig_in = []

        # Itera attraverso ogni prefisso nell'ordine selezionato
        for prefix in ordered_prefixes:
            prefix_data = df[df['Prefix'] == prefix]
            trunk_groups = prefix_data.groupby('ITEM_TRUNK')
            
            for trunk_name, trunk_group in trunk_groups:
                # Determina se questo tronco contiene un carosello
                condition_ca2_check = trunk_group['ITEM_ID_CUSTOM'].apply(lambda x: count_ca_occurrences(str(x)) == 2)
                has_carousel_in_trunk = condition_ca2_check.any()
                
                # Usa "Carousel" come chiave se questo è il tronco con carosello
                if has_carousel_in_trunk and global_trunk_counter == carousel_trunk_position:
                    trunk_key = "Carousel"
                else:
                    trunk_key = global_trunk_counter
                
                configurations_by_trunk[trunk_key] = [] 
                # Aggiunge l'intestazione della funzione
                header = f"""FUNCTION "CONF_T{trunk_key}" : Void
 {{ S7_Optimized_Access := 'TRUE' }}
 VERSION : 0.1
 
 BEGIN
	
 """
                configurations_by_trunk[trunk_key].append(header)
                
                # Calcola il numero progressivo all'interno del gruppo
                progressive_number = 1
                
                # Ordina il gruppo per le ultime tre cifre di item_id_custom
                trunk_group = trunk_group.sort_values(by='LastThreeDigits')
                
                # Itera attraverso ogni riga del gruppo
                for index, row in trunk_group.iterrows():
                    try:
                        # Inizializza le variabili all'inizio di ogni iterazione
                        carousel_number = None
                        utenza_number = None
                        
                        item_id_custom = row['ITEM_ID_CUSTOM']
                        cab_plc = row['CAB_PLC']
                        item_speed_transport = row['ITEM_SPEED_TRANSPORT']
                        item_speed_launch = row['ITEM_SPEED_LAUNCH']
                        item_speed_max = row['ITEM_SPEED_MAX']
                        item_acceleration = row['ITEM_ACCELERATION']
                        item_l = row['ITEM_L']
                        
                        # Ottieni i numeri globali (potrebbero sovrascrivere None se presenti)
                        utenza_number = row.get('GlobalUtenzaNumber') 
                        carousel_number = row.get('GlobalCarouselNumber') 
                        
                        # Assicura che NaN diventi None
                        if pd.isna(utenza_number):
                            utenza_number = None
                        if pd.isna(carousel_number):
                            carousel_number = None
                        
                        comment_name = item_id_custom
                        
                        # Determina il nuovo ID custom basato sul tipo e numero
                        if count_ca_occurrences(comment_name) == 2 and carousel_number is not None:
                            try:
                                item_id_custom_new = f"Carousel{int(carousel_number)}"
                            except (ValueError, TypeError):
                                print(f"Attenzione: Impossibile convertire GlobalCarouselNumber '{carousel_number}' in intero per ITEM_ID_CUSTOM '{item_id_custom}'. Uso l'ID originale.")
                                item_id_custom_new = item_id_custom
                        elif ("ST" in item_id_custom.upper() or "CN" in item_id_custom.upper() or "CX" in item_id_custom.upper()) and utenza_number is not None:
                            try:
                                item_id_custom_new = f"Utenza{int(utenza_number)}_{item_id_custom}"
                            except (ValueError, TypeError):
                                print(f"Attenzione: Impossibile convertire GlobalUtenzaNumber '{utenza_number}' in intero per ITEM_ID_CUSTOM '{item_id_custom}'. Uso l'ID originale.")
                                item_id_custom_new = item_id_custom
                        else:
                            item_id_custom_new = item_id_custom
                        
                        # Ottieni valori di default se necessario
                        item_speed_transport = get_value_or_default(item_speed_transport, default_speed_transport)
                        item_speed_launch = get_value_or_default(item_speed_launch, default_speed_launch)
                        item_speed_max = get_value_or_default(item_speed_max, default_speed_max)
                        item_acceleration = get_value_or_default(item_acceleration, default_acceleration)
                        item_l = get_value_or_default(item_l, default_item_l)
                        
                        # Determina il tipo di componente usando l'ID originale per il conteggio
                        original_comment_name = item_id_custom.upper()
                        print(f"DEBUG - Elaborazione elemento: {item_id_custom_new}")
                        print(f"DEBUG - ID originale: {item_id_custom}")
                        print(f"DEBUG - Conteggio CA in ID originale: {count_ca_occurrences(original_comment_name)}")
                        
                        if "FD" in original_comment_name:
                            print(f"DEBUG - Trovato elemento FD: {item_id_custom}")
                            component_type = "FIRESHUTTER"
                        elif "SD" in original_comment_name:
                            print(f"DEBUG - Trovato elemento SD: {item_id_custom}")
                            component_type = "SHUTTER"
                        elif count_ca_occurrences(original_comment_name) == 2:
                            print(f"DEBUG - Trovato elemento CAROUSEL: {item_id_custom}")
                            print(f"DEBUG - Forzando tipo componente a Carousel")
                            component_type = "Carousel"
                        elif "OG" in original_comment_name:
                            print(f"DEBUG - Trovato elemento OVERSIZE: {item_id_custom}")
                            component_type = "OVERSIZE"
                        elif "SC" in original_comment_name or "LC" in original_comment_name:
                            print(f"DEBUG - Trovato elemento Datalogic: {item_id_custom}")
                            component_type = "Datalogic"
                        else:
                            print(f"DEBUG - Elemento non riconosciuto come speciale, impostato come Conveyor")
                            component_type = "Conveyor"
                        print(f"DEBUG - Tipo componente determinato: {component_type}")
                        

                        # Costruisci la stringa di configurazione
                        configuration = ""
                        
                        if component_type == "Datalogic":
                            # Determine comment based on LC vs SC
                            is_lc = "LC" in item_id_custom.upper()
                            comment_text = "ATR Bottom" if is_lc else "ATR 360"
                            configuration = f"""    REGION Config ATR CAMERA {comment_text} ({item_id_custom})

        REGION General data configuration
            "Datalogic_{item_id_custom}".Data.CNF.Position := 0.5;
            "Datalogic_{item_id_custom}".Data.CNF.MachineId := 21;
            "Datalogic_{item_id_custom}".Data.CNF.SeqScanner := 7160;
            "Datalogic_{item_id_custom}".Data.CNF.DbObjNum := 2011;
            
            REGION PROFINET interface connection
                
                REGION Address Configuration
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.InputHwId := "{format_datalogic_hwid(item_id_custom)}_CD009~IM_128ByteIn_1";
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.OutputHwId := "{format_datalogic_hwid(item_id_custom)}_CD009~OM_32ByteOut_1";
                    
                END_REGION

                REGION Driver Configuration
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.DadDriver := TRUE;
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.DpdDriver := FALSE;
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.DataConsistency := TRUE;
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.EnableIO := FALSE;
                    
                END_REGION
                
                REGION Parameters Configuration
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.TimeoutKeepAliveRecv := T#20S;
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.TimeoutKeepAliveSend := T#10S;
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.MsgSendDelay := T#100MS;
                    
                END_REGION
                
            END_REGION
            
        END_REGION
    

   END_REGION

"""
                        elif component_type == "FIRESHUTTER":
                            configuration = f"""    REGION Config FIRE SHUTTER  ({item_id_custom})
        //Managed directly in the MAINx
    END_REGION

"""
                        
                        elif component_type in ["Carousel", "Conveyor"]:
                            try:
                                item_l_float = float(item_l) / 1000.0
                            except (ValueError, TypeError):
                                print(f"Attenzione: Impossibile convertire ITEM_L '{item_l}' in float per ITEM_ID_CUSTOM '{item_id_custom}'. Uso il valore di default {default_item_l/1000.0}.")
                                item_l_float = default_item_l / 1000.0
                                
                            # Determina Conveyor_ID basato sul progressive_number
                            conveyor_id = progressive_number
                            
                            # Parte iniziale della configurazione - struttura API004_NEW
                            if component_type == "Conveyor":
                                initial_config_part = f"""	REGION Config CONVEYOR_SEW_MOVIGEAR ({comment_name})
	    REGION Conveyor.Data.CNF
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht01En := FALSE;      // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht02En := TRUE;       // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht03En := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht04En := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht01TrkEn := FALSE;      // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht02TrkEn := TRUE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht03TrkEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Pht04TrkEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.SlowdownOnAsrEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.LinkedToNext := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.AdjToSpeedNext := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.ExtDeltaEncoderEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.HmiControlEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.AntiShadowingEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.StrictGapEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.JamStopReqEn := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.EnableContaminationCheck := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.EnableSecurityStopCheck := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.Data.CNF.DbObjectsNumber := 1;       // [default=1]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Conveyor_ID := {conveyor_id:04d};       // [default=0000]
	        "{item_id_custom_new}".Conveyor.Data.CNF.UseTrunkNumber := {progressive_number};          // [default=1]
	        "{item_id_custom_new}".Conveyor.Data.CNF.TimeEnergySaving := T#120s;      // [default=T#30S]
	        "{item_id_custom_new}".Conveyor.Data.CNF.TimeEnergySavingAutotest := T#10S;      // [default=T#30S]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Speed1 := "DB_TEST_HMI".BONUS_SPEED + {item_speed_transport}; // [default=1.5] (m/s)
	        "{item_id_custom_new}".Conveyor.Data.CNF.Speed2 := {item_speed_launch};        // [default=0.0]
	        "{item_id_custom_new}".Conveyor.Data.CNF.SpeedLow := 0.0;        // [default=0.0]
	        "{item_id_custom_new}".Conveyor.Data.CNF.DriveMaxSpeed := 1.15;        // [default=1.15]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Acceleration := {item_acceleration};        // [default=2.5]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Length := {item_l_float};       // [default=1600]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Gap := 0.4;        // [default=0.4]
	        "{item_id_custom_new}".Conveyor.Data.CNF.Step := 0.0;        // [default=0.4]
	        "{item_id_custom_new}".Conveyor.Data.CNF.TrackingSlotLength := {calculate_tracking_slot_length(component_type, item_l_float)};       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Data.CNF.StopDistance := 0.6;        // [default=0.6]
	        "{item_id_custom_new}".Conveyor.Data.CNF.EndZone := 0.6;        // [default=0.6]
	        "{item_id_custom_new}".Conveyor.Data.CNF.ContaminationAreaLength := 0.15;        // [default=0.15]
	        
	    END_REGION
	    
	    REGION Conveyor.Pht01.Data.CNF
	        "{item_id_custom_new}".Conveyor.Pht01.Data.CNF.FlickeringMaxFp := 5;          // [default=5]
	        "{item_id_custom_new}".Conveyor.Pht01.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]
	        "{item_id_custom_new}".Conveyor.Pht01.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht01.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht01.Data.CNF.JamLengthThr := 3;          // [default=3]
	    END_REGION
	    
	    REGION Conveyor.Pht02.Data.CNF
	        "{item_id_custom_new}".Conveyor.Pht02.Data.CNF.FlickeringMaxFp := 5;          // [default=5]
	        "{item_id_custom_new}".Conveyor.Pht02.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]
	        "{item_id_custom_new}".Conveyor.Pht02.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht02.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht02.Data.CNF.JamLengthThr := 3;          // [default=3]
	    END_REGION
	    
	    REGION Conveyor.Pht03.Data.CNF
	        "{item_id_custom_new}".Conveyor.Pht03.Data.CNF.FlickeringMaxFp := 5;          // [default=5]
	        "{item_id_custom_new}".Conveyor.Pht03.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]
	        "{item_id_custom_new}".Conveyor.Pht03.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht03.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht03.Data.CNF.JamLengthThr := 3;          // [default=3]
	    END_REGION
	    
	    REGION Conveyor.Pht04.Data.CNF
	        "{item_id_custom_new}".Conveyor.Pht04.Data.CNF.FlickeringMaxFp := 5;          // [default=5]
	        "{item_id_custom_new}".Conveyor.Pht04.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]
	        "{item_id_custom_new}".Conveyor.Pht04.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht04.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]
	        "{item_id_custom_new}".Conveyor.Pht04.Data.CNF.JamLengthThr := 3;          // [default=3]
	    END_REGION
	    
	    REGION Conveyor.PhtTracking01.Data.CNF
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId ;          // [default=1]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.DecisionPointId := 0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.Position := "{item_id_custom_new}".Conveyor.Data.CNF.Length - 0.4;        // [default=400]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.TrkCtrlTolerance := 0.40;       // [default=0.35] 
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking01.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]
	        
	    END_REGION
	    
	    REGION Conveyor.PhtTracking02.Data.CNF
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId ;          // [default=1]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.DecisionPointId := 0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.Position := "{item_id_custom_new}".Conveyor.Data.CNF.Length - 0.4;         // [default=400]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.TrkCtrlTolerance := 0.35;       // [default=0.35]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking02.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]
	    END_REGION
	    
	    REGION Conveyor.PhtTracking03.Data.CNF
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId ;          // [default=1]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.DecisionPointId := 0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.Position := 0.4;        // [default=400]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.TrkCtrlTolerance := 0.35;       // [default=0.35]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking03.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]
	    END_REGION
	    
	    REGION Conveyor.PhtTracking04.Data.CNF
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId ;          // [default=1]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.DecisionPointId := 0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.Position := 0.4;        // [default=400]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.TrkCtrlTolerance := 0.35;       // [default=0.35]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]
	        "{item_id_custom_new}".Conveyor.PhtTracking04.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]
	    END_REGION
	    
	    REGION Encoder.Data.CNF
	        "{item_id_custom_new}".Encoder.Data.CNF.K_pulse := 0.0;        // [default=0.0]
	        "{item_id_custom_new}".Encoder.Data.CNF.SpeedTolerance := 0.0;        // [default=0.0]
	    END_REGION
	    
	    REGION Drive.Par
	        "{item_id_custom_new}".Drive.Data.Par.Direction := FALSE;      // [default=FALSE]
	        "{item_id_custom_new}".Drive.Data.Par.UseDriveSpeedYs := TRUE;       // [default=TRUE]
	        "{item_id_custom_new}".Drive.Data.Par.HwAddr := 0;          // [default=0]
	        "{item_id_custom_new}".Drive.Data.Par.MaxSpeed := 1.15;        // [default=1.15]
	        "{item_id_custom_new}".Drive.Data.Par.FeedbackTime := T#500MS;    // [default=T#500MS]
	    END_REGION
	    
	END_REGION
"""
                            else:  # Carousel - mantieni struttura originale per ora
                                initial_config_part = f"""    REGION Config CAROUSEL LINEAR FLAT ({comment_name})
                            REGION {component_type}.Data.CNF

        "{item_id_custom_new}".{component_type}.Data.CNF.Pht01En := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.Pht02En := TRUE; // [default=TRUE]
        "{item_id_custom_new}".{component_type}.Data.CNF.SlowdownOnAsrEn := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.LinkedToNext := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.AdjToSpeedNext := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.ExtDeltaEncoderEn := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.HmiControlEn := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.AntiShadowingEn := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.StrictGapEn := FALSE; // [default=FALSE]
        "{item_id_custom_new}".{component_type}.Data.CNF.DbObjectsNumber := 2011; // [default=2011]
        "{item_id_custom_new}".{component_type}.Data.CNF.DecisionPointId := 0; // [default=0]
        "{item_id_custom_new}".{component_type}.Data.CNF.UseTrunkNumber := {progressive_number}; // [default=1]
        "{item_id_custom_new}".{component_type}.Data.CNF.LapForEnergySaving := 1.5; // [default=1.5] Custom for Nizza
        "{item_id_custom_new}".{component_type}.Data.CNF.TimeEnergySaving := T#1s;  // [default=T#1s] (s) -> Nizza timing is managed by the laps for energy saving
        "{item_id_custom_new}".{component_type}.Data.CNF.Speed1 :=  "DB_TEST_HMI".BONUS_SPEED +{item_speed_transport}; // [default=1.5] (m/s)
        "{item_id_custom_new}".{component_type}.Data.CNF.Speed2 := {item_speed_launch}; // [default=0.0] (m/s)
        "{item_id_custom_new}".{component_type}.Data.CNF.SpeedLow := 0.0; // [default=0.0]
        "{item_id_custom_new}".{component_type}.Data.CNF.DriveMaxSpeed := "{item_id_custom_new}".Drive_1.Data.Par.MaxSpeed;        // [default=2.0] da machine table = {item_speed_max}
        "{item_id_custom_new}".{component_type}.Data.CNF.Acceleration := {item_acceleration}; // [default=2.5]
        "{item_id_custom_new}".{component_type}.Data.CNF.Length := {item_l_float}; // [default=1600]   (m)
        "{item_id_custom_new}".{component_type}.Data.CNF.Gap := 0.4; // [default=0.4]
        "{item_id_custom_new}".{component_type}.Data.CNF.Step := 0.4; // [default=0.4]
        "{item_id_custom_new}".{component_type}.Data.CNF.TrackingSlotLength := {calculate_tracking_slot_length(component_type, item_l_float)}; // [default=0.04] (m)
        "{item_id_custom_new}".{component_type}.Data.CNF.StopDistance := 0.6; // [default=0.6]
        "{item_id_custom_new}".{component_type}.Data.CNF.EndZone := 0.6; // [default=0.6]
        "{item_id_custom_new}".Carousel.Data.CNF.PitchControl1_Enable := FALSE; // [default=false]
        "{item_id_custom_new}".Carousel.Data.CNF.PitchControl2_Enable := FALSE; // [default=false]
        "{item_id_custom_new}".Carousel.Data.CNF.DelayCarouselFull := T#10s;    //[default=T#10s]
        "{item_id_custom_new}".Carousel.Data.CNF.DelaySecondCheck := T#5s;    //[default=T#20s]
        "{item_id_custom_new}".Carousel.Data.CNF.MinLengthForCarouselFull := 1.5;    //[default=1.5] (m)
    END_REGION
    
     REGION {component_type}.Pht01.Data.CNF
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.FlickeringMaxFp := 5; // [default=5]
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.FlickeringTime := T#500MS; // [default=T#500MS]
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.PhtRiseFilterThr := 0.04; // [default=0.04]
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.PhtFallFilterThr := 0.04; // [default=0.04]
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.JamLengthThr := 3; // [default=3]
        END_REGION
        
        REGION {component_type}.Pht02.Data.CNF
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.FlickeringMaxFp := 5; // [default=5]
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.FlickeringTime := T#500MS; // [default=T#500MS]
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.PhtRiseFilterThr := 0.04; // [default=0.04]
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.PhtFallFilterThr := 0.04; // [default=0.04]
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.JamLengthThr := 3; // [default=3]
        END_REGION
        
        REGION {component_type}.PhtTracking01.Data.CNF
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.VidGenerationEn := TRUE; // [default=TRUE]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.ObjLengthUpdateDis := FALSE; // [default=FALSE]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId; // [default=1]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.DecisionPointId := 0; // [default=0]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.MaxLostPiecesForJam := 3; // [default=3]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.Position := 0.4; // [default=400]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.TrkCtrlTollerance := 0.35; // [default=0.35]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.ObjLengthTollerance := 0; // [default=0]
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.TrackingPointID := dint#99999; //To be defined
        END_REGION
        
        REGION {component_type}.PhtTracking02.Data.CNF
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.VidGenerationEn := TRUE; // [default=TRUE]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.ObjLengthUpdateDis := FALSE; // [default=FALSE]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId; // [default=1]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.DecisionPointId := 0; // [default=0]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.MaxLostPiecesForJam := 3; // [default=3]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.Position := "{item_id_custom_new}".Conveyor.Data.CNF.Length - 0.3;       // [default=1200]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.TrkCtrlTollerance := 0.35; // [default=0.35]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.ObjLengthTollerance := 0; // [default=0]
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.TrackingPointID := dint#99999; //To be defined
        END_REGION
        
        REGION Encoder.Data.CNF
            "{item_id_custom_new}".Encoder.Data.CNF.K_pulse := 0.0; // [default=0.0]
            "{item_id_custom_new}".Encoder.Data.CNF.SpeedTollerance := 0.0; // [default=0.0]
        END_REGION

        REGION Drive_1.Data.Par 
            "{item_id_custom_new}".Drive_1.Data.Par.Direction := TRUE; // [default=FALSE]
            "{item_id_custom_new}".Drive_1.Data.Par.UseDriveSpeedYs := TRUE; // [default=TRUE]
            "{item_id_custom_new}".Drive_1.Data.Par.HwAddr := 0; // [default=0]
            "{item_id_custom_new}".Drive_1.Data.Par.MaxSpeed := 0.91; // [default=2.0]
            "{item_id_custom_new}".Drive_1.Data.Par.FeedbackTime := T#500MS; // [default=T#500MS]
        END_REGION
        
        REGION Drive_2.Data.Par 
            "{item_id_custom_new}".Drive_2.Data.Par.Direction := TRUE; // [default=FALSE]
            "{item_id_custom_new}".Drive_2.Data.Par.UseDriveSpeedYs := TRUE; // [default=TRUE]
            "{item_id_custom_new}".Drive_2.Data.Par.HwAddr := 0; // [default=0]
            "{item_id_custom_new}".Drive_2.Data.Par.MaxSpeed := 0.91; // [default=2.0]
            "{item_id_custom_new}".Drive_2.Data.Par.FeedbackTime := T#500MS; // [default=T#500MS]
        END_REGION"""
                                # Se ci sono 3 occorrenze di CA, aggiungi anche il motore 3
                                ca_count = count_ca_occurrences(original_comment_name)
                                if ca_count >= 3:
                                    initial_config_part += f"""
        REGION Drive_3.Data.Par 
            "{item_id_custom_new}".Drive_3.Data.Par.Direction := TRUE; // [default=FALSE]
            "{item_id_custom_new}".Drive_3.Data.Par.UseDriveSpeedYs := TRUE; // [default=TRUE]
            "{item_id_custom_new}".Drive_3.Data.Par.HwAddr := 0; // [default=0]
            "{item_id_custom_new}".Drive_3.Data.Par.MaxSpeed := 0.91; // [default=2.0]
            "{item_id_custom_new}".Drive_3.Data.Par.FeedbackTime := T#500MS; // [default=T#500MS]
        END_REGION
        END_REGION
"""
                                else:
                                    initial_config_part += """
        END_REGION
"""
                            
                            # Assembla la configurazione finale
                            configuration = initial_config_part

                        # Aggiungi la configurazione e crea i file necessari
                        if component_type == "Datalogic":
                            output_folder = f'Configurazioni/{selected_cab_plc}/API0{selected_cab_plc[-2:]}'
                            print(f"DEBUG: Creazione file datalogic per {item_id_custom} in {output_folder}")
                            create_datalogic_file(item_id_custom, output_folder)
                            if configuration:
                                configurations_by_trunk[trunk_key].append(configuration)
                        elif component_type == "Carousel":
                            output_folder = f'Configurazioni/{selected_cab_plc}/API0{selected_cab_plc[-2:]}'
                            create_data_block_file(item_id_custom_new, component_type, output_folder, line_type_mapping)
                            if configuration:
                                configurations_by_trunk[trunk_key].append(configuration)
                            
                            print(f"DEBUG - Trovato Carousel: {item_id_custom_new} (originale: {item_id_custom})")
                            print(f"DEBUG - trunk_group size: {len(trunk_group)}")
                            
                            # Raccogli i dati del carousel per il file DigIn.scl
                            # Trova tutti i motori CA nello stesso tronco E con lo stesso prefisso (escludendo il carousel principale che ha 2 occorrenze di CA)
                            # Estrai il prefisso dal carousel (primi 4 caratteri, es. "CA11" da "CA11CA023")
                            carousel_prefix = item_id_custom[:4].upper() if len(item_id_custom) >= 4 else ""
                            print(f"DEBUG - Prefisso carousel: {carousel_prefix}")
                            
                            ca_motors = []
                            # Cerca prima nello stesso tronco
                            # I motori del carousel possono avere formato diverso:
                            # - "CA030", "CA045" (1 occorrenza di CA) 
                            # - "CA11CA030", "CA11CA045" (2 occorrenze di CA, ma diversi dal carousel principale)
                            for idx, motor_row in trunk_group.iterrows():
                                motor_id = str(motor_row['ITEM_ID_CUSTOM']).upper()
                                ca_count = count_ca_occurrences(motor_id)
                                motor_prefix = motor_id[:4] if len(motor_id) >= 4 else ""
                                print(f"DEBUG - Motor check (stesso tronco): {motor_id}, CA count: {ca_count}, prefix: {motor_prefix}, carousel_id: {item_id_custom.upper()}")
                                # I motori del carousel sono elementi CA che:
                                # 1. Hanno lo stesso prefisso del carousel (primi 4 caratteri)
                                # 2. NON sono il carousel principale stesso
                                # 3. Contengono "CA" nel nome
                                if 'CA' in motor_id and motor_prefix == carousel_prefix:
                                    # Escludi il carousel principale stesso
                                    if motor_id != item_id_custom.upper():
                                        # Accetta qualsiasi elemento CA con lo stesso prefisso (sia 1 che 2 occorrenze di CA)
                                        ca_motors.append({
                                            'item_id': motor_row['ITEM_ID_CUSTOM'],
                                            'item_id_upper': motor_id,
                                            'index': idx,
                                            'trunk': trunk_key
                                        })
                                        print(f"DEBUG - Motore CA trovato nello stesso tronco: {motor_id} (CA count: {ca_count})")
                            
                            # Se non trovati nello stesso tronco, cerca in tutti i dati del prefisso corrente con lo stesso prefisso
                            if len(ca_motors) == 0:
                                print(f"DEBUG - Nessun motore trovato nello stesso tronco, cerco in tutti i dati del prefisso {carousel_prefix}")
                                # Cerca SEMPRE in cab_plc_data per trovare tutti gli elementi CA con lo stesso prefisso
                                # Questo garantisce di trovare i motori anche se sono in tronchi diversi
                                print(f"DEBUG - Cerco in cab_plc_data (totale righe: {len(cab_plc_data)})")
                                for idx, motor_row in cab_plc_data.iterrows():
                                    motor_id = str(motor_row['ITEM_ID_CUSTOM']).upper()
                                    motor_prefix = motor_id[:4] if len(motor_id) >= 4 else ""
                                    if motor_prefix == carousel_prefix:
                                        ca_count = count_ca_occurrences(motor_id)
                                        motor_trunk = motor_row.get('ITEM_TRUNK')
                                        # I motori del carousel sono elementi CA con stesso prefisso ma diversi dal carousel principale
                                        if 'CA' in motor_id and motor_prefix == carousel_prefix:
                                            # Escludi il carousel principale stesso
                                            if motor_id != item_id_custom.upper():
                                                # Accetta qualsiasi elemento CA con lo stesso prefisso (sia 1 che 2 occorrenze di CA)
                                                # Evita duplicati
                                                if not any(m['item_id'] == motor_row['ITEM_ID_CUSTOM'] for m in ca_motors):
                                                    ca_motors.append({
                                                        'item_id': motor_row['ITEM_ID_CUSTOM'],
                                                        'item_id_upper': motor_id,
                                                        'index': idx,
                                                        'trunk': motor_trunk
                                                    })
                                                    print(f"DEBUG - Motore trovato in cab_plc_data: {motor_id} (tronco: {motor_trunk}, CA count: {ca_count})")
                            
                            print(f"DEBUG - ca_motors trovati: {len(ca_motors)}")
                            
                            # Ordina i motori per ordine di apparizione nel tronco (usando l'indice originale)
                            ca_motors_sorted = sorted(ca_motors, key=lambda x: x['index'])
                            
                            # LIMITAZIONE: Prendi solo i primi 3 motori CA trovati (per ora, come richiesto)
                            ca_motors_sorted = ca_motors_sorted[:3]
                            print(f"DEBUG - ca_motors dopo limitazione a 3: {len(ca_motors_sorted)}")
                            
                            # Prepara i dati per ogni motore
                            motor_data_list = []
                            for i, motor in enumerate(ca_motors_sorted, start=1):
                                motor_item_id = motor['item_id']
                                motor_item_id_upper = motor['item_id_upper']
                                
                                # Aggiungi underscore dopo il prefisso se necessario
                                motor_item_id_with_underscore = motor_item_id
                                if len(motor_item_id) >= 4:
                                    prefix = motor_item_id[:4]
                                    rest = motor_item_id[4:]
                                    if rest and rest.startswith('CA'):
                                        motor_item_id_with_underscore = f"{prefix}_{rest}"
                                
                                motor_data_list.append({
                                    'motor_number': i,
                                    'item_id': motor_item_id,
                                    'item_id_with_underscore': motor_item_id_with_underscore,
                                    'safety_switch_ref': f"{motor_item_id_with_underscore}_T0001_SAFETY_SWITCH_POWER_SUPPLY_400V".replace("-", "_").replace(" ", "_").upper(),
                                    'key_switch_ref': f"{motor_item_id_with_underscore}_T0001_KEY_SWITCH_LOCAL_MODE".replace("-", "_").replace(" ", "_").upper(),
                                    'motor_group_inserted_ref': f"{motor_item_id_with_underscore}_B2002_GROUP_INSERTERD".replace("-", "_").replace(" ", "_").upper(),
                                    'pitch_control_ref': f"{motor_item_id_with_underscore}_B2001_CAROUSEL_PITCH_CONTROL_SENSOR".replace("-", "_").replace(" ", "_").upper(),
                                    'telegram_ref': f"{motor_item_id.upper()}_IN",
                                    'profinet_index': None  # Sarà calcolato dopo
                                })
                            
                            # Calcola i profinet_index (partono da un valore base, es. 18 per il primo motore)
                            base_profinet_index = 18  # Valore di esempio, potrebbe essere calcolato dinamicamente
                            for i, motor_data in enumerate(motor_data_list):
                                motor_data['profinet_index'] = base_profinet_index + i
                            
                            # Se non ci sono motori, salta l'aggiunta del carousel (o aggiungi comunque con lista vuota?)
                            if len(motor_data_list) == 0:
                                print(f"DEBUG - ATTENZIONE: Carousel {item_id_custom_new} trovato ma nessun motore CA con 1 occorrenza nello stesso tronco!")
                                print(f"DEBUG - Elementi nel tronco:")
                                for idx, motor_row in trunk_group.iterrows():
                                    motor_id = str(motor_row['ITEM_ID_CUSTOM']).upper()
                                    ca_count = count_ca_occurrences(motor_id)
                                    print(f"  - {motor_row['ITEM_ID_CUSTOM']}: CA count = {ca_count}")
                            
                            # Trova le booking photocells (Pht01 e Pht02) - potrebbero essere nel tronco o nel tronco successivo
                            # Per ora usiamo valori di esempio basati sul primo e ultimo motore
                            booking_pht01_ref = None
                            booking_pht02_ref = None
                            if len(motor_data_list) > 0:
                                first_motor = motor_data_list[0]
                                last_motor = motor_data_list[-1]
                                prefix = first_motor['item_id'][:4] if len(first_motor['item_id']) >= 4 else ""
                                # Booking photocell 1 potrebbe essere vicino al primo motore
                                booking_pht01_ref = f"{prefix}_CA023_B6901_BOOKING_PHOTOCELL".replace("-", "_").replace(" ", "_").upper()
                                # Booking photocell 2 potrebbe essere vicino all'ultimo motore
                                booking_pht02_ref = f"{prefix}_CA065_B6901_BOOKING_PHOTOCELL".replace("-", "_").replace(" ", "_").upper()
                            
                            # Power supply breaker status (comune per tutti i motori)
                            power_supply_breaker_status_ref = ""
                            if len(motor_data_list) > 0:
                                power_supply_breaker_status_ref = f"MCP{selected_cab_plc[-2:]}_130F3_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_INVERTER_{motor_data_list[0]['item_id_upper']}_{motor_data_list[-1]['item_id_upper'] if len(motor_data_list) > 1 else motor_data_list[0]['item_id_upper']}".replace("-", "_").replace(" ", "_").upper()
                            
                            # Motor group rotating (solo per il primo motore)
                            motor_group_rotating_ref = motor_data_list[0]['motor_group_inserted_ref'].replace("GROUP_INSERTERD", "GROUP_ROTATING") if len(motor_data_list) > 0 else ""
                            
                            # Aggiungi il carousel solo se ci sono motori
                            if len(motor_data_list) > 0:
                                carousel_entry = {
                                    'carousel_id': item_id_custom_new,  # es. "Carousel1"
                                    'comment_name': item_id_custom,  # es. "CA11CA023"
                                    'motors': motor_data_list,
                                    'booking_pht01_ref': booking_pht01_ref,
                                    'booking_pht02_ref': booking_pht02_ref,
                                    'power_supply_breaker_status_ref': power_supply_breaker_status_ref,
                                    'motor_group_rotating_ref': motor_group_rotating_ref,
                                    'selected_cab_plc': selected_cab_plc
                                }
                                print(f"DEBUG - Aggiungo carousel_data: {carousel_entry['carousel_id']}, motors: {len(motor_data_list)}")
                                carousel_data_for_dig_in.append(carousel_entry)
                            else:
                                print(f"DEBUG - Carousel {item_id_custom_new} saltato perché non ci sono motori")
                        elif component_type == "Conveyor": # Per i Conveyor, la logica DriveInterface.Par rimane invariata
                            output_folder = f'Configurazioni/{selected_cab_plc}/API0{selected_cab_plc[-2:]}'
                            create_data_block_file(item_id_custom_new, component_type, output_folder, line_type_mapping)
                            if configuration:
                                configurations_by_trunk[trunk_key].append(configuration)
                            
                            # Raccogli i dati del conveyor per il file DigIn.scl
                            profinet_index = 11 # Valore fisso per ora, da definire meglio se necessario
                            # Aggiungi underscore dopo il nome della linea (es. CP21ST025 -> CP21_ST025)
                            item_id_with_underscore = item_id_custom
                            if len(item_id_custom) >= 4:
                                # Estrai prefisso (primi 4 caratteri) e resto
                                prefix = item_id_custom[:4]
                                rest = item_id_custom[4:]
                                # Se il resto inizia con ST, CN, CX, aggiungi underscore dopo il prefisso
                                if rest and (rest.startswith('ST') or rest.startswith('CN') or rest.startswith('CX')):
                                    item_id_with_underscore = f"{prefix}_{rest}"
                            
                            safety_switch_ref = f"{item_id_with_underscore}_T0001_SAFETY_SWITCH_POWER_SUPPLY_400V".replace("-", "_").replace(" ", "_").upper()
                            key_switch_local_mode_ref = f"{item_id_with_underscore}_T0001_KEY_SWITCH_LOCAL_MODE".replace("-", "_").replace(" ", "_").upper()
                            stop_head_photocell_ref = f"{item_id_with_underscore}_B1101_STOP_HEAD_PHOTOCELL".replace("-", "_").replace(" ", "_").upper()
                            power_supply_breaker_status_ref = "MCP_130F1_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_INVERTER_ST001_ST007" # Valore fisso come richiesto

                            conveyor_data_for_dig_in.append({
                                'item_id_custom_new': item_id_custom_new,
                                'comment_name': item_id_custom,
                                'profinet_index': profinet_index,
                                'safety_switch_ref': safety_switch_ref,
                                'key_switch_local_mode_ref': key_switch_local_mode_ref,
                                'stop_head_photocell_ref': stop_head_photocell_ref,
                                'power_supply_breaker_status_ref': power_supply_breaker_status_ref
                            })

                        elif component_type in ["SHUTTER", "FIRESHUTTER", "OVERSIZE"]:
                            output_folder = f'Configurazioni/{selected_cab_plc}/API0{selected_cab_plc[-2:]}'
                            create_data_block_file(item_id_custom_new, component_type, output_folder, line_type_mapping)
                            # Non aggiungiamo la 'configuration' qui, poiché la loro regione CONF_Tx è gestita separatamente
                            # configurations_by_trunk[global_trunk_counter].append(configuration)
                        
                        # Incrementa il numero progressivo all'interno del gruppo
                        progressive_number += 1
                            
                    except Exception as e:
                        print(f"Errore durante l'elaborazione dell'item {item_id_custom}: {e}")
                        continue
                
                # Filtra e Memorizza dati per MAIN
                condition_st = trunk_group['ITEM_ID_CUSTOM'].str.contains('ST', case=False, na=False)
                condition_cn = trunk_group['ITEM_ID_CUSTOM'].str.contains('CN', case=False, na=False)
                condition_cx = trunk_group['ITEM_ID_CUSTOM'].str.contains('CX', case=False, na=False)
                condition_ca2 = trunk_group['ITEM_ID_CUSTOM'].apply(lambda x: count_ca_occurrences(str(x)) == 2)
                condition_sc = trunk_group['ITEM_ID_CUSTOM'].str.contains('SC|LC', case=False, na=False)
                condition_fd = trunk_group['ITEM_ID_CUSTOM'].str.contains('FD', case=False, na=False)
                condition_sd = trunk_group['ITEM_ID_CUSTOM'].str.contains('SD', case=False, na=False)
                condition_og = trunk_group['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)

                # Includi anche i Datalogic (SC), FIRESHUTTER (FD) e SHUTTER (SD) nella lista degli elementi validi
                valid_items_for_main = trunk_group[condition_st | condition_cn | condition_cx | condition_ca2 | condition_sc | condition_fd | condition_sd | condition_og]

                if not valid_items_for_main.empty:
                    items_ordered_dict = valid_items_for_main.sort_values(by='LastThreeDigits').to_dict('records')
                    # Usa la stessa trunk_key determinata sopra
                    main_data_by_trunk[trunk_key] = items_ordered_dict
                
                # Aggiungi qui la logica per la regione OVERSIZE per CONF_Tx
                oversize_conf_counter = 1
                oversize_items_in_trunk = trunk_group[trunk_group['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)].copy()
                
                if not oversize_items_in_trunk.empty:
                    for _ in oversize_items_in_trunk.iterrows():
                        configurations_by_trunk[trunk_key].append(f'    REGION Config Oversize{oversize_conf_counter}')
                        configurations_by_trunk[trunk_key].append('        ')
                        configurations_by_trunk[trunk_key].append(f'        "Oversize{oversize_conf_counter}".DATA.CNF.MaxLength := 0.9; //m')
                        configurations_by_trunk[trunk_key].append('        ')
                        configurations_by_trunk[trunk_key].append('    END_REGION')
                        configurations_by_trunk[trunk_key].append('')
                        oversize_conf_counter += 1
                
                # Aggiungi qui la logica per la regione SHUTTER per CONF_Tx
                shutter_conf_counter = 1
                shutter_items_in_trunk = trunk_group[trunk_group['ITEM_ID_CUSTOM'].str.contains('SD', case=False, na=False)].copy()
                
                if not shutter_items_in_trunk.empty:
                    for item_idx, _ in shutter_items_in_trunk.iterrows():
                        item_id_original = shutter_items_in_trunk.loc[item_idx, 'ITEM_ID_CUSTOM'] # Ottieni l'item_id_original
                        configurations_by_trunk[trunk_key].append(f'    REGION Config SECURITY SHUTTER ({item_id_original})')
                        configurations_by_trunk[trunk_key].append(f'        "SHUTTER{shutter_conf_counter}".Data.CNF.Timeout_opening := T#10s;')
                        configurations_by_trunk[trunk_key].append(f'        "SHUTTER{shutter_conf_counter}".Data.CNF.Timeout_closing := T#10s;')
                        configurations_by_trunk[trunk_key].append(f'        "SHUTTER{shutter_conf_counter}".Data.CNF.Command_pulse_duration := T#1000ms;')
                        configurations_by_trunk[trunk_key].append('    END_REGION')
                        configurations_by_trunk[trunk_key].append('')
                        shutter_conf_counter += 1
                
                # Identifica i caroselli nel tronco corrente per la logica SIDE_INPUT_CAROUSEL
                carousel_items_in_trunk_for_side_input = trunk_group[trunk_group['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2].copy()

                # Aggiungi qui la logica per la regione SIDE_INPUT_CAROUSEL per CONF_Tx
                # Genera un SIDE_INPUT_CAROUSEL per ogni CAROUSEL presente nel tronco
                if not carousel_items_in_trunk_for_side_input.empty:
                    for item_idx, carousel_row in carousel_items_in_trunk_for_side_input.iterrows():
                        carousel_number = carousel_row.get('GlobalCarouselNumber')
                        if carousel_number is not None:
                            side_input_carousel_num = int(carousel_number)
                            
                            # Costruisci la configurazione Side_Input_Carousel
                            side_input_config_content = [
                                f'    REGION Config Side_Input_Carousel{side_input_carousel_num}',
                                '',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.InputAreaPosition := 5.5; //Distanza rispetto all\'inizio immaginario del nastro carosello',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.InputAreaLength := 1.3; //Larghezza in metri dello spazio libero necessario per scaricare',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.LoadLength := 1.2; // Quando carico scrivo negli slot di tracking del carosello questa lunghezza fissa',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.StopRetainTime := T#1S; //Non utilizzato',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.TransferTime := T#500ms; //',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.MachineId := 0;',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.UseNextObjTransferInForDelay := TRUE; // Alway true for every side input',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.NextObjTransferInDelayTransfer := T#500MS; // T#8500MS; // Time needed to create the gap between the last object',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.UsePrevFullStatusToReqAsr := FALSE; // TRUE only for side input on recirculation lane',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.UseBufferingStatusToReqAsr := FALSE; // TRUE only for side input on accumulation lane',
                                f'        "Side_Input_Carousel{side_input_carousel_num}".DATA.CNF.InjectionCarouselManualEnable := TRUE; // [default=FALSE]',
                                '',
                                '    END_REGION',
                                ''
                            ]
                            
                            # Salva la configurazione per il tronco precedente
                            # Calcola il tronco precedente considerando Carousel
                            prev_trunk_num_raw = global_trunk_counter - 1
                            
                            # Se il tronco precedente è quello che contiene il Carousel, usa "Carousel" come chiave
                            if carousel_trunk_position is not None and prev_trunk_num_raw == carousel_trunk_position:
                                prev_trunk_key = "Carousel"
                            else:
                                prev_trunk_key = prev_trunk_num_raw
                            
                            if prev_trunk_num_raw > 0: # Assicurati che esista un tronco precedente valido
                                if prev_trunk_key not in side_input_configs_to_inject:
                                    side_input_configs_to_inject[prev_trunk_key] = []
                                side_input_configs_to_inject[prev_trunk_key].extend(side_input_config_content)
                            else:
                                print(f"DEBUG - Non è possibile generare Side_Input_Carousel{side_input_carousel_num} per il tronco {trunk_key} in quanto non esiste un tronco precedente.")
                        else:
                            print(f"DEBUG - Impossibile trovare GlobalCarouselNumber per SIDE_INPUT associato a ITEM_ID_CUSTOM: {carousel_row.get('ITEM_ID_CUSTOM', 'N/A')}")
                
                # Aggiunge END_FUNCTION alla fine delle configurazioni del tronco
                configurations_by_trunk[trunk_key].append("END_FUNCTION")
                
                # Incrementa il contatore globale (anche se abbiamo usato "Carousel" come chiave)
                # Questo scalerà automaticamente i tronchi successivi
                global_trunk_counter += 1
        
        # Inietta le configurazioni SIDE_INPUT_CAROUSEL nei tronchi precedenti
        for trunk_num_to_inject, configs_to_add in side_input_configs_to_inject.items():
            if trunk_num_to_inject in configurations_by_trunk:
                # Trova la posizione di END_FUNCTION e inserisci prima
                end_function_index = -1
                for i, line in enumerate(configurations_by_trunk[trunk_num_to_inject]):
                    if line == "END_FUNCTION":
                        end_function_index = i
                        break
                
                if end_function_index != -1:
                    configurations_by_trunk[trunk_num_to_inject][end_function_index:end_function_index] = configs_to_add
                    print(f"DEBUG - Inserita configurazione Side_Input_Carousel nel tronco {trunk_num_to_inject}")
                else:
                    print(f"AVVISO - END_FUNCTION non trovato nel tronco {trunk_num_to_inject}, configurazione Side_Input_Carousel non inserita.")
            else:
                print(f"AVVISO - Il tronco {trunk_num_to_inject} non esiste in configurations_by_trunk, configurazione Side_Input_Carousel non inserita.")

        # Salva le configurazioni CONF_T in file separati per tronco
        files_created = [] 
        # Gestisci sia numeri che "Carousel" nell'ordinamento
        trunk_keys = configurations_by_trunk.keys()
        numeric_trunks = sorted([k for k in trunk_keys if isinstance(k, int)])
        carousel_trunk = [k for k in trunk_keys if isinstance(k, str) and k == "Carousel"]
        sorted_trunks = numeric_trunks + carousel_trunk
        
        # Crea la stessa mappatura di scalatura usata per MAIN
        conf_trunk_number_mapping = {}
        for trunk_key in sorted_trunks:
            if trunk_key == "Carousel":
                conf_trunk_number_mapping[trunk_key] = "Carousel"
            elif isinstance(trunk_key, int):
                if carousel_trunk_position is not None and trunk_key > carousel_trunk_position:
                    # Scala di 1 i tronchi dopo il Carousel
                    conf_trunk_number_mapping[trunk_key] = trunk_key - 1
                else:
                    # Mantieni il numero originale per i tronchi prima del Carousel
                    conf_trunk_number_mapping[trunk_key] = trunk_key
        
        for trunk_key in sorted_trunks:
            trunk_num_for_file = conf_trunk_number_mapping[trunk_key]
            output_filename = f'CONF_T{trunk_num_for_file}.scl'
            output_path = os.path.join('Configurazioni', selected_cab_plc, f'API0{selected_cab_plc[-2:]}', output_filename)
            
            try:
                if not os.path.exists(os.path.join('Configurazioni', selected_cab_plc, f'API0{selected_cab_plc[-2:]}')):
                    os.makedirs(os.path.join('Configurazioni', selected_cab_plc, f'API0{selected_cab_plc[-2:]}'))
                with open(output_path, 'w') as f:
                    f.write("\n".join(configurations_by_trunk[trunk_key]))
                files_created.append(output_filename)
            except Exception as e:
                # messagebox.showerror("Errore", f"Errore nel salvataggio del file {output_filename}: {e}")
                print(f"Errore nel salvataggio del file {output_filename}: {e}")
                if QApplication.instance():
                     QMessageBox.critical(None, "Errore Salvataggio", f"Errore nel salvataggio del file {output_filename}:\n{e}")
                continue
        
        # Crea i file LINEA per ogni prefisso selezionato e raccogli mappa prefisso->linee
        print(f"DEBUG - ordered_prefixes passato a create_linea_files: {ordered_prefixes}")
        print(f"DEBUG - df shape prima di create_linea_files: {df.shape}, colonne: {df.columns.tolist()}")
        # Verifica che df abbia tutti gli item necessari per il CAB_PLC
        cab_plc_check = df[df['CAB_PLC'] == selected_cab_plc]
        print(f"DEBUG - Items nel df per CAB_PLC {selected_cab_plc}: {len(cab_plc_check)}")
        prefix_to_line_numbers = create_linea_files(df, selected_cab_plc, line_type_mapping, ordered_prefixes)
        print(f"DEBUG - prefix_to_line_numbers restituito: {prefix_to_line_numbers}")
        print(f"DEBUG - line_type_mapping finale: {line_type_mapping}")
        
        # Gestione dei file MAIN
        api_folder = f'API0{selected_cab_plc[-2:]}'
        main_output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        conf_output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        utenze_output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        db_trunk_output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        
        # Ottieni la sequenza ordinata dei numeri di tronco che hanno dati MAIN validi
        # Gestisci sia numeri che "Carousel" nell'ordinamento
        trunk_keys = main_data_by_trunk.keys()
        numeric_trunks = sorted([k for k in trunk_keys if isinstance(k, int)])
        carousel_trunk = [k for k in trunk_keys if isinstance(k, str) and k == "Carousel"]
        ordered_trunk_nums = numeric_trunks + carousel_trunk
        
        # Crea una mappatura per scalare i numeri dopo il Carousel
        # Se carousel_trunk_position = 14, allora:
        # - Tronchi 1-13: rimangono 1-13
        # - Tronco 14: diventa "Carousel"
        # - Tronco 15: diventa 14
        # - Tronco 16: diventa 15
        trunk_number_mapping = {}
        for trunk_key in ordered_trunk_nums:
            if trunk_key == "Carousel":
                trunk_number_mapping[trunk_key] = "Carousel"
            elif isinstance(trunk_key, int):
                if carousel_trunk_position is not None and trunk_key > carousel_trunk_position:
                    # Scala di 1 i tronchi dopo il Carousel
                    trunk_number_mapping[trunk_key] = trunk_key - 1
                else:
                    # Mantieni il numero originale per i tronchi prima del Carousel
                    trunk_number_mapping[trunk_key] = trunk_key
        
        for idx, trunk_key in enumerate(ordered_trunk_nums):
            items_ordered = main_data_by_trunk[trunk_key]
            
            # Usa il numero scalato per creare i file
            trunk_num_for_file = trunk_number_mapping[trunk_key]
            
            # Trova ultimo elemento VALIDO del tronco precedente (skippa Datalogic etc.)
            last_valid_prev_item_data = None
            if idx > 0:
                prev_trunk_key = ordered_trunk_nums[idx - 1]
                prev_trunk_items = main_data_by_trunk.get(prev_trunk_key, [])
                # Cerca all'indietro l'ultimo item valido per la catena
                for item_data in reversed(prev_trunk_items):
                    if _is_valid_component_for_chain(item_data):
                        # Verifica se appartiene alla stessa linea del trunk corrente
                        prev_item_trunk_id = item_data.get('ITEM_TRUNK')
                        current_trunk_id = None
                        if items_ordered:
                            current_trunk_id = items_ordered[0].get('ITEM_TRUNK')
                        
                        # Se la linea è diversa, imposta a None
                        if prev_item_trunk_id and current_trunk_id:
                            prev_line = trunk_to_line_mapping.get(prev_item_trunk_id)
                            current_line = trunk_to_line_mapping.get(current_trunk_id)
                            if prev_line != current_line:
                                last_valid_prev_item_data = None
                                break
                        
                        last_valid_prev_item_data = item_data
                        break # Trovato l'ultimo valido

            # Trova primo elemento VALIDO del tronco successivo (skippa Datalogic etc.)
            first_valid_next_item_data = None
            if idx < len(ordered_trunk_nums) - 1:
                next_trunk_key = ordered_trunk_nums[idx + 1]
                next_trunk_items = main_data_by_trunk.get(next_trunk_key, [])
                # Cerca in avanti il primo item valido per la catena
                for item_data in next_trunk_items:
                     if _is_valid_component_for_chain(item_data):
                        # Verifica se appartiene alla stessa linea del trunk corrente
                        next_item_trunk_id = item_data.get('ITEM_TRUNK')
                        current_trunk_id = None
                        if items_ordered:
                            current_trunk_id = items_ordered[0].get('ITEM_TRUNK')
                        
                        # Se la linea è diversa, imposta a None
                        if next_item_trunk_id and current_trunk_id:
                            next_line = trunk_to_line_mapping.get(next_item_trunk_id)
                            current_line = trunk_to_line_mapping.get(current_trunk_id)
                            if next_line != current_line:
                                first_valid_next_item_data = None
                                break
                        
                        first_valid_next_item_data = item_data
                        break # Trovato il primo valido

            # Chiama create_main_file con contesto corretto
            if items_ordered:
                try:
                    create_main_file(
                        trunk_num_for_file, 
                        items_ordered, 
                        main_output_folder,
                        last_valid_prev_item_data=last_valid_prev_item_data,
                        first_valid_next_item_data=first_valid_next_item_data,
                        trunk_to_line_mapping=trunk_to_line_mapping
                    )
                    
                    # Crea i file correlati
                    create_trunk_file(trunk_num_for_file, db_trunk_output_folder)
                except Exception as e:
                    print(f"Errore durante la creazione dei file per il tronco {trunk_num_for_file}: {e}")
                    continue

        # Crea il file CONF.scl nella cartella API0## dopo che tutti i trunk sono stati processati
        conf_output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        os.makedirs(conf_output_folder, exist_ok=True)  # Crea la cartella se non esiste
        create_conf_file(selected_cab_plc, df, conf_output_folder, order, prefix_to_line_numbers, carousel_trunk_position)

        # Usa ordered_prefixes già creato all'inizio (dal parametro order)
        num_lines = len(ordered_prefixes)

        # Calcola il numero di tronchi per ogni linea
        trunks_per_line = []
        for prefix in ordered_prefixes:
            prefix_data = cab_plc_data[cab_plc_data['ITEM_ID_CUSTOM'].str.lower().str.startswith(prefix)]
            unique_trunks = prefix_data['ITEM_TRUNK'].nunique()
            trunks_per_line.append(unique_trunks)

        print(f"DEBUG - Numero di linee: {num_lines}")
        print(f"DEBUG - Tronchi per linea: {trunks_per_line}")
        print(f"DEBUG - Totale MAIN da generare: {sum(trunks_per_line)}")
        print(f"DEBUG - Prefissi ordinati: {ordered_prefixes}")

        create_main_structure_file(main_output_folder, num_lines, selected_cab_plc, trunks_per_line, ordered_prefixes, carousel_trunk_position)

        # Popola trunk_to_line_mapping usando la mappa prefisso->linee creata sopra
        # Associa ogni tronco alla linea corretta (normale o carousel) per il proprio prefisso
        # Prima identifica quali trunk contengono carousel e mappa ogni trunk al suo prefisso
        trunks_with_carousel = set()
        trunk_prefix_map = {}  # Mappa trunk_id -> prefix
        
        # Usa df invece di cab_plc_data per essere sicuri di avere tutti i dati
        for _, row in df.iterrows():
            trunk_id = row['ITEM_TRUNK']
            item_id_custom = str(row['ITEM_ID_CUSTOM'])
            prefix = item_id_custom[:4].lower()
            # Usa il primo prefisso trovato per questo trunk (dovrebbero essere tutti uguali)
            if trunk_id not in trunk_prefix_map:
                trunk_prefix_map[trunk_id] = prefix
            
            if count_ca_occurrences(item_id_custom) == 2:
                trunks_with_carousel.add(trunk_id)
        
        # Ora associa ogni trunk alla linea corretta
        # IMPORTANTE: I trunk con carousel vanno sempre alla linea Carousel (separata, non associata al prefisso)
        # I trunk senza carousel vanno alla linea normale del prefisso
        for trunk_id, prefix in trunk_prefix_map.items():
            if trunk_id in trunks_with_carousel:
                # Il carosello ha sempre una linea separata, indipendente dal prefisso
                trunk_to_line_mapping[trunk_id] = 'Carousel'
                print(f"DEBUG - Trunk {trunk_id} (prefisso {prefix}) -> LINE Carousel (carousel - linea separata)")
            else:
                line_nums = prefix_to_line_numbers.get(prefix)
                if not line_nums:
                    print(f"DEBUG - ATTENZIONE: Prefisso {prefix} non trovato in prefix_to_line_numbers per trunk {trunk_id}")
                    print(f"DEBUG - prefix_to_line_numbers disponibili: {list(prefix_to_line_numbers.keys())}")
                    continue
                trunk_to_line_mapping[trunk_id] = line_nums['normal']
                print(f"DEBUG - Trunk {trunk_id} (prefisso {prefix}) -> LINE {line_nums['normal']} (normale)")
        
        print(f"DEBUG - trunk_to_line_mapping finale: {trunk_to_line_mapping}")
        print(f"DEBUG - trunks_with_carousel: {trunks_with_carousel}")
        print(f"DEBUG - trunk_prefix_map: {trunk_prefix_map}")

        # Genera il file GEN_LINE.scl dopo che tutte le linee e i trunk sono stati processati
        generate_gen_line_file(df, selected_cab_plc, line_type_mapping, ordered_prefixes, trunk_to_line_mapping, carousel_trunk_position)

        # Crea il file DigIn.scl nella cartella API0##
        print(f"DEBUG - carousel_data_for_dig_in prima di create_dig_in_file: {len(carousel_data_for_dig_in) if carousel_data_for_dig_in else 0} elementi")
        if carousel_data_for_dig_in:
            for idx, car_data in enumerate(carousel_data_for_dig_in):
                print(f"DEBUG - carousel_data_for_dig_in[{idx}]: carousel_id={car_data.get('carousel_id')}, motors={len(car_data.get('motors', []))}")
        create_dig_in_file(selected_cab_plc, 'Configurazioni', conveyor_data_for_dig_in, carousel_data_for_dig_in, ordered_prefixes, trunk_to_line_mapping, prefix_to_line_numbers, carousel_trunk_position)

        # Aggiorna lo stato
        # status_var.set(f"Completato! {len(files_created)} file CONF_T e {len(main_data_by_trunk)} file MAIN salvati.")
        completion_message = f"Completato! {len(files_created)} file CONF_T e {len(main_data_by_trunk)} file MAIN salvati."
        print(f"process_excel: {completion_message}")

        # LOG_ENABLE generation removed as per requirements
        
        # Genera il file Zones_Input.scl
        print("DEBUG - Generazione file Zones_Input.scl...")
        try:
            generate_zones_input_scl(selected_cab_plc)
        except Exception as e:
            print(f"ERRORE durante la generazione del file Zones_Input.scl: {e}")
            # Non bloccare il processo se la generazione delle zone fallisce
        
        # Genera il file PCE_Input.scl
        print("DEBUG - Generazione file PCE_Input.scl...")
        try:
            generate_pce_input_scl(selected_cab_plc)
        except Exception as e:
            print(f"ERRORE durante la generazione del file PCE_Input.scl: {e}")
            # Non bloccare il processo se la generazione del PCE fallisce

        # Genera DigOut.scl
        print("DEBUG - Generazione file DigOut.scl...")
        try:
            create_dig_out_file(selected_cab_plc, 'Configurazioni', ordered_prefixes, trunk_to_line_mapping, carousel_trunk_position, df, conveyor_data_for_dig_in)
        except Exception as e:
            print(f"ERRORE durante la generazione del file DigOut.scl: {e}")

        # Genera PCE_Output.scl
        print("DEBUG - Generazione file PCE_Output.scl...")
        try:
            generate_pce_output_scl(selected_cab_plc)
        except Exception as e:
            print(f"ERRORE durante la generazione del file PCE_Output.scl: {e}")
        
        # Genera file logger config per API004
        if selected_cab_plc == 'API004':
            print("DEBUG - Generazione file logger config...")
            try:
                from creazione_file import generate_logger_config_files, generate_puls_line_scl, generate_additional_db_files
                generate_logger_config_files(selected_cab_plc)
                generate_puls_line_scl(selected_cab_plc)
                generate_additional_db_files(selected_cab_plc)
            except Exception as e:
                print(f"ERRORE durante la generazione dei file aggiuntivi: {e}")
        
        # Esegui test di confronto automatico per API004
        if selected_cab_plc == 'API004':
            try:
                from test_comparison import run_comparison_test
                run_comparison_test(selected_cab_plc)
            except Exception as e:
                print(f"ERRORE durante il test di confronto: {e}")
        
        return True, completion_message

        
    except Exception as e:
        # messagebox.showerror("Errore", f"Errore nell'elaborazione del file Excel: {e}")
        print(f"Errore nell'elaborazione del file Excel: {e}")
        import traceback
        traceback.print_exc()
        # status_var.set("Errore nell'elaborazione")
        return False, f"Errore nell'elaborazione del file Excel: {str(e)}"


def create_logger_configuration_file(file_path):
    """Genera il file 'LoggerConfiguration.scl' con il contenuto SCL predefinito.
    
    Viene richiamato automaticamente ogni volta che viene generato il file LOG_ENABLE[FC10].scl.
    """
    logger_configuration_content = """FUNCTION "LoggerConfiguration" : Void
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      JumpStaticLogActivation : Bool;
   END_VAR

   VAR_IN_OUT 
      ConnectionLog {InstructionName := 'TCON_IP_v4'; LibVersion := '1.0'} : TCON_IP_v4;   //   Configurazione del canale di comunicazione
      "Ist-LogBuffer" : "GstLogBuffer";
      EnabledMessages : Array[0..32767] of Bool;   //   Array di configurazione messaggi abilitati
   END_VAR


BEGIN
	REGION NETWORK 1 - Logger channel configuration
	    
	    // Log connection
	    #ConnectionLog.InterfaceId := "Local~PROFINET_interface_1";//"Local~PROFINET_interface_GBIT_3";
	    #ConnectionLog.ID := 8;
	    #ConnectionLog.ActiveEstablished := TRUE;
	    #ConnectionLog.ConnectionType := 16#0B;
	    #ConnectionLog.RemoteAddress.ADDR[1] := 10;//172;
	    #ConnectionLog.RemoteAddress.ADDR[2] :=0;// 20;
	    #ConnectionLog.RemoteAddress.ADDR[3] := 8;// 198;
	    #ConnectionLog.RemoteAddress.ADDR[4] := 133;//28;
	    #ConnectionLog.RemotePort := 7000;
	    #ConnectionLog.LocalPort := 0;
	    
	    // LogBuffer configuration
	    #"Ist-LogBuffer".Cfg.BufferClosingTime := T#500ms;
	    #"Ist-LogBuffer".Cfg.LifeMsgTime := T#5s;
	    #"Ist-LogBuffer".Cfg.SourceNode := 8;
	    
	END_REGION
	
	REGION Enable log messages
	    
	    IF NOT #JumpStaticLogActivation THEN
	        // Always active logs
	        // #EnabledMessages["IDLOG_GTW_CHRTX_SORT_RESULT"] := TRUE;
	        // #EnabledMessages["IDLOG_GTW_CHMTX_SORT_REQUEST"] := TRUE;
	        // #EnabledMessages["IDLOG_GTW_CHMTX_SUBSYSTEM_STS"] := TRUE;
	        // #EnabledMessages["IDLOG_TRK_LogBrokenObject"] := TRUE; //102
	        #EnabledMessages["IDLOG_TRK_LogPhotocellTrk"] := TRUE;//101
	        // #EnabledMessages["IDLOG_TRK_LogMsgGapMonitor"] := TRUE;//104
	    END_IF;
	    
	END_REGION
END_FUNCTION"""
    
    with open(file_path, "w") as f:
        f.write(logger_configuration_content)
    print(f"File {file_path} generato con successo.")
