"""
Questo modulo contiene la funzione principale di elaborazione che gestisce la generazione
delle configurazioni per i nastri trasportatori. Include la logica per l'elaborazione dei dati
e la creazione dei file di configurazione.
"""

import os
import pandas as pd
from tkinter import messagebox, ttk
import tkinter as tk
from funzioni_elaborazione import (
    get_last_three_digits,
    count_ca_occurrences,
    get_value_or_default,
    extract_numeric_part
)
from creazione_file import (
    create_txt_files,
    create_data_block_file,
    create_datalogic_file,
    create_linea_files,
    create_main_file,
    create_conft_t_file,
    create_utenza_file,
    create_trunk_file
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
    """
    status_var.set("Elaborazione in corso...")
    
    # Verifica se il file Excel è stato selezionato
    if not excel_file_path:
        messagebox.showerror("Errore", "Nessun file Excel selezionato. Seleziona un file Excel prima di procedere.")
        status_var.set("Errore: nessun file selezionato")
        return
    
    if not os.path.exists(excel_file_path):
        messagebox.showerror("Errore", f"Il file {excel_file_path} non esiste.")
        status_var.set("Errore: file non trovato")
        return
    
    try:
        # Carica il file Excel
        df = pd.read_excel(excel_file_path)
        
        # Verifica le colonne richieste
        required_columns = ['ITEM_ID_CUSTOM', 'CAB_PLC', 'ITEM_TRUNK', 'ITEM_SPEED_TRANSPORT', 
                          'ITEM_SPEED_LAUNCH', 'ITEM_SPEED_MAX', 'ITEM_ACCELERATION', 'ITEM_L']
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror("Errore", "Alcune colonne richieste sono mancanti nel file Excel.")
            status_var.set("Errore: colonne mancanti")
            return
        
        # Filtra le righe escludendo ITEM_ID_CUSTOM contenenti "OG", "SD", "FD", "RS", "CX", "CN", "CH", "XR", "SO", "LC", "IN"
        df = df[~df['ITEM_ID_CUSTOM'].str.contains('OG|SD|FD|RS|CX|CN|CH|XR|SO|LC|IN', case=False, na=False)]

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
            messagebox.showerror("Errore", f"Nessun dato trovato per il CAB_PLC {selected_cab_plc} nel file Excel.")
            status_var.set(f"Errore: nessun dato per {selected_cab_plc}")
            return
        
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
        
        # Contatori per numeri UTENZA e CAROUSEL unici
        global_utenza_counter = 1
        global_carousel_counter = 1
        
        # Crea un dizionario per mappare i prefissi all'ordine di selezione
        prefix_order = {}
        if order:
            for i, item in enumerate(order):
                prefix = item.split('. ')[1] if '. ' in item else item
                prefix_order[prefix[:4].lower()] = i
        
        # Ordina i prefissi in base all'ordine di selezione
        ordered_prefixes = sorted(df['Prefix'].unique(), 
                                key=lambda x: prefix_order.get(x, 999))
        
        # Per ogni prefisso nell'ordine selezionato
        for prefix in ordered_prefixes:
            prefix_data = df[df['Prefix'] == prefix].copy()
            
            # Ordina il gruppo per le ultime tre cifre
            prefix_data = prefix_data.sort_values(by='LastThreeDigits')
            
            # Assegna numeri UTENZA e CAROUSEL
            for index, row in prefix_data.iterrows():
                item_id = str(row['ITEM_ID_CUSTOM'])
                
                if count_ca_occurrences(item_id) == 2:
                    df.at[index, 'GlobalCarouselNumber'] = global_carousel_counter
                    global_carousel_counter += 1
                    df.at[index, 'GlobalUtenzaNumber'] = None
                elif "ST" in item_id.upper():
                    df.at[index, 'GlobalUtenzaNumber'] = global_utenza_counter
                    global_utenza_counter += 1
                    df.at[index, 'GlobalCarouselNumber'] = None
                else:
                    df.at[index, 'GlobalUtenzaNumber'] = None
                    df.at[index, 'GlobalCarouselNumber'] = None
        
        # Contatore globale per la numerazione progressiva dei file CONFT
        global_trunk_counter = 1
        
        # Dizionario per memorizzare le configurazioni per numero di tronco
        configurations_by_trunk = {}
        # --- NUOVO: Dizionario per memorizzare i dati per i file MAIN ---
        main_data_by_trunk = {} 
        # --- FINE NUOVO ---
        
        # Itera attraverso ogni prefisso nell'ordine selezionato
        for prefix in ordered_prefixes:
            prefix_data = df[df['Prefix'] == prefix]
            trunk_groups = prefix_data.groupby('ITEM_TRUNK')
            
            for trunk_name, trunk_group in trunk_groups:
                configurations_by_trunk[global_trunk_counter] = [] 
                # Aggiunge l'intestazione della funzione
                header = f"""FUNCTION "CONF_T{global_trunk_counter}" : Void
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
BEGIN
"""
                configurations_by_trunk[global_trunk_counter].append(header)
                
                # Calcola il numero progressivo all'interno del gruppo
                progressive_number = 1
                
                # Ordina il gruppo per le ultime tre cifre di item_id_custom
                trunk_group = trunk_group.sort_values(by='LastThreeDigits')
                
                # Itera attraverso ogni riga del gruppo
                for index, row in trunk_group.iterrows():
                    print(f"DEBUG: Inizio iterazione {index}") # DEBUG PRINT 1
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
                    
                    # --- NUOVA MODIFICA: Assicura che NaN diventi None ---
                    if pd.isna(utenza_number):
                        utenza_number = None
                    if pd.isna(carousel_number):
                        carousel_number = None
                    # --- FINE NUOVA MODIFICA ---
                    
                    comment_name = item_id_custom
                    
                    # Determina il nuovo ID custom basato sul tipo e numero
                    if count_ca_occurrences(comment_name) == 2 and carousel_number is not None:
                        # Assicurati che carousel_number sia un intero prima di usarlo nella f-string
                        try:
                            # Usa il numero di carousel direttamente, senza altre manipolazioni
                            item_id_custom_new = f"CAROUSEL{int(carousel_number)}"
                        except (ValueError, TypeError):
                            # Gestisci il caso in cui carousel_number non sia convertibile in int
                            print(f"Attenzione: Impossibile convertire GlobalCarouselNumber '{carousel_number}' in intero per ITEM_ID_CUSTOM '{item_id_custom}'. Uso l'ID originale.")
                            item_id_custom_new = item_id_custom
                    elif "ST" in item_id_custom.upper() and utenza_number is not None:
                         # Assicurati che utenza_number sia un intero prima di usarlo nella f-string
                        try:
                            item_id_custom_new = f"UTENZA{int(utenza_number)}"
                        except (ValueError, TypeError):
                             # Gestisci il caso in cui utenza_number non sia convertibile in int
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
                    
                    component_type = "Carousel" if count_ca_occurrences(comment_name) == 2 else "Conveyor"
                    
                    # Costruisci la stringa di configurazione - Parte 1 (regione comune)
                    configuration = f"""   REGION {comment_name}

"""
                    # Costruisci la stringa di configurazione - Parte 2 (specifica per "SC")
                    if "SC" in item_id_custom:
                        configuration += f"""    REGION Config ATR CAMERA 360 ({item_id_custom})
        REGION General data configuration
            "Datalogic_{item_id_custom}".Data.CNF.Position := 0.5;
            "Datalogic_{item_id_custom}".Data.CNF.MachineId := 21;
            "Datalogic_{item_id_custom}".Data.CNF.SeqScanner := 7160;
            "Datalogic_{item_id_custom}".Data.CNF.DbObjNum := 2011;
            
            REGION PROFINET interface connection
                
                REGION Address Configuration
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.InputHwId := "{item_id_custom}_CD014~IM_128ByteIn_1";
                    "Datalogic_{item_id_custom}"."Sub-DatalogicComProfinet_Instance".DATA.CNF.OutputHwId := "{item_id_custom}_CD014~OM_32ByteOut_1";
                    
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
                    # Costruisci la stringa di configurazione - Parte 3 (specifica per "ST" o "CA")
                    # Nota: Ho aggiunto un controllo try-except per la conversione a float di item_l
                    try:
                        item_l_float = float(item_l) / 1000.0
                    except (ValueError, TypeError):
                        print(f"Attenzione: Impossibile convertire ITEM_L '{item_l}' in float per ITEM_ID_CUSTOM '{item_id_custom}'. Uso il valore di default {default_item_l/1000.0}.")
                        item_l_float = default_item_l / 1000.0
                        
                    if "ST" in item_id_custom.upper() or count_ca_occurrences(comment_name) == 2:
                        configuration += f"""    REGION {component_type}.Data.CNF

        "{item_id_custom_new}".{component_type}.Data.CNF.Pht01En := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.Pht02En := TRUE;
        "{item_id_custom_new}".{component_type}.Data.CNF.SlowdownOnAsrEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.LinkedToNext := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.AdjToSpeedNext := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.ExtDeltaEncoderEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.HmiControlEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.AntiShadowingEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.StrictGapEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.StopForAdjacentJamEn := FALSE;
        "{item_id_custom_new}".{component_type}.Data.CNF.DbObjectsNumber := 2011;
        "{item_id_custom_new}".{component_type}.Data.CNF.DecisionPointId := 0;
        "{item_id_custom_new}".{component_type}.Data.CNF.UseTrunkNumber := {progressive_number};
        "{item_id_custom_new}".{component_type}.Data.CNF.TimeEnergySaving := T#30S;
        "{item_id_custom_new}".{component_type}.Data.CNF.TimeAccelerationHighSpeed := T#0S;
        "{item_id_custom_new}".{component_type}.Data.CNF.Speed1 := {item_speed_transport};
        "{item_id_custom_new}".{component_type}.Data.CNF.Speed2 := {item_speed_launch};
        "{item_id_custom_new}".{component_type}.Data.CNF.SpeedLow := 0.0;
        "{item_id_custom_new}".{component_type}.Data.CNF.SpeedHigh := 0.0;
        "{item_id_custom_new}".{component_type}.Data.CNF.DriveMaxSpeed := {item_speed_max};
        "{item_id_custom_new}".{component_type}.Data.CNF.Acceleration := {item_acceleration};
        "{item_id_custom_new}".{component_type}.Data.CNF.Length := {item_l_float}; # Usato valore convertito e controllato
        "{item_id_custom_new}".{component_type}.Data.CNF.Gap := 0.4;
        "{item_id_custom_new}".{component_type}.Data.CNF.Step := 0.4;
        "{item_id_custom_new}".{component_type}.Data.CNF.TrackingSlotLength := 0.04;
        "{item_id_custom_new}".{component_type}.Data.CNF.StopDistance := 0.6;
        "{item_id_custom_new}".{component_type}.Data.CNF.EndZone := 0.6;
        "{item_id_custom_new}".{component_type}.Data.CNF.ObjectMaxLength := 0.0;
        "{item_id_custom_new}".{component_type}.Data.CNF.JamInterferenceDistance := 0.0;
    END_REGION
    
     REGION {component_type}.Pht01.Data.CNF
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.FlickeringMaxFp := 5;
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.FlickeringTime := T#500MS;
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.PhtRiseFilterThr := 0.04;
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.PhtFallFilterThr := 0.04;
            "{item_id_custom_new}".{component_type}.Pht01.Data.CNF.JamLengthThr := 3;
        END_REGION
        
        REGION {component_type}.Pht02.Data.CNF
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.FlickeringMaxFp := 5;
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.FlickeringTime := T#500MS;
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.PhtRiseFilterThr := 0.04;
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.PhtFallFilterThr := 0.04;
            "{item_id_custom_new}".{component_type}.Pht02.Data.CNF.JamLengthThr := 3;
        END_REGION
        
        REGION {component_type}.PhtTracking01.Data.CNF
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.VidGenerationEn := TRUE;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.ObjLengthUpdateDis := FALSE;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.MachineId := "UpstreamDB-Globale".Global_Data.MachineId;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.DecisionPointId := 0;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.MaxLostPiecesForJam := 3;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.Position := 0.4;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.TrkCtrlTollerance := 0.35;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.ObjLengthTollerance := 0;
            "{item_id_custom_new}".{component_type}.PhtTracking01.Data.CNF.TrackingPointID := dint#50102301;
        END_REGION
        
        REGION {component_type}.PhtTracking02.Data.CNF
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.VidGenerationEn := TRUE;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.ObjLengthUpdateDis := FALSE;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.MachineId := "UpstreamDB-Globale".Global_Data.MachineId;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.DecisionPointId := 0;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.MaxLostPiecesForJam := 3;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.Position := 7.05;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.TrkCtrlTollerance := 0.35;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.ObjLengthTollerance := 0;
            "{item_id_custom_new}".{component_type}.PhtTracking02.Data.CNF.TrackingPointID := dint#50102301;
        END_REGION
        
        REGION Encoder.Data.CNF
            "{item_id_custom_new}".Encoder.Data.CNF.K_pulse := 0.0;
            "{item_id_custom_new}".Encoder.Data.CNF.SpeedTollerance := 0.0;
        END_REGION
        
        REGION DriveInterface.Par
            "{item_id_custom_new}".DriveInterface.Par.Direction := FALSE;
            "{item_id_custom_new}".DriveInterface.Par.UseDriveSpeedYs := TRUE;
            "{item_id_custom_new}".DriveInterface.Par.HwAddr := 0;
            "{item_id_custom_new}".DriveInterface.Par.MaxSpeed := 2.0;
            "{item_id_custom_new}".DriveInterface.Par.FeedbackTime := T#500MS;
        END_REGION
        
        REGION PhonicWeel.Data.CNF
            "{item_id_custom_new}".PhonicWeel.Data.CNF.PhonicWheelEn := FALSE;
            "{item_id_custom_new}".PhonicWeel.Data.CNF.FlickeringMaxFp := 0;
            "{item_id_custom_new}".PhonicWeel.Data.CNF.FlickeringTime := T#500MS;
            "{item_id_custom_new}".PhonicWeel.Data.CNF.PhtRiseFilterThr := T#100MS;
            "{item_id_custom_new}".PhonicWeel.Data.CNF.PhtFallFilterThr := T#100MS;
            "{item_id_custom_new}".PhonicWeel.Data.CNF.JamTimeThr := T#1S;
        END_REGION
END_REGION
"""
                    # Aggiungi la configurazione e crea i file necessari
                    if "SC" in item_id_custom:
                        output_folder = f'Configurazioni/{selected_cab_plc}/UTENZE'
                        print(f"DEBUG: Creazione file datalogic per {item_id_custom} in {output_folder}") # DEBUG PRINT 2
                        create_datalogic_file(item_id_custom, output_folder)
                        configurations_by_trunk[global_trunk_counter].append(configuration)
                    else:
                        output_folder = f'Configurazioni/{selected_cab_plc}/UTENZE'
                        create_data_block_file(item_id_custom_new, component_type, output_folder)
                        configurations_by_trunk[global_trunk_counter].append(configuration)
                    
                    # Incrementa il numero progressivo all'interno del gruppo
                    progressive_number += 1
                
                # Aggiunge END_FUNCTION alla fine delle configurazioni del tronco
                configurations_by_trunk[global_trunk_counter].append("END_FUNCTION")
                
                # --- MODIFICA: Filtra e Memorizza dati per MAIN --- 
                # Filtra per includere SOLO 'ST' o 'CAx2', come in CONF_T
                condition_st = trunk_group['ITEM_ID_CUSTOM'].str.contains('ST', case=False, na=False)
                # Applica la funzione count_ca_occurrences a ogni riga
                condition_ca2 = trunk_group['ITEM_ID_CUSTOM'].apply(lambda x: count_ca_occurrences(str(x)) == 2)
                
                valid_items_for_main = trunk_group[condition_st | condition_ca2] # Includi se ST OR CAx2

                if not valid_items_for_main.empty: # Solo se ci sono item validi nel tronco
                    items_ordered_dict = valid_items_for_main.sort_values(by='LastThreeDigits').to_dict('records') 
                    main_data_by_trunk[global_trunk_counter] = items_ordered_dict
                # else: # Opzionale: se vuoi che un tronco esista in main_data anche se vuoto dopo il filtro
                #     main_data_by_trunk[global_trunk_counter] = []
                # --- FINE MODIFICA ---

                # Incrementa il contatore globale
                global_trunk_counter += 1
        
        # Salva le configurazioni CONF_T in file separati per tronco
        files_created = [] 
        for trunk in sorted(configurations_by_trunk.keys(), key=int): # Ri-aggiunto loop salvataggio CONF_T
            output_filename = f'CONF_T{trunk}.scl'
            output_path = os.path.join('Configurazioni', selected_cab_plc, 'CONF', output_filename)
            
            try:
                if not os.path.exists(os.path.join('Configurazioni', selected_cab_plc, 'CONF')):
                    os.makedirs(os.path.join('Configurazioni', selected_cab_plc, 'CONF'))
                with open(output_path, 'w') as f:
                    f.write("\n".join(configurations_by_trunk[trunk]))
                files_created.append(output_filename)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio del file {output_filename}: {e}")

        # Crea i file LINEA
        create_linea_files(df, selected_cab_plc)
        
        # --- SOSTITUITO BLOCCO MAINx con Logica di Contesto ---
        main_output_folder = os.path.join('Configurazioni', selected_cab_plc, 'MAIN')
        conf_output_folder = os.path.join('Configurazioni', selected_cab_plc, 'CONF')
        utenze_output_folder = os.path.join('Configurazioni', selected_cab_plc, 'UTENZE')
        db_trunk_output_folder = os.path.join('Configurazioni', selected_cab_plc, 'DB_TRUNK')
        
        # Ottieni la sequenza ordinata dei numeri di tronco che hanno dati MAIN validi
        ordered_trunk_nums = sorted(main_data_by_trunk.keys())
        
        for idx, trunk_num in enumerate(ordered_trunk_nums):
            items_ordered = main_data_by_trunk[trunk_num] # Lista già filtrata e ordinata
            
            # Trova ultimo elemento valido del tronco precedente
            last_valid_prev_item_data = None
            if idx > 0:
                prev_trunk_num = ordered_trunk_nums[idx - 1]
                if main_data_by_trunk[prev_trunk_num]: # Assicurati che il tronco precedente non sia vuoto
                    last_valid_prev_item_data = main_data_by_trunk[prev_trunk_num][-1]

            # Trova primo elemento valido del tronco successivo
            first_valid_next_item_data = None
            if idx < len(ordered_trunk_nums) - 1:
                next_trunk_num = ordered_trunk_nums[idx + 1]
                if main_data_by_trunk[next_trunk_num]: # Assicurati che il tronco successivo non sia vuoto
                    first_valid_next_item_data = main_data_by_trunk[next_trunk_num][0]

            # Chiama create_main_file con contesto
            if items_ordered: # Solo se ci sono elementi validi in questo tronco
                create_main_file(
                    trunk_num, 
                    items_ordered, 
                    main_output_folder,
                    last_valid_prev_item_data=last_valid_prev_item_data,
                    first_valid_next_item_data=first_valid_next_item_data
                )
                
                # Aggiunte: creazione file CONFT_T e UTENZE
                create_conft_t_file(trunk_num, items_ordered, conf_output_folder)
                create_utenza_file(trunk_num, items_ordered, utenze_output_folder)
                
                # Creazione file TRUNK nella cartella DB_TRUNK
                create_trunk_file(trunk_num, db_trunk_output_folder)
        # --- FINE SOSTITUZIONE ---

        # Aggiorna lo stato
        status_var.set(f"Completato! {len(files_created)} file CONF_T e {len(main_data_by_trunk)} file MAIN salvati.")

        # Mostra il messaggio di completamento
        show_completion_message(root, selected_cab_plc)
        
        # Crea il file LOG_ENABLE[FC10].txt
        log_enable_path = os.path.join('Configurazioni', selected_cab_plc, 'LOG_ENABLE[FC10].txt')
        os.makedirs(os.path.dirname(log_enable_path), exist_ok=True)
        
        # Estrai i nomi effettivi delle utenze e caroselli
        utenze = df[df['ITEM_ID_CUSTOM'].str.contains('ST', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
        caroselli = df[df['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2]['ITEM_ID_CUSTOM'].unique()
        
        print(f"Utenze trovate: {utenze}")
        print(f"Caroselli trovati: {caroselli}")
        print(f"Ordine selezionato: {order}")
        
        # Ordina le utenze e i caroselli secondo l'ordine scelto dall'utente
        ordered_utenze = []
        ordered_caroselli = []
        
        # Estrai i prefissi dall'ordine selezionato
        prefixes = [item.split('. ')[1] for item in order]
        
        # Ordina le utenze e i caroselli in base ai prefissi
        for prefix in prefixes:
            # Filtra le utenze che iniziano con questo prefisso
            prefix_utenze = [u for u in utenze if u.startswith(prefix)]
            ordered_utenze.extend(sorted(prefix_utenze))
            
            # Filtra i caroselli che iniziano con questo prefisso
            prefix_caroselli = [c for c in caroselli if c.startswith(prefix)]
            ordered_caroselli.extend(sorted(prefix_caroselli))
        
        print(f"Utenze ordinate: {ordered_utenze}")
        print(f"Caroselli ordinati: {ordered_caroselli}")
        
        with open(log_enable_path, 'w') as f:
            f.write("REGION Enabling debug\n")
            f.write("    IF #EnableDebug THEN\n")
            f.write("        // va inserito il phtTracking in base alla fotocellula attivata nella CONF\n")
            
            # Scrivi le configurazioni per tutte le utenze nell'ordine scelto
            current_prefix = None
            for i, utenza in enumerate(ordered_utenze, 1):
                prefix = utenza[:4]  # Prendi i primi 4 caratteri come prefisso
                if prefix != current_prefix:
                    if current_prefix is not None:
                        f.write("\n")  # Aggiungi una riga vuota tra gruppi diversi
                    current_prefix = prefix
                f.write(f'        "UTENZA{i}".Conveyor.PhtTracking02.Debug.DebugEn := TRUE;\n')
            
            f.write("\n")  # Aggiungi una riga vuota tra utenze e caroselli
            
            for i, carosello in enumerate(ordered_caroselli, 1):
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Debug.DebugEn := TRUE;    //D.D.\n')
            
            f.write("    ELSE\n")
            
            current_prefix = None
            for i, utenza in enumerate(ordered_utenze, 1):
                prefix = utenza[:4]
                if prefix != current_prefix:
                    if current_prefix is not None:
                        f.write("\n")
                    current_prefix = prefix
                f.write(f'        "UTENZA{i}".Conveyor.PhtTracking02.Debug.DebugEn := FALSE;\n')
            
            f.write("\n")
            
            for i, carosello in enumerate(ordered_caroselli, 1):
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Debug.DebugEn := FALSE;    //D.D.\n')
            f.write("    END_IF;\n")
            f.write("END_REGION\n\n")
            
            f.write("REGION Enabling log\n")
            f.write("    IF #EnableLog THEN\n")
            
            # Raggruppa le utenze per numero
            utenze_by_number = {}
            for i, utenza in enumerate(ordered_utenze, 1):
                number = i
                if number not in utenze_by_number:
                    utenze_by_number[number] = []
                utenze_by_number[number].append(utenza)
            
            # Scrivi le configurazioni raggruppate per numero
            for number, utenze in sorted(utenze_by_number.items()):
                for utenza in utenze:
                    f.write(f'        "UTENZA{number}".Conveyor.PhtTracking02.Data.CNF.HsitoryEventEn := TRUE;\n')
                    f.write(f'        "UTENZA{number}".Conveyor.PhtTracking02.Data.CNF.LogEventEn := TRUE;\n')
                f.write("\n")  # Aggiungi una riga vuota dopo ogni gruppo
            
            # Scrivi le configurazioni per i caroselli
            for i, carosello in enumerate(ordered_caroselli, 1):
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Data.CNF.HsitoryEventEn := TRUE;\n')
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Data.CNF.LogEventEn := TRUE;\n')
            
            f.write("    ELSE\n")
            
            # Raggruppa le utenze per numero (per la parte ELSE)
            for number, utenze in sorted(utenze_by_number.items()):
                for utenza in utenze:
                    f.write(f'        "UTENZA{number}".Conveyor.PhtTracking02.Data.CNF.HsitoryEventEn := FALSE;\n')
                    f.write(f'        "UTENZA{number}".Conveyor.PhtTracking02.Data.CNF.LogEventEn := FALSE;\n')
                f.write("\n")  # Aggiungi una riga vuota dopo ogni gruppo
            
            # Scrivi le configurazioni per i caroselli (per la parte ELSE)
            for i, carosello in enumerate(ordered_caroselli, 1):
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Data.CNF.HsitoryEventEn := FALSE;\n')
                f.write(f'        "CAROUSEL{i}".Carousel.PhtTracking02.Data.CNF.LogEventEn := FALSE;\n')
            
            f.write("    END_IF;\n")
            f.write("END_REGION")
        
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nell'elaborazione del file Excel: {e}")
        status_var.set("Errore nell'elaborazione")

def show_completion_message(root, selected_cab_plc):
    """
    Mostra una finestra con il messaggio di completamento e i dettagli dei file creati.
    
    Args:
        root: Finestra principale
        selected_cab_plc (str): CAB_PLC selezionato
    """
    # Ottieni la lista delle sottocartelle e dei loro file
    all_subfolders = os.listdir(os.path.join('Configurazioni', selected_cab_plc))
    subfolder_files = {
        subfolder: os.listdir(os.path.join('Configurazioni', selected_cab_plc, subfolder))
        for subfolder in all_subfolders
        if os.path.isdir(os.path.join('Configurazioni', selected_cab_plc, subfolder))
    }
    
    completion_window = tk.Toplevel(root)
    completion_window.title("Operazione Completata")
    completion_window.geometry("800x600")
    completion_window.configure(bg="#2C3E50")
    completion_window.transient(root)
    completion_window.grab_set()
    # Crea un canvas per l'animazione dei coriandoli come ultimo widget
    confetti_canvas = tk.Canvas(completion_window, width=800, height=600, 
                              bg="#2C3E50", highlightthickness=0)


    
    # Applica lo stile moderno
    style = ttk.Style()
    style.configure("Completion.TFrame", background="#2C3E50")
    style.configure("Completion.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 12))
    style.configure("CompletionTitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 16, "bold"))
    style.configure("CompletionSubtitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 14))
    
    # Frame principale
    main_frame = ttk.Frame(completion_window, style="Completion.TFrame")
    main_frame.place(x=20, y=20, width=760, height=560)
    
    # Titolo
    completion_label = ttk.Label(main_frame, 
                               text="Elaborazione completata con successo!", 
                               style="CompletionTitle.TLabel")
    completion_label.pack(pady=(0, 20))
    
    # Sottotitolo
    subtitle_label = ttk.Label(main_frame, 
                             text=f"File generati per {selected_cab_plc}:", 
                             style="CompletionSubtitle.TLabel")
    subtitle_label.pack(anchor="w", pady=(0, 10))
    
    # Frame per le colonne
    columns_frame = ttk.Frame(main_frame, style="Completion.TFrame")
    columns_frame.pack(fill=tk.BOTH, expand=True)
    
    # Calcola il numero di sottocartelle per colonna
    total_subfolders = len(subfolder_files)
    subfolders_per_column = (total_subfolders + 2) // 3  # Arrotonda per eccesso
    
    # Crea tre colonne
    for col in range(3):
        column_frame = ttk.Frame(columns_frame, style="Completion.TFrame")
        column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Calcola gli indici di inizio e fine per questa colonna
        start_idx = col * subfolders_per_column
        end_idx = min((col + 1) * subfolders_per_column, total_subfolders)
        
        # Ottieni le sottocartelle per questa colonna
        subfolders_list = list(subfolder_files.keys())[start_idx:end_idx]
        
        # Aggiungi le sottocartelle e i file alla colonna
        for subfolder in subfolders_list:
            subfolder_label = ttk.Label(column_frame, 
                                      text=subfolder, 
                                      style="Completion.TLabel",
                                      font=("Segoe UI", 12, "bold"))
            subfolder_label.pack(anchor="w", pady=(5, 0))
            
            files_list = "\n".join(f"• {file}" for file in subfolder_files[subfolder])
            files_label = ttk.Label(column_frame, 
                                  text=files_list, 
                                  style="Completion.TLabel",
                                  justify=tk.LEFT)
            files_label.pack(anchor="w", pady=(0, 10))
    
    # Pulsante di chiusura
    close_button = ttk.Button(main_frame, text="Chiudi", 
                             command=completion_window.destroy)
    close_button.pack(pady=20)
    
    # Imposta il focus sulla finestra
    completion_window.focus_set()
    
    # Centra la finestra rispetto alla finestra principale
    completion_window.update_idletasks()
    width = completion_window.winfo_width()
    height = completion_window.winfo_height()
    x = (completion_window.winfo_screenwidth() // 2) - (width // 2)
    y = (completion_window.winfo_screenheight() // 2) - (height // 2)
    completion_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Posiziona il canvas dei coriandoli sopra tutto
    confetti_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Lista per memorizzare i coriandoli
    confetti_pieces = []
    
    # Colori dei coriandoli
    colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F", "#9B59B6", "#1ABC9C"]
    
    # Crea i coriandoli
    for _ in range(100):
        x = random.randint(0, 800)
        y = random.randint(-600, 0)
        color = random.choice(colors)
        size = random.randint(5, 15)
        shape = random.choice(["circle", "rectangle", "triangle"])
        
        if shape == "circle":
            piece = confetti_canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
        elif shape == "rectangle":
            piece = confetti_canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
        else:  # triangle
            points = [x, y+size, x+size, y, x+size, y+size]
            piece = confetti_canvas.create_polygon(points, fill=color, outline="")
        
        # Aggiungi velocità casuale
        dx = random.uniform(-2, 2)
        dy = random.uniform(1, 3)
        rotation = random.uniform(-5, 5)
        
        confetti_pieces.append({
            "id": piece,
            "dx": dx,
            "dy": dy,
            "rotation": rotation,
            "shape": shape,
            "size": size
        })
    
    # Funzione per animare i coriandoli
    def animate_confetti():
        for piece in confetti_pieces[:]:
            try:
                # Ottieni le coordinate attuali
                coords = confetti_canvas.coords(piece["id"])
                if not coords:  # Se l'oggetto non esiste più
                    confetti_pieces.remove(piece)
                    continue
                
                # Aggiorna le coordinate
                new_coords = []
                for i in range(0, len(coords), 2):
                    new_coords.append(coords[i] + piece["dx"])
                    new_coords.append(coords[i+1] + piece["dy"])
                
                # Applica la rotazione se è un triangolo
                if piece["shape"] == "triangle":
                    # Calcola il centro
                    center_x = sum(new_coords[::2]) / 3
                    center_y = sum(new_coords[1::2]) / 3
                    
                    # Ruota i punti
                    rotated_coords = []
                    for i in range(0, len(new_coords), 2):
                        x = new_coords[i] - center_x
                        y = new_coords[i+1] - center_y
                        
                        # Applica la rotazione
                        angle = math.radians(piece["rotation"])
                        rotated_x = x * math.cos(angle) - y * math.sin(angle)
                        rotated_y = x * math.sin(angle) + y * math.cos(angle)
                        
                        rotated_coords.append(rotated_x + center_x)
                        rotated_coords.append(rotated_y + center_y)
                    
                    confetti_canvas.coords(piece["id"], *rotated_coords)
                else:
                    confetti_canvas.coords(piece["id"], *new_coords)
                
                # Aggiungi gravità
                piece["dy"] += 0.1
                
                # Rimuovi i coriandoli che escono dallo schermo
                if coords[1] > 600:
                    confetti_canvas.delete(piece["id"])
                    confetti_pieces.remove(piece)
            except tk.TclError:
                # Se c'è un errore con il canvas (es. finestra chiusa), rimuovi il pezzo
                if piece in confetti_pieces:
                    confetti_pieces.remove(piece)
        
        # Continua l'animazione se ci sono ancora coriandoli e la finestra esiste
        if confetti_pieces and completion_window.winfo_exists():
            completion_window.after(20, animate_confetti)
    
    # Avvia l'animazione
    completion_window.after(100, animate_confetti)

if __name__ == "__main__":
    try:
        # Importa l'interfaccia grafica
        from interfaccia_grafica import create_gui
        
        # Crea e avvia l'interfaccia grafica
        root = create_gui()
        
        # Avvia il loop principale
        root.mainloop()
    except Exception as e:
        print(f"Errore durante l'avvio dell'applicazione: {e}")
        # Mostra un messaggio di errore in caso di problemi
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Nasconde la finestra principale
        messagebox.showerror("Errore di Avvio", f"Si è verificato un errore durante l'avvio dell'applicazione: {e}") 