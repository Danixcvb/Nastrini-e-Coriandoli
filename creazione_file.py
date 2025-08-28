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

def create_shutter_file(shutter_number, output_folder):
    """
    Crea un file DATA_BLOCK per un componente SHUTTER.
    
    Args:
        shutter_number (int): Numero progressivo dello shutter
        output_folder (str): Cartella di destinazione
    """
    data_block_content = f"""DATA_BLOCK "SHUTTER{shutter_number}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"SHUTTER"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"SHUTTER{shutter_number}.db"
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
    
    data_block_filename = f"FIRESHUTTER{shutter_number}.db"
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
    
    data_block_filename = f"SIDE_INPUT_CAROUSEL{carousel_number}.db"
    if not os.path.exists(output_folder):
        print(f"DEBUG - Creazione cartella: {output_folder}")
        os.makedirs(output_folder)
        
    output_path = os.path.join(output_folder, data_block_filename)
    print(f"DEBUG - Scrittura file: {output_path}")
    with open(output_path, 'w') as db_file:
        db_file.write(data_block_content)
    print(f"DEBUG - File SIDE_INPUT creato con successo: {output_path}")

def create_oversize_file(oversize_number, output_folder):
    """
    Crea un file DATA_BLOCK per un componente OVERSIZE.
    
    Args:
        oversize_number (int): Numero progressivo dell'oversize
        output_folder (str): Cartella di destinazione
    """
    data_block_content = f"""DATA_BLOCK "OVERSIZE{oversize_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : ENG
VERSION : 0.2
NON_RETAIN
"OVERSIZE"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"OVERSIZE{oversize_number}.db"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)
    print(f"DEBUG - File OVERSIZE creato con successo: {os.path.join(output_folder, data_block_filename)}")

def create_data_block_file(item_id_custom, component_type, output_folder, line_type_mapping):
    """
    Crea un file DATA_BLOCK per un componente specifico.
    
    Args:
        item_id_custom (str): ID del componente
        component_type (str): Tipo di componente (Carousel/Conveyor/FIRESHUTTER/SHUTTER/OVERSIZE)
        output_folder (str): Cartella di destinazione
        line_type_mapping (dict): Dizionario per mappare i numeri di linea ai loro tipi (es. 'Carousel').
    """
    print(f"DEBUG - create_data_block_file chiamata con:")
    print(f"DEBUG - item_id_custom: {item_id_custom}")
    print(f"DEBUG - component_type: {component_type}")
    print(f"DEBUG - output_folder: {output_folder}")

    # Se è un OVERSIZE, crea un file DATA_BLOCK OVERSIZE
    if component_type == "OVERSIZE":
        print(f"DEBUG - Creazione file OVERSIZE per {item_id_custom}")
        oversize_number = 1
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("OVERSIZE") and f.endswith(".db")]
        if existing_files:
            numbers = [int(f.replace("OVERSIZE", "").replace(".db", "")) for f in existing_files]
            oversize_number = max(numbers) + 1 if numbers else 1
        print(f"DEBUG - Numero OVERSIZE assegnato: {oversize_number}")
        create_oversize_file(oversize_number, output_folder)
        return

    # Se l'item contiene "SD", crea un file SHUTTER
    if component_type == "SHUTTER":
        print(f"DEBUG - Creazione file SHUTTER per {item_id_custom}")
        # Estrai il numero progressivo dal nome del file esistente o usa 1 come default
        shutter_number = 1
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("SHUTTER") and f.endswith(".db")]
        if existing_files:
            numbers = [int(f.replace("SHUTTER", "").replace(".db", "")) for f in existing_files]
            shutter_number = max(numbers) + 1 if numbers else 1
        print(f"DEBUG - Numero SHUTTER assegnato: {shutter_number}")
        create_shutter_file(shutter_number, output_folder)
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
            line_type_mapping[next_line_number] = 'Carousel'

            # Logica per creare CAROUSELX_FULL_TIMEOUT.db
            carousel_number = item_id_custom.replace("CAROUSEL", "") # Estrae il numero da "CAROUSELX"
            if carousel_number.isdigit():
                full_timeout_filename = f"CAROUSEL{carousel_number}_FULL_TIMEOUT.db"
                full_timeout_file_path = os.path.join(output_folder, full_timeout_filename)
                full_timeout_content = f"""DATA_BLOCK "CAROUSEL{carousel_number}_FULL_TIMEOUT"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"CAROUSEL_FULL_TIMEOUT"

BEGIN

END_DATA_BLOCK
"""
                with open(full_timeout_file_path, 'w') as ft_file:
                    ft_file.write(full_timeout_content)
                print(f"DEBUG - File CAROUSEL_FULL_TIMEOUT creato: {full_timeout_file_path}")

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
    
    data_block_filename = f"{item_id_custom}.db"
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
    
    data_block_filename = f"DATALOGIC_{item_id_custom}.db"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)

def create_linea_files(df, selected_cab_plc, line_type_mapping):
    """
    Crea i file LINEA per le configurazioni delle linee (LINEA1 per normale, LINEA2 per Carousel se presente).
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
        line_type_mapping (dict): Dizionario per mappare i numeri di linea ai loro tipi (es. 'Carousel').
    """
    linee_folder = f'Configurazioni/{selected_cab_plc}/_DB Line'
    os.makedirs(linee_folder, exist_ok=True)
    
    # Pulisci il mapping esistente per evitare residui da precedenti esecuzioni
    line_type_mapping.clear()

    # 1. Crea sempre LINEA1.scl (linea normale)
    line_num_normal = 1
    filename_normal = f"LINE_{line_num_normal}.scl"
    with open(os.path.join(linee_folder, filename_normal), 'w') as f:
        f.write(f"""DATA_BLOCK \"LINE_{line_num_normal}\"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
\"LINE\"

BEGIN

END_DATA_BLOCK
""")
    print(f"DEBUG - File LINEA{line_num_normal}.scl creato: {os.path.join(linee_folder, filename_normal)}")
    line_type_mapping[line_num_normal] = 'Normale'

    # 2. Controlla se esistono elementi Carousel nel DataFrame
    #    Per fare questo, dobbiamo usare il df completo (non solo cab_plc_data filtrato, ma l'originale df se la logica carousel è globale)
    #    Assumiamo che la logica di consolidamento dei carousel sia già stata applicata a df a monte in process_excel
    carousel_exists = (df['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2).any()

    if carousel_exists:
        line_num_carousel = 2
        filename_carousel = f"LINE_{line_num_carousel}.scl"
        with open(os.path.join(linee_folder, filename_carousel), 'w') as f:
            f.write(f"""DATA_BLOCK \"LINE_{line_num_carousel}\"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
\"LINE\"

BEGIN

END_DATA_BLOCK
""")
        print(f"DEBUG - File LINEA{line_num_carousel}.scl creato: {os.path.join(linee_folder, filename_carousel)}")
        line_type_mapping[line_num_carousel] = 'Carousel'
    
    print(f"DEBUG - line_type_mapping finale: {line_type_mapping}")

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
    elif "SD" in item_id.upper(): # Aggiungi la logica per SHUTTER
        raw_num = item_data.get('GlobalShutterNumber')
        if raw_num is not None:
            try:
                number_int = int(raw_num)
                formatted_name = f"SHUTTER{number_int}"
            except (ValueError, TypeError):
                print(f"Attenzione (_get_item_details): Impossibile convertire shutter_number '{raw_num}' in int per {item_id}. Uso fallback nome.")
                formatted_name = f"SHUTTER_ERR_{index_fallback}"
                number_int = None
        else:
            number_int = index_fallback
            formatted_name = f"SHUTTER{number_int}"

    return formatted_name, number_int

def _is_valid_component_for_chain(item_data):
    """
    Verifica se un componente è valido per la catena (ST, CN o doppio CA)
    """
    item_id = item_data.get('ITEM_ID_CUSTOM', '')
    return ("ST" in item_id.upper() or "CN" in item_id.upper() or count_ca_occurrences(item_id) == 2)

def create_main_file(trunk_number, valid_items, output_folder, last_valid_prev_item_data=None, first_valid_next_item_data=None, trunk_to_line_mapping=None):
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
    content.append('   VAR_TEMP ')
    content.append('      StartTronco : Bool;')
    content.append('      TempEncoderNotUsed : "ENCODER_Interface";')
    content.append('   END_VAR')
    content.append('')
    content.append('')
    content.append('BEGIN')
    content.append('')
    
    # Aggiungi la sezione di inizializzazione
    content.append('	REGION Initializing Temp Section')
    content.append('	    ')
    content.append('	    #TempEncoderNotUsed.Count := 16#0;')
    content.append('	    ')
    content.append('	END_REGION')
    content.append('	')
    
    # Contatori per elementi FD e SD
    fd_counter = 1
    datalogic_counter = 1
    oversize_counter = 1

    # Aggiungi la sezione di gestione richiesta start tronco
    content.append('	REGION Gestione Richiesta Start Tronco')
    content.append('')
    # Assicurati che trunk_number sia intero qui
    try:
        safe_trunk_number = int(trunk_number)
    except (ValueError, TypeError):
        print(f"Attenzione create_main_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
        safe_trunk_number = 0
        
    associated_line_num = trunk_to_line_mapping.get(safe_trunk_number, 1) if trunk_to_line_mapping else 1

    content.append(f'	    IF "UpstreamDB-Globale".Global_Data.Start_All OR') 
    content.append(f'	        "UpstreamDB-Globale".Global_Data.StartTronco{safe_trunk_number} OR')
    content.append(f'	        "TRUNK{safe_trunk_number}".StartReqAutoFp')
    content.append(f'	    THEN')
    content.append('	        #StartTronco := TRUE;')
    content.append('	    END_IF;')
    content.append('	    ')
    content.append('	END_REGION')
    content.append('	')
    
    # Aggiungi le chiamate ai blocchi funzionali
    for i, item in enumerate(valid_items):
        item_id_original = item.get('ITEM_ID_CUSTOM', f'MISSING_ID_{i+1}') 
        current_name, current_number = _get_item_details(item, i + 1) 
        item_id_upper = item_id_original.upper()

        # Determina il tipo di componente
        component_type = None
        if 'SC' in item_id_upper: # Datalogic
            component_type = "Datalogic"
        elif "SD" in item_id_upper:
            component_type = "SHUTTER"
        elif "FD" in item_id_upper:
            component_type = "FIRESHUTTER"
        elif count_ca_occurrences(item_id_original) == 2:
            component_type = "Carousel"
        elif "ST" in item_id_upper or "CN" in item_id_upper:
            component_type = "Conveyor"
        elif "OG" in item_id_upper:
            component_type = "OVERSIZE"
        
        # Se non è un componente valido per la catena, salta
        if component_type is None:
            continue

        # Gestione del riferimento all'item precedente (valido per tutti i tipi di catena)
        prev_item_data_to_use = None
        if i == 0: 
            if last_valid_prev_item_data and _is_valid_component_for_chain(last_valid_prev_item_data):
                prev_item_data_to_use = last_valid_prev_item_data
        elif i > 0: 
            for j in range(i-1, -1, -1):
                if _is_valid_component_for_chain(valid_items[j]):
                    prev_item_data_to_use = valid_items[j]
                    break
        prev_name_formatted, prev_number = _get_item_details(prev_item_data_to_use, i)
        prev_component_type = "Carousel" if (prev_item_data_to_use and count_ca_occurrences(prev_item_data_to_use.get('ITEM_ID_CUSTOM', '')) == 2) else "Conveyor"
        prev_name_ref = (f'"{prev_name_formatted}".{prev_component_type}.Data.OUT' if prev_item_data_to_use else "NULL")

        # Gestione del riferimento all'item successivo (valido per tutti i tipi di catena)
        next_item_data_to_use = None
        found_next_in_trunk = False
        if i < len(valid_items) - 1:
            for j in range(i+1, len(valid_items)):
                if _is_valid_component_for_chain(valid_items[j]):
                    next_item_data_to_use = valid_items[j]
                    found_next_in_trunk = True
                    break
        if not found_next_in_trunk and first_valid_next_item_data and _is_valid_component_for_chain(first_valid_next_item_data):
             next_item_data_to_use = first_valid_next_item_data
        next_name_formatted, next_number = _get_item_details(next_item_data_to_use, i+2)
        next_component_type = "Carousel" if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2 else "Conveyor"
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
            next_carousel_num_for_side = next_number if next_number is not None else 0
            next_name_ref = f'"SIDE_INPUT_CAROUSEL{next_carousel_num_for_side}".DATA.OUT'
        else:
            next_name_ref = f'"{next_name_formatted}".{next_component_type}.Data.OUT' if next_item_data_to_use else "NULL"
        
        # Se è un Datalogic (contiene SC), aggiungi la configurazione specifica
        if component_type == "Datalogic":
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
                    print(f"Attenzione: Impossibile convertire GlobalUtenzaNumber in intero per {item_id_original}. Uso 0.")
                    prev_utenza_num = 0
                    
                content.append(f'	REGION Call Datalogic ATR 360 ({item_id_original})')
                content.append('	    ')
                content.append(f'	    "DATALOGIC_{item_id_original}"(')
                content.append('	                          TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
                content.append(f'	                          Trk := "UTENZA{prev_utenza_num}".Conveyor.Trk,')
                content.append(f'	                          PANYTO_SA := "SV_DB_DATALOGIC_SA".DATALOGIC[{datalogic_counter}],')
                content.append(f'	                          PANYTO_CMD := "SV_DB_DATALOGIC_CMD".DATALOGIC[{datalogic_counter}],')
                content.append('	                          DB_OBJ := "DBsObject".DbObj[1],')
                content.append('	                          "Ist-McpChmMsgBuffer" := "Ist-GtwChmMsgBuffer",')
                content.append('	                          "Ist-PcSocket" := "Ist-GtwManageSocket",')
                content.append('	                          "Ist-LogBuffer" := "Ist-LogBuffer",')
                content.append('	                          "Ist-Logger" := "Ist-Logger",')
                content.append('	                          "Ist-VidGenerator" := "Ist_Sub-VidGenerator");')
                content.append('	    ')
                content.append('	END_REGION')
                content.append('	')
                datalogic_counter += 1
            continue  # Salta il resto della logica per i Datalogic
        
        # Se contiene SD, gestisci come SHUTTER
        if component_type == "SHUTTER":
            shutter_num = current_number if current_number is not None else 0 # Use global shutter number
            content.append(f"	REGION Call SHUTTER ({item_id_original})")
            content.append(f'	    "SHUTTER{shutter_num}".Data.CMD := "SV_DB_SHUTTER_CMD".SHUTTER[{shutter_num}];')
            content.append(f'	    "SHUTTER{shutter_num}"(PANYTOSHUTTER_SA := "SV_DB_SHUTTER_SA".SHUTTER[{shutter_num}],')
            content.append(f'	                     PREV := {prev_name_ref},')
            content.append(f'	                     NEXT := {next_name_ref},')
            content.append(f'	                     InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,')
            content.append(f'	                     DB_Globale := "UpstreamDB-Globale".Global_Data);')
            content.append("	END_REGION")
            content.append('	')
            continue  # Salta la generazione delle altre regioni per questo elemento
        
        # Se contiene FD, gestisci come FIRESHUTTER
        if component_type == "FIRESHUTTER":
            content.append(f"	REGION Call FIRESHUTTER ({item_id_original})")
            content.append('	    ')
            content.append(f'	    "FIRESHUTTER{fd_counter}"(InterfaceTrunkuse := "TRUNK{safe_trunk_number}".ComTrunkUse,')
            content.append(f'	                   SV_FIRESHUTTER_CMD := "SV_DB_FIRESHUTTER_CMD".FIRESHUTTER[{fd_counter}],')
            content.append(f'	                   SV_FIRESHUTTER_SA := "SV_DB_FIRESHUTTER_SA".FIRESHUTTER[{fd_counter}]);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            fd_counter += 1  # Incrementa il contatore solo per elementi FD
            continue  # Salta la generazione delle altre regioni per questo elemento
            
        # Se contiene OG, gestisci come OVERSIZE
        if component_type == "OVERSIZE":
            content.append(f"	REGION Call OVERSIZE ({item_id_original})")
            content.append(f'	    "OVERSIZE{oversize_counter}"(ID:=0,')
            content.append(f'	                InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,')
            content.append(f'	                PANYTO_SA := "SV_DB_OVERSIZE_SA".OVERSIZE[{oversize_counter}],')
            content.append(f'	                PANYTO_CMD := "SV_DB_OVERSIZE_CMD".OVERSIZE[{oversize_counter}]);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            oversize_counter += 1 # Incrementa il contatore solo per elementi OVERSIZE
            continue # Salta la generazione delle altre regioni per questo elemento

        # Per gli altri elementi (Carousel/Conveyor)
        if component_type == "Carousel":
            # --- Generazione Chiamata CAROUSEL ---
            content.append(f"\tREGION Call CAROUSEL_SEW_MOVIGEAR ({item_id_original})")
            content.append('	    ')
            content.append(f'	    "{current_name}"(')
            
            # ID: usa sempre current_number per i CAROUSEL, che è il numero progressivo del carousel
            carousel_id = current_number if current_number is not None else i + 1
            content.append(f'	              ID := {carousel_id},')
            content.append('	              DINO := 0,')
            
            # PREV: riferimento a SIDE_INPUT
            carousel_prev_ref = f'"SIDE_INPUT_CAROUSEL{current_number if current_number is not None else 0}".DATA.OUT' # Usa current_number per SIDE_INPUT
            content.append(f'	              PREV := {carousel_prev_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'	              NEXT := {next_name_ref},')
                 
            content.append('	              START := #StartTronco,')
            content.append('	              TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
            content.append('	              Constants := "DB_Constants".Constants,')
            content.append('	              DB_Globale := "UpstreamDB-Globale".Global_Data,) # Aggiunto DB_Globale')
            content.append(f'	              InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'	              PANYTOCNV_SA := "SV_DB_CAROUSEL_SA".CAROUSEL[{panytocnv_num_to_use}],') # Usa CAROUSEL_SA
            content.append(f'	              PANYTOCNV_CMD := "SV_DB_CAROUSEL_CMD".CAROUSEL[{panytocnv_num_to_use}],') # Usa CAROUSEL_CMD

            content.append('	              DB_OBJ := "DBsObject".DbObj[1],')
            content.append('	              "Ist-VidGenerator" := "Ist_Sub-VidGenerator",')
            content.append('	              EncoderInterface := #TempEncoderNotUsed,')
            # Drive Interface per Carousel
            content.append(f'	              DriveInterface_1_IN := "{item_id_original}_1_IN",') 
            content.append(f'	              DriveInterface_1_OUT := "{item_id_original}_1_OUT",') 
            content.append(f'	              DriveInterface_2_IN := "{item_id_original}_2_IN",') 
            content.append(f'	              DriveInterface_2_OUT := "{item_id_original}_2_OUT",')

            content.append('	              "Ist-McpCreateChrMsg" := "Ist-McpCreateChrMsg",')
            content.append('	              "Ist-PcSocket" := "Ist-GtwManageSocket",')
            content.append('	              "Ist-McpChrMsgBuffer" := "Ist-GtwChrMsgBuffer",')
            content.append('	              "Ist-LogBuffer" := "Ist-LogBuffer",')
            content.append('	              "Ist-Logger" := "Ist-Logger");')
            content.append('	    ')
            content.append(f'	            "CAROUSEL{carousel_id}_FULL_TIMEOUT"(PrevLineRunning:="LINE_{associated_line_num}".Data.SA.ST_RUN,')
            content.append('	                                     LapsBeforeStopping:=1,')
            content.append('	                                     WindowLengthFromBooking:=7.0,')
            content.append(f'	                                     Carousel :="CAROUSEL{carousel_id}".Carousel);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            # --- Fine Chiamata CAROUSEL ---
            
        elif component_type == "Conveyor":
            # --- Generazione Chiamata CONVEYOR/UTENZA (standard) ---
            content.append(f"\tREGION Call CONVEYOR_SEW_MOVIGEAR ({item_id_original})")
            content.append('	    ')
            content.append(f'	    "{current_name}"(')
            
            id_value_to_use = current_number if current_number is not None else 0 
            content.append(f'	              ID := {id_value_to_use},') 
            
            # PREV: riferimento a item precedente effettivo (gestito sopra da prev_name_ref)
            content.append(f'	              PREV := {prev_name_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'	              NEXT := {next_name_ref},')

            content.append('	              START := #StartTronco,')
            content.append('	              TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
            content.append('	              Constants := "DB_Constants".Constants,')
            content.append(f'	              InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'	              PANYTOCNV_SA := "SV_DB_CONVEYOR_SA".CONVEYOR[{panytocnv_num_to_use}],')
            content.append(f'	              PANYTOCNV_CMD := "SV_DB_CONVEYOR_CMD".CONVEYOR[{panytocnv_num_to_use}],')

            content.append('	              DB_OBJ := "DBsObject".DbObj[1],')
            content.append('	              "Ist-VidGenerator" := "Ist_Sub-VidGenerator",')
            content.append('	              EncoderInterface := #TempEncoderNotUsed,')
            # Drive Interface standard
            content.append(f'	              DriveInterface_IN := "{item_id_original}_IN",') 
            content.append(f'	              DriveInterface_OUT := "{item_id_original}_OUT",') 

            content.append('	              "Ist-McpCreateChrMsg" := "Ist-McpCreateChrMsg",')
            content.append('	              "Ist-PcSocket" := "Ist-GtwManageSocket",')
            content.append('	              "Ist-McpChrMsgBuffer" := "Ist-GtwChrMsgBuffer",')
            content.append('	              "Ist-LogBuffer" := "Ist-LogBuffer",')
            content.append('	              "Ist-Logger" := "Ist-Logger");')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            # --- Fine Chiamata CONVEYOR/UTENZA ---
            
        # --- Logica SIDE_INPUT (Spostata DOPO la chiamata del blocco i) ---
        # Se il prossimo elemento EFFETTIVO è un carousel, aggiungi la sua configurazione SIDE_INPUT
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
             side_input_carousel_num = next_number if next_number is not None else 0 
             next_carousel_id = next_item_data_to_use.get('ITEM_ID_CUSTOM', '')
             
             # Crea il file SIDE_INPUT nella cartella _DB User
             utenze_folder = os.path.join(os.path.dirname(output_folder), '_DB User')
             create_side_input_file(side_input_carousel_num, utenze_folder)
             
             content.append(f"\tREGION Call SIDE INPUT for CAROUSEL{side_input_carousel_num} ({next_carousel_id})")
             content.append("\t    // il side input si inserisce prima di un carosello , nel tronco precedente al carosello")
             
             # PREV per SIDE_INPUT è l'output dell'elemento CORRENTE (blocco appena generato)
             current_output_ref = f'"{current_name}".{component_type}.Data.OUT'
             content.append(f'	    "SIDE_INPUT_CAROUSEL{side_input_carousel_num}"(PREV := {current_output_ref},')
             
             next_carousel_name_for_next = f"CAROUSEL{side_input_carousel_num}"
             content.append(f'	                         NEXT := "{next_carousel_name_for_next}".Carousel.Data.OUT,')
             content.append('	                         NextObjTransferIn := FALSE,')
             content.append('	                         NextObjTransferInAboutToStart := FALSE,')
             
             # Formatta item_id_original per FTU_Conveyor
             formatted_item_id_for_ftu = item_id_original
             if "ST" in item_id_original:
                 formatted_item_id_for_ftu = item_id_original.replace("ST", "_ST", 1)
             elif "CN" in item_id_original:
                 formatted_item_id_for_ftu = item_id_original.replace("CN", "_CN", 1)

             
             
             # PrevFullStatus usa lo stato dell'elemento CORRENTE
             current_full_status_ref = current_output_ref.replace(".Data.OUT", ".Data.SA.ST_FULL")
             content.append(f'	                         PrevFullStatus := {current_full_status_ref},')
             
             content.append(f'	                         Prev2FullStatus := "{next_carousel_name_for_next}".Carousel.Data.SA.ST_FULL,')
             content.append(f'	                         TrunkPrevAutomaticStatus := "TRUNK{safe_trunk_number}".Data.SA.ST_AUTOMATIC,')
             content.append('	                         Prev2BufferingActive := FALSE,')
             content.append(f'	                         FTU_Conveyor:= NOT "{formatted_item_id_for_ftu}_B1101_STOP_HEAD_PHOTOCELL",')
             content.append(f'	                         Trk := "{next_carousel_name_for_next}".Carousel.Trk,')
             content.append('	                         DB_OBJ_PREV := "DBsObject".DbObj[1],')
             content.append('	                         DB_OBJ_NEXT := "DBsObject".DbObj[1]);')
             content.append('	    ')
             content.append("	END_REGION")
             content.append('	')
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
        content.append(f'        "LINE_{line_idx}".Data.CNF.T_PRESTART_RES := L#5000;')
        content.append(f'        "LINE_{line_idx}".Data.CNF.T_SRNAVR := L#3000;')
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

def generate_gen_line_file(df, selected_cab_plc, line_type_mapping, ordered_prefixes, trunk_to_line_mapping):
    """
    Genera il file GEN_LINE.scl in base alle linee e ai trunk esistenti.

    Args:
        df (DataFrame): DataFrame con i dati completi.
        selected_cab_plc (str): CAB_PLC selezionato.
        line_type_mapping (dict): Mappa dei numeri di linea ai loro tipi (es. 'Carousel').
        ordered_prefixes (list): Lista ordinata dei prefissi delle linee (es. ['CP11', 'CP12', ...]).
        trunk_to_line_mapping (dict): Mappa dei numeri di trunk ai numeri di linea associati.
    """
    print(f"DEBUG - Generazione di GEN_LINE.scl per {selected_cab_plc}...")
    
    line_folder = os.path.join('Configurazioni', selected_cab_plc, 'LINE')
    os.makedirs(line_folder, exist_ok=True)
    
    gen_line_content = []
    gen_line_content.append("FUNCTION \"GEN_LINE\" : Void")
    gen_line_content.append("{ S7_Optimized_Access := 'TRUE' }")
    gen_line_content.append("VERSION : 0.1")
    gen_line_content.append("   VAR_TEMP ")
    gen_line_content.append("      StartTronco : Bool;")
    gen_line_content.append("      tempBool : Bool;")
    gen_line_content.append('   END_VAR')
    gen_line_content.append("")
    gen_line_content.append("BEGIN")
    gen_line_content.append("")

    # Ordina i numeri di linea per assicurare un output consistente
    sorted_line_numbers = sorted(line_type_mapping.keys())

    # Genera le chiamate LINE
    for line_num in sorted_line_numbers:
        line_type = line_type_mapping.get(line_num, 'Normale')
        
        region_comment = f"Call LINE {line_num}"
        if line_type == 'Carousel':
            region_comment += " (Carousel)"
        
        gen_line_content.append(f"\tREGION {region_comment}")
        gen_line_content.append("\t    ")
        gen_line_content.append(f"\t    \"LINEA{line_num}\"(")
        gen_line_content.append("\t             TimeData := \"UpstreamDB-Globale\".Global_Data.TimeData,")
        gen_line_content.append("\t             LMP_RUN => #tempBool,")
        gen_line_content.append("\t             LMP_AVR => #tempBool,")
        gen_line_content.append("\t             SRN_AVR => #tempBool,")
        gen_line_content.append(f"\t             PANYTO_SA := \"SV_DB_LINE_SA\".LINE[{line_num}],")
        gen_line_content.append(f"\t             PANYTO_CMD := \"SV_DB_LINE_CMD\".LINE[{line_num}]);")
        gen_line_content.append("\t    ")
        gen_line_content.append("\tEND_REGION")
        gen_line_content.append("\t")

    # Ottieni tutti i trunk_numbers disponibili per il CAB_PLC corrente
    trunk_files = []
    trunk_folder = os.path.join('Configurazioni', selected_cab_plc, '_DB Trunk')
    if os.path.exists(trunk_folder):
        trunk_files = [f for f in os.listdir(trunk_folder) if f.startswith("TRUNK") and f.endswith(".scl")]
    
    trunk_numbers = sorted([int(f.replace("TRUNK", "").replace(".scl", "")) for f in trunk_files])

    # Per ogni trunk, genera le chiamate TRUNK
    for trunk_num in trunk_numbers:
        # Usa la mappatura trunk_to_line_mapping per associare il trunk alla linea corretta
        associated_line_num = trunk_to_line_mapping.get(trunk_num, 1)  # Default a 1 se non trovato
        
        gen_line_content.append(f"\tREGION Call TRUNK {trunk_num} LINE {associated_line_num}")
        gen_line_content.append("\t")
        gen_line_content.append(f"\t    #StartTronco := \"UpstreamDB-Globale\".Global_Data.Start_All OR \"UpstreamDB-Globale\".Global_Data.StartTronco{trunk_num};")
        gen_line_content.append("\t    ")
        gen_line_content.append(f"\t    \"TRUNK{trunk_num}\"(")
        gen_line_content.append(f"\t             ID := {trunk_num},")
        gen_line_content.append("\t             Start_Tronco := #StartTronco,")
        gen_line_content.append("\t             TimeData := \"UpstreamDB-Globale\".Global_Data.TimeData,")
        gen_line_content.append(f"\t             PANYTOTRUNK_SA := \"SV_DB_TRUNK_SA\".TRUNK[{trunk_num}],")
        gen_line_content.append(f"\t             PANYTOTRUNK_CMD := \"SV_DB_TRUNK_CMD\".TRUNK[{trunk_num}],")
        gen_line_content.append(f"\t             PANYTOPCT_SA := \"SV_DB_PCT_SA\".PCT[{trunk_num}],")
        gen_line_content.append(f"\t             PANYTOPCT_CMD := \"SV_DB_PCT_CMD\".PCT[{trunk_num}],")
        gen_line_content.append(f"\t             InterfaceLineTrunk := \"LINEA{associated_line_num}\".ComLineTrunk);")
        gen_line_content.append("\tEND_REGION")
        gen_line_content.append("\t")
    
    gen_line_content.append("END_FUNCTION")

    output_path = os.path.join(line_folder, 'GEN_LINE.scl')
    with open(output_path, 'w') as f:
        f.write("\n".join(gen_line_content))
    print(f"DEBUG - File GEN_LINE.scl creato in {output_path}") 