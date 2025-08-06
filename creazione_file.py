"""
Questo modulo contiene le funzioni per la creazione dei file di configurazione.
Gestisce la generazione dei file .txt e .scl per le configurazioni dei nastri trasportatori.
"""

import os
from funzioni_elaborazione import count_ca_occurrences, get_last_three_digits
import pandas as pd

def create_txt_files(df, selected_cab_plc, order):
    """
    Crea i file .txt per le configurazioni delle linee.
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
        order: Ordine selezionato per la generazione dei file
    """
    # Crea una directory per LINEE all'interno della cartella CAB_PLC selezionata
    linee_folder = f'Configurazioni/{selected_cab_plc}/_DB Line'
    if not os.path.exists(linee_folder):
        os.makedirs(linee_folder)
    
    # Crea una sottocartella "Dettaglio linee" all'interno della cartella LINEE
    detail_folder = os.path.join(linee_folder, 'Dettaglio linee')
    if not os.path.exists(detail_folder):
        os.makedirs(detail_folder)
    
    # Estrai i prefissi unici da ITEM_ID_CUSTOM
    unique_prefixes = sorted(set(item[:4].lower() for item in df['ITEM_ID_CUSTOM']))
    
    # Crea un file .txt per ogni prefisso
    for index, prefix in enumerate(unique_prefixes):
        # Converti il nome del file in maiuscolo
        filename = f"{prefix.upper()}.txt"
        # Salva tutti i file di prefisso nella sottocartella Dettaglio linee
        with open(os.path.join(detail_folder, filename), 'w') as f:
            # Filtra le righe per il prefisso corrente
            prefix_data = df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(prefix)]
            for _, row in prefix_data.iterrows():
                f.write(f"{row['ITEM_ID_CUSTOM']}\n")
    
    # Salva l'ordine selezionato in un file di testo nella sottocartella Dettaglio linee
    with open(os.path.join(detail_folder, 'selected_order.txt'), 'w') as order_file:
        for item in order:
            order_file.write(f"{item}\n")

def create_safety_shutter_file(shutter_number, output_folder):
    """
    Crea un file DATA_BLOCK per un componente SAFETYSHUTTER.
    
    Args:
        shutter_number (int): Numero progressivo dello shutter
        output_folder (str): Cartella di destinazione
    """
    data_block_content = f"""DATA_BLOCK "SAFETYSHUTTER{shutter_number}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"SHUTTER"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"SAFETYSHUTTER{shutter_number}.scl"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)

def create_fire_shutter_file(shutter_number, output_folder):
    """
    Crea un file DATA_BLOCK per un componente FIRESHUTTER.
    
    Args:
        shutter_number (int): Numero progressivo dello shutter
        output_folder (str): Cartella di destinazione
    """
    print(f"DEBUG - create_fire_shutter_file chiamata con:")
    print(f"DEBUG - shutter_number: {shutter_number}")
    print(f"DEBUG - output_folder: {output_folder}")

    data_block_content = f"""DATA_BLOCK "FIRESHUTTER{shutter_number}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"FIRESHUTTER"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"FIRESHUTTER{shutter_number}.scl"
    if not os.path.exists(output_folder):
        print(f"DEBUG - Creazione cartella: {output_folder}")
        os.makedirs(output_folder)
        
    output_path = os.path.join(output_folder, data_block_filename)
    print(f"DEBUG - Scrittura file: {output_path}")
    with open(output_path, 'w') as db_file:
        db_file.write(data_block_content)
    print(f"DEBUG - File FIRESHUTTER creato con successo: {output_path}")

def create_side_input_file(carousel_number, output_folder):
    """
    Crea un file DATA_BLOCK per un componente SIDE_INPUT.
    
    Args:
        carousel_number (int): Numero progressivo del carousel
        output_folder (str): Cartella di destinazione
    """
    print(f"DEBUG - create_side_input_file chiamata con:")
    print(f"DEBUG - carousel_number: {carousel_number}")
    print(f"DEBUG - output_folder: {output_folder}")

    data_block_content = f"""DATA_BLOCK "SIDE_INPUT_CAROUSEL{carousel_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : DF
VERSION : 0.3
NON_RETAIN
"SIDE_INPUT_NCE"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"SIDE_INPUT_CAROUSEL{carousel_number}.scl"
    if not os.path.exists(output_folder):
        print(f"DEBUG - Creazione cartella: {output_folder}")
        os.makedirs(output_folder)
        
    output_path = os.path.join(output_folder, data_block_filename)
    print(f"DEBUG - Scrittura file: {output_path}")
    with open(output_path, 'w') as db_file:
        db_file.write(data_block_content)
    print(f"DEBUG - File SIDE_INPUT creato con successo: {output_path}")

def create_data_block_file(item_id_custom, component_type, output_folder):
    """
    Crea un file DATA_BLOCK per un componente specifico.
    
    Args:
        item_id_custom (str): ID del componente
        component_type (str): Tipo di componente (Carousel/Conveyor/FIRESHUTTER/SHUTTER)
        output_folder (str): Cartella di destinazione
    """
    print(f"DEBUG - create_data_block_file chiamata con:")
    print(f"DEBUG - item_id_custom: {item_id_custom}")
    print(f"DEBUG - component_type: {component_type}")
    print(f"DEBUG - output_folder: {output_folder}")

    # Se l'item contiene "SD", crea un file SAFETYSHUTTER
    if component_type == "SHUTTER":
        print(f"DEBUG - Creazione file SAFETYSHUTTER per {item_id_custom}")
        # Estrai il numero progressivo dal nome del file esistente o usa 1 come default
        shutter_number = 1
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("SAFETYSHUTTER") and f.endswith(".scl")]
        if existing_files:
            numbers = [int(f.replace("SAFETYSHUTTER", "").replace(".scl", "")) for f in existing_files]
            shutter_number = max(numbers) + 1 if numbers else 1
        print(f"DEBUG - Numero SAFETYSHUTTER assegnato: {shutter_number}")
        create_safety_shutter_file(shutter_number, output_folder)
        return

    # Se l'item contiene "FD", crea un file FIRESHUTTER
    if component_type == "FIRESHUTTER":
        print(f"DEBUG - Creazione file FIRESHUTTER per {item_id_custom}")
        # Estrai il numero progressivo dal nome del file esistente o usa 1 come default
        fire_shutter_number = 1
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("FIRESHUTTER") and f.endswith(".scl")]
        if existing_files:
            numbers = [int(f.replace("FIRESHUTTER", "").replace(".scl", "")) for f in existing_files]
            fire_shutter_number = max(numbers) + 1 if numbers else 1
        print(f"DEBUG - Numero FIRESHUTTER assegnato: {fire_shutter_number}")
        create_fire_shutter_file(fire_shutter_number, output_folder)
        return

    # Per gli altri componenti, usa la logica esistente
    print(f"DEBUG - Creazione file standard per {item_id_custom} di tipo {component_type}")
    # Determina il nome corretto del blocco in base al tipo di componente
    if component_type == "Carousel":
        block_name = "CAROUSEL_SEW_MOVIGEAR"
        print(f"DEBUG - Usando nome blocco CAROUSEL: {block_name}")
        # --- LOGICA CENTRALIZZATA: crea anche un nuovo file LINE_# nella cartella _DB Line ---
        output_folder_norm = os.path.normpath(output_folder)
        parts = output_folder_norm.split(os.sep)
        if parts[-1] == "_DB User":
            parts[-1] = "_DB Line"
            db_line_folder = os.sep.join(parts)
            if not os.path.exists(db_line_folder):
                os.makedirs(db_line_folder)
            next_line_number = get_next_line_number(db_line_folder)
            line_filename = f"LINE_{next_line_number}.scl"
            line_file_path = os.path.join(db_line_folder, line_filename)
            with open(line_file_path, 'w') as line_file:
                line_file.write(f'''DATA_BLOCK "LINE_{next_line_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
"LINE"

BEGIN

END_DATA_BLOCK
''')
            print(f"DEBUG - File LINE creato: {line_file_path}")
    else:
        block_name = f"{component_type.upper()}_SEW_MOVIGEAR"
        print(f"DEBUG - Usando nome blocco standard: {block_name}")
    
    data_block_content = f"""DATA_BLOCK "{item_id_custom}"

{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"{block_name}"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"{item_id_custom}.scl"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)
    print(f"DEBUG - File creato: {os.path.join(output_folder, data_block_filename)}")

def create_datalogic_file(item_id_custom, output_folder):
    """
    Crea un file DATA_BLOCK per un componente Datalogic.
    
    Args:
        item_id_custom (str): ID del componente
        output_folder (str): Cartella di destinazione
    """
    data_block_content = f"""DATA_BLOCK "DATALOGIC_{item_id_custom}"

{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : Dani
FAMILY : ATR
VERSION : 0.2
NON_RETAIN
"Sub-Datalogic"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"DATALOGIC_{item_id_custom}.scl"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)

def create_linea_files(df, selected_cab_plc):
    """
    Crea i file LINEA per le configurazioni delle linee.
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
    """
    # Usa la stessa cartella LINEE per i file LINEA
    linee_folder = f'Configurazioni/{selected_cab_plc}/_DB Line'
    if not os.path.exists(linee_folder):
        os.makedirs(linee_folder)
    
    # Estrai i prefissi unici da ITEM_ID_CUSTOM
    unique_prefixes = sorted(set(item[:4].lower() for item in df['ITEM_ID_CUSTOM']))
    
    # Trova i numeri già usati per i file LINE_#.scl
    existing_line_files = [f for f in os.listdir(linee_folder) if f.startswith("LINE_") and f.endswith(".scl")]
    used_numbers = set()
    for f in existing_line_files:
        try:
            n = int(f.replace("LINE_", "").replace(".scl", ""))
            used_numbers.add(n)
        except Exception:
            continue
    
    # Crea un file LINEA per ogni prefisso, usando il primo numero libero
    next_number = 1
    for prefix in unique_prefixes:
        # Trova il primo numero libero
        while next_number in used_numbers:
            next_number += 1
        filename = f"LINE_{next_number}.scl"
        with open(os.path.join(linee_folder, filename), 'w') as f:
            f.write(f"""DATA_BLOCK \"LINE_{next_number}\"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
\"LINE\"

BEGIN

END_DATA_BLOCK
""")
        used_numbers.add(next_number)
        next_number += 1

def get_next_line_number(linee_folder):
    """
    Restituisce il primo numero libero per un nuovo file LINE_# nella cartella specificata.
    """
    existing_line_files = [f for f in os.listdir(linee_folder) if f.startswith("LINE_") and f.endswith(".scl")]
    used_numbers = set()
    for f in existing_line_files:
        try:
            n = int(f.replace("LINE_", "").replace(".scl", ""))
            used_numbers.add(n)
        except Exception:
            continue
    next_number = 1
    while next_number in used_numbers:
        next_number += 1
    return next_number

def _get_item_details(item_data, index_fallback):
    """Helper function to get formatted name and integer number for an item."""
    if not item_data:
        return "NULL", None # Handle case where item_data is None (e.g., no prev/next)

    item_id = item_data.get('ITEM_ID_CUSTOM', f'MISSING_ID_{index_fallback}')
    formatted_name = item_id # Default a ID originale
    number_int = None

    if "ST" in item_id.upper() or "CN" in item_id.upper():
        raw_num = item_data.get('GlobalUtenzaNumber')
        if raw_num is not None:
            try:
                number_int = int(raw_num)
                formatted_name = f"UTENZA{number_int}"
            except (ValueError, TypeError):
                print(f"Attenzione (_get_item_details): Impossibile convertire utenza_number '{raw_num}' in int per {item_id}. Uso fallback nome.")
                formatted_name = f"UTENZA_ERR_{index_fallback}"
                number_int = None # Reset number if conversion failed
        else:
            # Fallback se GlobalUtenzaNumber non trovato
            number_int = index_fallback 
            formatted_name = f"UTENZA{number_int}"
    elif count_ca_occurrences(item_id) == 2:
        raw_num = item_data.get('GlobalCarouselNumber')
        if raw_num is not None:
            try:
                number_int = int(raw_num)
                formatted_name = f"CAROUSEL{number_int}"
            except (ValueError, TypeError):
                print(f"Attenzione (_get_item_details): Impossibile convertire carousel_number '{raw_num}' in int per {item_id}. Uso fallback nome.")
                formatted_name = f"CAROUSEL_ERR_{index_fallback}"
                number_int = None
        else:
            number_int = index_fallback
            formatted_name = f"CAROUSEL{number_int}"

    return formatted_name, number_int

def _is_valid_component_for_chain(item_data):
    """
    Verifica se un componente è valido per la catena (ST, CN o doppio CA)
    """
    item_id = item_data.get('ITEM_ID_CUSTOM', '')
    return ("ST" in item_id.upper() or "CN" in item_id.upper() or count_ca_occurrences(item_id) == 2)

def create_main_file(trunk_number, valid_items, output_folder, last_valid_prev_item_data=None, first_valid_next_item_data=None):
    """
    Crea il file MAINx per un tronco specifico.
    
    Args:
        trunk_number (int): Numero del tronco
        valid_items (list): Lista di elementi nel tronco (dizionari)
        output_folder (str): Cartella di output
        last_valid_prev_item_data (dict, optional): Dati dell'ultimo item valido del tronco precedente.
        first_valid_next_item_data (dict, optional): Dati del primo item valido del tronco successivo.
    """
    content = []
    
    # Aggiungi l'intestazione della funzione
    content.append(f'FUNCTION "MAIN{trunk_number}" : Void')
    content.append('{ S7_Optimized_Access := \'TRUE\' }')
    content.append('VERSION : 0.1')
    content.append('   VAR_TEMP')
    content.append('      StartTronco : Bool;')
    content.append('      TempEncoderNotUsed : "ENCODER_Interface";')
    content.append('   END_VAR')
    content.append('')
    content.append('BEGIN')
    content.append('')
    
    # Aggiungi la sezione di inizializzazione
    content.append("REGION Initializing Temp Section")
    content.append("    #TempEncoderNotUsed.Count := 16#0;")
    content.append("END_REGION")
    content.append("")
    
    # Contatori per elementi FD e SD
    fd_counter = 1
    sd_counter = 1
    
    # Aggiungi la sezione di gestione richiesta start tronco
    content.append("REGION Gestione Richiesta Start Tronco")
    # Assicurati che trunk_number sia intero qui
    try:
        safe_trunk_number = int(trunk_number)
    except (ValueError, TypeError):
        print(f"Attenzione create_main_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
        safe_trunk_number = 0
        
    content.append(f'    IF "UpstreamDB-Globale".Global_Data.Start_All OR') 
    content.append(f'       "UpstreamDB-Globale".Global_Data.StartTronco{safe_trunk_number} OR')
    content.append(f'       "TRUNK{safe_trunk_number}".StartReqAutoFp')
    content.append("    THEN")
    content.append("        #StartTronco := TRUE;")
    content.append("    END_IF;")
    content.append("END_REGION")
    content.append("")
    
    # Aggiungi le chiamate ai blocchi funzionali
    for i, item in enumerate(valid_items):
        item_id = item.get('ITEM_ID_CUSTOM', '')
        
        # Se è un Datalogic (contiene SC), aggiungi la configurazione specifica
        if 'SC' in item_id.upper():
            # Trova l'utenza precedente valida
            prev_utenza = None
            for j in range(i-1, -1, -1):
                prev_item = valid_items[j]
                prev_id = prev_item.get('ITEM_ID_CUSTOM', '')
                if 'ST' in prev_id.upper() or 'CN' in prev_id.upper():
                    prev_utenza = prev_item
                    break
            
            if prev_utenza:
                try:
                    prev_utenza_num = int(prev_utenza.get('GlobalUtenzaNumber', 0))
                except (ValueError, TypeError):
                    print(f"Attenzione: Impossibile convertire GlobalUtenzaNumber in intero per {item_id}. Uso 0.")
                    prev_utenza_num = 0
                    
                content.append(f'REGION Call Datalogic ATR 360 ({item_id})')
                content.append('    ')
                content.append(f'    "DATALOGIC_{item_id}"(')
                content.append('                          TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
                content.append(f'                          Trk := "UTENZA{prev_utenza_num}".Conveyor.Trk,')
                content.append('                          PANYTO_SA := "SV_DB_DATALOGIC_SA".DATALOGIC_1,')
                content.append('                          PANYTO_CMD := "SV_DB_DATALOGIC_CMD".DATALOGIC_1,')
                content.append('                          DB_OBJ := "DBsObject".DbObj[1],')
                content.append('                          "Ist-McpChmMsgBuffer" := "Ist-GtwChmMsgBuffer",')
                content.append('                          "Ist-PcSocket" := "Ist-GtwManageSocket",')
                content.append('                          "Ist-LogBuffer" := "Ist-LogBuffer",')
                content.append('                          "Ist-Logger" := "Ist-Logger",')
                content.append('                          "Ist-VidGenerator" := "Ist_Sub-VidGenerator");')
                content.append('    ')
                content.append('END_REGION')
                content.append('')
            continue  # Salta il resto della logica per i Datalogic
        
        # Se contiene SD, gestisci come SHUTTER
        if "SD" in item_id.upper():
            content.append(f"REGION Call SHUTTER ({item_id})")
            content.append(f'    "SAFETYSHUTTER1".Data.CMD := "SV_DB_SHUTTER_CMD".SHUTTER[{sd_counter}];')
            content.append(f'    "SAFETYSHUTTER1"(Start_From_Line := 1,')
            content.append(f'                     PANYTOSHUTTER_SA := "SV_DB_SHUTTER_SA".SHUTTER[{sd_counter}]);')
            content.append("END_REGION")
            content.append("")
            sd_counter += 1  # Incrementa il contatore solo per elementi SD
            continue  # Salta la generazione delle altre regioni per questo elemento
        
        # --- Ottieni dettagli per item corrente, precedente e successivo EFFETTIVI ---
        current_name, current_number = _get_item_details(item, i + 1) 
        item_id_original = item.get('ITEM_ID_CUSTOM', f'MISSING_ID_{i+1}') 
        
        # Determina il tipo di componente
        item_id_upper = item_id_original.upper()
        
        # Se contiene FD, gestisci come FIRESHUTTER
        if "FD" in item_id_upper:
            content.append(f"REGION Call FIRESHUTTER ({item_id_original})")
            content.append("")
            content.append(f'    "FIRESHUTTER1"(InterfaceTrunkuse := "TRUNK{safe_trunk_number}".ComTrunkUse,')
            content.append(f'                   SV_FIRESHUTTER_CMD := "SV_DB_FIRESHUTTER_CMD".FIRESHUTTER[{fd_counter}],')
            content.append(f'                   SV_FIRESHUTTER_SA := "SV_DB_FIRESHUTTER_SA".FIRESHUTTER[{fd_counter}]);')
            content.append("")
            content.append("END_REGION")
            content.append("")
            fd_counter += 1  # Incrementa il contatore solo per elementi FD
            continue  # Salta la generazione delle altre regioni per questo elemento
            
        # Per gli altri elementi, determina il tipo di componente
        if count_ca_occurrences(item_id_original) == 2:
            component_type = "Carousel"
        elif "ST" in item_id_upper or "CN" in item_id_upper:
            component_type = "Conveyor"
        else:
            component_type = None  # Non è né Carousel né Conveyor standard
            
        # Se non è un componente valido, salta la generazione delle regioni
        if component_type is None:
            continue
        
        # Gestione del riferimento all'item precedente
        prev_item_data_to_use = None
        if i == 0: 
            # Cerca l'ultimo componente valido nel tronco precedente
            if last_valid_prev_item_data and _is_valid_component_for_chain(last_valid_prev_item_data):
                prev_item_data_to_use = last_valid_prev_item_data
        elif i > 0: 
            # Cerca l'ultimo componente valido nel tronco corrente
            for j in range(i-1, -1, -1):
                if _is_valid_component_for_chain(valid_items[j]):
                    prev_item_data_to_use = valid_items[j]
                    break
        # Ottieni i dettagli dell'item precedente
        prev_name_formatted, prev_number = _get_item_details(prev_item_data_to_use, i)
        
        # Determina il tipo di componente precedente (Carousel o Conveyor)
        prev_component_type = "Carousel" if (
            prev_item_data_to_use and 
            count_ca_occurrences(prev_item_data_to_use.get('ITEM_ID_CUSTOM', '')) == 2
        ) else "Conveyor"
        
        # Crea il riferimento al componente precedente o imposta NULL se non esiste
        prev_name_ref = (
            f'"{prev_name_formatted}".{prev_component_type}.Data.OUT' 
            if prev_item_data_to_use 
            else "NULL"
        )

        # Gestione del riferimento all'item successivo
        next_item_data_to_use = None
        found_next_in_trunk = False

        # Cerca il prossimo componente valido nel tronco corrente
        if i < len(valid_items) - 1:
            for j in range(i+1, len(valid_items)):
                if _is_valid_component_for_chain(valid_items[j]):
                    next_item_data_to_use = valid_items[j]
                    found_next_in_trunk = True
                    break

        # Se non è stato trovato un successore valido NEL tronco corrente,
        # usa il primo valido del tronco SUCCESSIVO (se esiste e è valido)
        if not found_next_in_trunk and first_valid_next_item_data and _is_valid_component_for_chain(first_valid_next_item_data):
             next_item_data_to_use = first_valid_next_item_data

        # Ottieni dettagli basati sul risultato della ricerca
        next_name_formatted, next_number = _get_item_details(next_item_data_to_use, i+2)
        next_component_type = "Carousel" if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2 else "Conveyor"

        # Determine next_name_ref based on the correctly identified next_item_data_to_use
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
            # Se il successivo è Carousel, punta al suo SIDE_INPUT
            next_carousel_num_for_side = next_number if next_number is not None else 0
            next_name_ref = f'"SIDE_INPUT_CAROUSEL{next_carousel_num_for_side}".DATA.OUT'
        else:
            # Altrimenti usa il nome formattato e tipo del successivo (Conveyor/Utenza)
            next_name_ref = f'"{next_name_formatted}".{next_component_type}.Data.OUT' if next_item_data_to_use else "NULL"

        # --- Gestione Differenziata Chiamata --- 
        if component_type == "Carousel":
            # --- Generazione Chiamata CAROUSEL ---
            content.append(f"REGION Call CAROUSEL_SEW_MOVIGEAR ({item_id_original})")
            content.append("")
            content.append(f'    "{current_name}"(')
            
            # ID: usa sempre current_number per i CAROUSEL, che è il numero progressivo del carousel
            carousel_id = current_number if current_number is not None else i + 1
            content.append(f'               ID := {carousel_id},')
            content.append('               DINO := 0,')
            
            # PREV: riferimento a SIDE_INPUT
            carousel_prev_ref = f'"SIDE_INPUT_CAROUSEL{current_number if current_number is not None else 0}".DATA.OUT' # Usa current_number per SIDE_INPUT
            content.append(f'               PREV := {carousel_prev_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'               NEXT := {next_name_ref},')
                 
            content.append('               START := #StartTronco,')
            content.append('               TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
            content.append('               Constants := "DB_Constants".Constants,')
            content.append('               DB_Globale := "UpstreamDB-Globale".Global_Data,') # Aggiunto DB_Globale
            content.append(f'               InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'               PANYTOCNV_SA := "SV_DB_CAROUSEL_SA".CAROUSEL_{panytocnv_num_to_use},') # Usa CAROUSEL_SA
            content.append(f'               PANYTOCNV_CMD := "SV_DB_CAROUSEL_CMD".CAROUSEL_{panytocnv_num_to_use},') # Usa CAROUSEL_CMD

            content.append('               DB_OBJ := "DBsObject".DbObj[1],')
            content.append('               "Ist-VidGenerator" := "Ist_Sub-VidGenerator",')
            content.append('               EncoderInterface := #TempEncoderNotUsed,')
            # Drive Interface per Carousel
            content.append(f'               DriveInterface_1_IN := "{item_id_original}_1_IN",') 
            content.append(f'               DriveInterface_1_OUT := "{item_id_original}_1_OUT",') 
            content.append(f'               DriveInterface_2_IN := "{item_id_original}_2_IN",') 
            content.append(f'               DriveInterface_2_OUT := "{item_id_original}_1_OUT",') # Come da esempio

            content.append('               "Ist-McpCreateChrMsg" := "Ist-McpCreateChrMsg",')
            content.append('               "Ist-PcSocket" := "Ist-GtwManageSocket",')
            content.append('               "Ist-McpChrMsgBuffer" := "Ist-GtwChrMsgBuffer",')
            content.append('               "Ist-LogBuffer" := "Ist-LogBuffer",')
            content.append('               "Ist-Logger" := "Ist-Logger");')
            content.append("")
            content.append("END_REGION")
            content.append("")
            # --- Fine Chiamata CAROUSEL ---
            
        else: # component_type == "Conveyor"
            # --- Generazione Chiamata CONVEYOR/UTENZA (standard) ---
            content.append(f"REGION Call CONVEYOR_SEW_MOVIGEAR ({item_id_original})")
            content.append("")
            content.append(f'    "{current_name}"(')
            
            id_value_to_use = current_number if current_number is not None else 0 
            content.append(f'               ID := {id_value_to_use},') 
            
            # PREV: riferimento a item precedente effettivo (gestito sopra da prev_name_ref)
            content.append(f'               PREV := {prev_name_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'               NEXT := {next_name_ref},')

            content.append('               START := #StartTronco,')
            content.append('               TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
            content.append('               Constants := "DB_Constants".Constants,')
            content.append(f'               InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'               PANYTOCNV_SA := "SV_DB_CONVEYOR_SA".CONVEYOR[{panytocnv_num_to_use}],')
            content.append(f'               PANYTOCNV_CMD := "SV_DB_CONVEYOR_CMD".CONVEYOR[{panytocnv_num_to_use}],') # CONVEYOR_CMD

            content.append('               DB_OBJ := "DBsObject".DbObj[1],')
            content.append('               "Ist-VidGenerator" := "Ist_Sub-VidGenerator",')
            content.append('               EncoderInterface := #TempEncoderNotUsed,')
            # Drive Interface standard
            content.append(f'               DriveInterface_IN := "{item_id_original}_IN",') 
            content.append(f'               DriveInterface_OUT := "{item_id_original}_OUT",') 

            content.append('               "Ist-McpCreateChrMsg" := "Ist-McpCreateChrMsg",')
            content.append('               "Ist-PcSocket" := "Ist-GtwManageSocket",')
            content.append('               "Ist-McpChrMsgBuffer" := "Ist-GtwChrMsgBuffer",')
            content.append('               "Ist-LogBuffer" := "Ist-LogBuffer",')
            content.append('               "Ist-Logger" := "Ist-Logger");')
            content.append("")
            content.append("END_REGION")
            content.append("")
            # --- Fine Chiamata CONVEYOR/UTENZA ---
            
        # --- Logica SIDE_INPUT (Spostata DOPO la chiamata del blocco i) ---
        # Se il prossimo elemento EFFETTIVO è un carousel, aggiungi la sua configurazione SIDE_INPUT
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
             side_input_carousel_num = next_number if next_number is not None else 0 
             next_carousel_id = next_item_data_to_use.get('ITEM_ID_CUSTOM', '')
             
             # Crea il file SIDE_INPUT nella cartella _DB User
             utenze_folder = os.path.join(os.path.dirname(output_folder), '_DB User')
             create_side_input_file(side_input_carousel_num, utenze_folder)
             
             content.append(f"REGION Call SIDE INPUT for CAROUSEL{side_input_carousel_num} ({next_carousel_id})")
             content.append("    // il side input si inserisce prima di un carosello , nel tronco precedente al carosello")
             
             # PREV per SIDE_INPUT è l'output dell'elemento CORRENTE (blocco appena generato)
             current_output_ref = f'"{current_name}".{component_type}.Data.OUT'
             content.append(f'    "SIDE_INPUT_CAROUSEL{side_input_carousel_num}"(PREV := {current_output_ref},')
             
             next_carousel_name_for_next = f"CAROUSEL{side_input_carousel_num}"
             content.append(f'                         NEXT := "{next_carousel_name_for_next}".Carousel.Data.OUT,')
             content.append('                         NextObjTransferIn := FALSE,')
             content.append('                         NextObjTransferInAboutToStart := FALSE,')
             
             # PrevFullStatus usa lo stato dell'elemento CORRENTE
             current_full_status_ref = current_output_ref.replace(".Data.OUT", ".Data.SA.ST_FULL")
             content.append(f'                         PrevFullStatus := {current_full_status_ref},')
             
             content.append(f'                         Prev2FullStatus := "{next_carousel_name_for_next}".Carousel.Data.SA.ST_FULL,')
             content.append(f'                         TrunkPrevAutomaticStatus := "TRUNK{safe_trunk_number}".Data.SA.ST_AUTOMATIC,')
             content.append('                         Prev2BufferingActive := FALSE,')
             content.append(f'                         Trk := "{next_carousel_name_for_next}".Carousel.Trk,')
             content.append('                         DB_OBJ_PREV := "DBsObject".DbObj[1],')
             content.append('                         DB_OBJ_NEXT := "DBsObject".DbObj[1]);')
             content.append("")
             content.append("END_REGION")
             content.append("")
        # --- Fine Logica SIDE_INPUT ---
    
    # Aggiungi END_FUNCTION alla fine
    content.append("END_FUNCTION")
    
    # Crea il file
    output_path = os.path.join(output_folder, f"MAIN{safe_trunk_number}.scl") # Usa numero tronco sicuro
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("\n".join(content))

def create_trunk_file(trunk_number, output_folder):
    """
    Crea un file DATA_BLOCK per un tronco specifico.
    
    Args:
        trunk_number (int): Numero del tronco
        output_folder (str): Cartella di destinazione
    """
    # Assicurati che trunk_number sia intero
    try:
        safe_trunk_number = int(trunk_number)
    except (ValueError, TypeError):
        print(f"Attenzione create_trunk_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
        safe_trunk_number = 0
        
    # Contenuto del file TRUNK
    trunk_content = f"""DATA_BLOCK "TRUNK{safe_trunk_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.4
NON_RETAIN
"TRUNK-PCT"

BEGIN

END_DATA_BLOCK
"""
    
    # Nome del file e percorso
    trunk_filename = f"TRUNK{safe_trunk_number}.scl"
    
    # Crea la directory se non esiste
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Scrivi il file
    with open(os.path.join(output_folder, trunk_filename), 'w') as trunk_file:
        trunk_file.write(trunk_content) 

def create_main_structure_file(output_folder, num_lines, selected_cab_plc, trunks_per_line, ordered_prefixes):
    """
    Crea il file di struttura principale con le regioni dei trunk line dinamiche.
    Il numero di regioni corrisponde al numero di LINEAx files creati.
    I MAIN sono raggruppati per prefisso della linea (es. CP11).
    
    Args:
        output_folder (str): Cartella di output
        num_lines (int): Numero di linee da generare
        selected_cab_plc (str): CAB_PLC selezionato
        trunks_per_line (list): Lista con il numero di tronchi per ogni linea
        ordered_prefixes (list): Lista ordinata dei prefissi delle linee (es. ['CP11', 'CP12', ...])
    """
    print(f"Creazione file MAIN [OB1].scl con {num_lines} linee per CAB_PLC {selected_cab_plc}...")
    print(f"Tronchi per linea: {trunks_per_line}")
    print(f"Prefissi ordinati: {ordered_prefixes}")
    
    # Calcola i range di numeri MAIN per ogni linea
    main_ranges = []
    current_main = 1
    for num_trunks in trunks_per_line:
        main_ranges.append((current_main, current_main + num_trunks - 1))
        current_main += num_trunks
    
    print(f"Range MAIN per linea: {main_ranges}")
    
    content = [
        '#ReturnValue := RD_SYS_T(#OBDateTime);',
        '',
        'REGION Time management',
        '    "TimeMng_DB"(OBDateTime := #OBDateTime,',
        '                 StartCycle := TRUE,',
        '                 EndCycle := FALSE,',
        '                 Clk100ms_En := TRUE,',
        '                 Clk200ms_En := TRUE,',
        '                 Clk500ms_En := TRUE,',
        '                 Clk1sec_En := TRUE,',
        '                 Clk1min_En := TRUE,',
        '                 LampeggioLento_En := TRUE,',
        '                 LampeggioVeloce_En := TRUE,',
        '                 Sirena_En := FALSE,',
        '                 DB_Globale := "UpstreamDB-Globale".Global_Data);',
        'END_REGION',
        '',
        'REGION Library constants',
        '    "CONST"("DB_Constants".Constants);',
        'END_REGION',
        '',
        'REGION Configuration',
        '    "CONF"();',
        'END_REGION',
        '',
        'REGION Input signals update',
        '    "DIG_IN"();',
        'END_REGION',
        '',
        'REGION Eth-Communications',
        '    "Ist-Logger"(mSecWeek := "UpstreamDB-Globale".Global_Data.TimeData.mSecWeek,',
        '                    CycleTime := "UpstreamDB-Globale".Global_Data.TimeData.CycleTime,',
        '                    StartUpPlcFlag := "UpstreamDB-Globale".Global_Data.StartUpPlcFlag,',
        '                    "Ist-LogBuffer" := "Ist-LogBuffer");',
        '',
        '   "Ist-GtwManageSocket"(StartUpPlcFlag := "UpstreamDB-Globale".Global_Data.StartUpPlcFlag,',
        '                         GtwConfiguration := "DB-GtwConfiguration".GtwConfiguration,',
        '                         TimeData := "UpstreamDB-Globale".Global_Data.TimeData,',
        '                         SyncroData := "UpstreamDB-Globale".Global_Data.SyncroData,',
        '                         HmiGatewayRd := "DB-HmiGatewayRd",',
        '                         HmiGatewayWr := "DB-HmiGatewayWr",',
        '                         "Ist-ChmMsgBuffer" := "Ist-GtwChmMsgBuffer",',
        '                         "Ist-ChrMsgBuffer" := "Ist-GtwChrMsgBuffer",',
        '                         "Ist-ChmMsgBufferRetry" := "Ist-GtwChmMsgBufferRetry",',
        '                         "Ist-ChrMsgBufferRetry" := "Ist-GtwChrMsgBufferRetry",',
        '                         "Ist-GtwCreateAckMsg" := "Ist-GtwCreateAckMsg",',
        '                         IstDBGtwConfiguration := "DB-GtwConfiguration");',
        'END_REGION',
        '',
        'REGION Line and pushbuttons panel management',
        '    "GEN_LINE"();',
        '    "PULS_LINE"();',
        'END_REGION',
        '',
        'REGION Panels management',
        '    "PANEL1"(PANYTO_SA := "SV_DB_PANEL_SA".MCP1,',
        '             PANYTO_CMD := "SV_DB_PANEL_CMD".MCP1);  // Panel MCP1  ()',
        'END_REGION',
        '',
        'REGION Profibus/Profinet nodes faults managment',
        '    // Abilitazione area di diagnostica per supervisione',
        '    "SV_DB_PROFINET_SA".PROFINET1_ON := TRUE;',
        '    "SV_DB_PROFINET_SA".PROFIBUS1_ON := FALSE;',
        '    "SV_DB_PROFINET_SA".PROFIBUS2_ON := FALSE;',
        '',
        '    "NET_ALM1"(LADDR := 257,',
        '               ERROR => "SV_DB_PROFINET_SA".FAULT_PROFINET1,',
        '               FAULT => "SV_DB_PROFINET_SA".ST_AVR1PN);',
        '    "NET_ALM2"();',
        '    "NET_ALM3"();',
        'END_REGION',
        ''
    ]

    # Aggiungi le regioni dei trunk line in modo dinamico
    for line_num in range(1, num_lines + 1):
        prefix = ordered_prefixes[line_num - 1]
        content.append(f'REGION Trunk Line {line_num} ({prefix})')
        content.append('')
        
        # Ottieni il range di numeri MAIN per questa linea
        start_main, end_main = main_ranges[line_num - 1]
        for main_num in range(start_main, end_main + 1):
            content.append(f'    "MAIN{main_num}"();')
        
        content.append('')
        content.append('END_REGION')
        content.append('')

    # Aggiungi il resto della struttura
    content.extend([
        'REGION Output signals update',
        '    "DIG_OUT"();',
        'END_REGION',
        '',
        'REGION SCADA',
        '    //   "MAIN_SCADA_ATR"();',
        '    //   "MAIN_SCADA_CAROUSEL"();',
        '    //   "MAIN_SCADA_CONVEYOR"();',
        '    //   "MAIN_SCADA_DIAG"();',
        '    //   "MAIN_SCADA_LINE"();',
        '    //   "MAIN_SCADA_PCT"();',
        '    //   "MAIN_SCADA_SINGLE_DIVERTER"();',
        '    //   "MAIN_SCADA_TRUNK"();',
        'END_REGION',
        '',
        'REGION Time management',
        '    "TimeMng_DB"(OBDateTime := #OBDateTime,',
        '                 StartCycle := FALSE,',
        '                 EndCycle := TRUE,',
        '                 Clk100ms_En := TRUE,',
        '                 Clk200ms_En := TRUE,',
        '                 Clk500ms_En := TRUE,',
        '                 Clk1sec_En := TRUE,',
        '                 Clk1min_En := TRUE,',
        '                 LampeggioLento_En := TRUE,',
        '                 LampeggioVeloce_En := TRUE,',
        '                 Sirena_En := TRUE,',
        '                 DB_Globale := "UpstreamDB-Globale".Global_Data);',
        'END_REGION',
        '',
        'REGION PN COMMUNICATION',
        '    "PN_PN_EXCHANGE"();',
        'END_REGION',
        '',
        'REGION Version',
        '    "V_Major" := "PlcSwVersion".MAJOR;',
        '    "V_Minor" := "PlcSwVersion".MINOR;',
        '    "V_Patch" := "PlcSwVersion".PATCH;',
        'END_REGION'
    ])

    # Crea il percorso completo includendo il CAB_PLC
    output_path = os.path.join('Configurazioni', selected_cab_plc, 'MAIN [OB1].scl')
    print(f"Percorso file: {os.path.abspath(output_path)}")
    
    # Crea la cartella se non esiste
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Cartella creata/verificata: {os.path.exists(os.path.dirname(output_path))}")
    
    try:
        with open(output_path, 'w') as f:
            f.write('\n'.join(content))
        print(f"File MAIN [OB1].scl creato con successo in: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Errore durante la creazione del file: {e}")
        
    print("File MAIN [OB1].scl creato con successo!") 

def create_conf_file(selected_cab_plc, df, output_folder, order):
    """
    Crea il file CONF.scl con le configurazioni dei trunk e delle linee.
    
    Args:
        selected_cab_plc (str): CAB_PLC selezionato
        df (DataFrame): DataFrame con i dati
        output_folder (str): Cartella di output
        order (list): Lista dell'ordine selezionato dall'utente
    """
    content = []
    
    # Intestazione della funzione
    content.append('FUNCTION "CONF" : Void')
    content.append('{ S7_Optimized_Access := \'TRUE\' }')
    content.append('VERSION : 0.1')
    content.append('   VAR_TEMP')
    content.append('      RetVal : Int;')
    content.append('      ZeroWord : Word;')
    content.append('   END_VAR')
    content.append('')
    content.append('BEGIN')
    
    # Regione di inizializzazione
    content.append('    REGION Initialization')
    content.append('        #ZeroWord := W#16#0;')
    content.append('    END_REGION')
    content.append('')
    
    # Regione di configurazione generale
    content.append('    REGION General Configuration')
    content.append('        "UpstreamDB-Globale".Global_Data.MachineId := 101;')
    content.append('    END_REGION')
    content.append('')
    
    # Regione di configurazione PANEL1
    content.append('    REGION Config PANEL1 ()')
    content.append('        ')
    content.append('        "PANEL1".Data.CNF.TIME_SIL := L#20000;    // L#20000;')
    content.append('        ')
    content.append('        //Posso lasciare tutto a false, al limite custom per SCADA da vedere a posteriori')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL1  := TRUE;       //  -> Sono a gruppi di 20 allarmi da Signal1 a Signal20')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL2  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL3  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL4  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL5  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL6  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL7  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL8  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL9  := FALSE;      // FALSE;')
    content.append('        "PANEL1".Data.CNF.BLOCK_ALL10 := FALSE;      // FALSE;')
    content.append('        ')
    content.append('        //Profinet alarms CNF')
    content.append('        //Essendo che gli allarmi sono a gruppi di 20, devono essere valorizzati tutti e 20, per questo si mette lo stesso nodo del controller per evitare indice 0')
    content.append('        ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[1]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[2]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[3]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[4]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[5]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[6]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[7]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[8]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[9]  := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[10] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[11] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[12] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[13] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[14] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[15] := ###; ')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[16] := ###;')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[17] := ###;')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[18] := ###;')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[19] := ###;')
    content.append('        "PANEL1".Data.CNF.PROFINET_NODE_BY_SIGNALS[20] := ###;')
    content.append('        ')
    content.append('    END_REGION')
    content.append('')
    
    # Estrai i prefissi dall'ordine selezionato
    unique_lines = []
    for item in order:
        prefix = item.split('. ')[1].lower() if '. ' in item else item.lower()
        prefix_data = df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(prefix)]
        if not prefix_data.empty:
            unique_lines.append(prefix)
            print(f"DEBUG - Aggiunta linea con prefisso: {prefix}")
    
    print(f"DEBUG - Linee ordinate: {unique_lines}")
    
    # Contatore globale per i trunk
    global_trunk_counter = 1
    
    # Per ogni linea nell'ordine selezionato
    for line_idx, line_prefix in enumerate(unique_lines, 1):
        print(f"\nDEBUG - Elaborazione Linea {line_idx} con prefisso {line_prefix}")
        # Regione di configurazione della linea
        content.append(f'    REGION Conf Line {line_idx}')
        content.append(f'        "LINEA{line_idx}".Data.CNF.T_PRESTART_RES := L#5000;')
        content.append(f'        "LINEA{line_idx}".Data.CNF.T_SRNAVR := L#3000;')
        content.append('    END_REGION')
        content.append('')
        
        # Estrai i trunk unici per questa linea
        if 'ITEM_LINE' in df.columns:
            line_trunks = sorted(df[df['ITEM_LINE'] == line_prefix]['ITEM_TRUNK'].unique())
        else:
            line_trunks = sorted(df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(line_prefix.lower())]['ITEM_TRUNK'].unique())
        
        print(f"DEBUG - Tronchi trovati per linea {line_idx}: {line_trunks}")
        
        # Per ogni trunk della linea
        for trunk_num in line_trunks:
            # Estrai gli elementi del trunk
            trunk_items = df[(df['ITEM_ID_CUSTOM'].str.lower().str.startswith(line_prefix.lower())) & 
                           (df['ITEM_TRUNK'] == trunk_num)]
            
            print(f"\nDEBUG - Trunk {global_trunk_counter} (Linea {line_idx}):")
            print(f"DEBUG - Elementi nel trunk: {len(trunk_items)}")
            print("DEBUG - Dettagli elementi:")
            for _, item in trunk_items.iterrows():
                print(f"  - ITEM_ID_CUSTOM: {item['ITEM_ID_CUSTOM']}")
            
            # Conta solo le utenze (ST o CN) escludendo datalogic (SC) e carousel (doppio CA)
            total_conveyors = 0
            for _, item in trunk_items.iterrows():
                item_id = str(item['ITEM_ID_CUSTOM']).upper()
                if ('ST' in item_id or 'CN' in item_id) and 'SC' not in item_id and item_id.count('CA') != 2:
                    total_conveyors += 1
                    print(f"DEBUG - Trovata utenza valida: {item_id}")
            
            print(f"DEBUG - Total conveyors calcolato: {total_conveyors}")
            
            # Regione di configurazione del trunk usando il contatore globale
            content.append(f'    REGION Conf Trunk {global_trunk_counter} Line {line_idx}')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.PRESTART_TIMER := T#10S;     // Prestart Time [ms]')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.ENGSAV_TIMER := T#5S;        // Disable trunk time [ms]')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.SEGN_RESTART_PCT := TRUE;    // TRUE=Signal Restart after reset from PCT')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.SEGN_RESTART := TRUE;        // TRUE=Signal Restart')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.SEGN_REMG := TRUE;           // TRUE=reset emergency also the warning')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.TOT_CONVEYORS := {total_conveyors};         // Total number of conveyors in trunk')
            content.append(f'        "TRUNK{global_trunk_counter}".Data.CNF.EN_FULL_ALLCONV := FALSE;    // TRUE=all conveyors of trunk are full then trunk is full, FALSE = atleast one conveyor of trunk is full then trunk is full')
            content.append('    END_REGION')
            content.append('')
            
            global_trunk_counter += 1
    
    # Reset del contatore globale per la sezione dei device
    global_trunk_counter = 1
    
    # Regione di configurazione dei device per ogni linea
    for line_idx, line_prefix in enumerate(unique_lines, 1):
        content.append(f'    REGION Conf Device Line {line_idx}')
        content.append('        ')
        if 'ITEM_LINE' in df.columns:
            line_trunks = sorted(df[df['ITEM_LINE'] == line_prefix]['ITEM_TRUNK'].unique())
        else:
            line_trunks = sorted(df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(line_prefix.lower())]['ITEM_TRUNK'].unique())
        
        # Aggiungi le chiamate CONF_Tx per ogni trunk della linea
        for trunk_num in line_trunks:
            content.append(f'        "CONF_T{global_trunk_counter}"();')
            global_trunk_counter += 1
        
        content.append('        ')
        content.append('    END_REGION')
        content.append('    ')
        content.append('    ')
    
    # Regione di configurazione della comunicazione SAC
    content.append('    REGION Conf Sac communication')
    content.append('        ')
    content.append('        "GtwConfiguration"();')
    content.append('        ')
    content.append('    END_REGION')
    content.append('    ')
    content.append('    ')
    
    # Regione di abilitazione log
    content.append('    REGION Enable log')
    content.append('        ')
    content.append('        "LOG_ENABLE"(EnableLog := "Ist-Logger".LogSocket.ConnStConnected,')
    content.append('                     EnableDebug:=TRUE);')
    content.append('        ')
    content.append('    END_REGION')
    content.append('    ')
    
    content.append('END_FUNCTION')
    
    # Salva il file
    output_path = os.path.join(output_folder, 'CONF.scl')
    with open(output_path, 'w') as f:
        f.write('\n'.join(content))
    
    print(f"DEBUG - File CONF.scl creato in {output_path}") 