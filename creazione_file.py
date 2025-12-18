"""
Questo modulo contiene le funzioni per la creazione dei file di configurazione.
Gestisce la generazione dei file .txt e .scl per le configurazioni dei nastri trasportatori.
"""

import os
from funzioni_elaborazione import count_ca_occurrences, get_last_three_digits
import pandas as pd
from io_data import find_io_list_file

def create_txt_files(df, selected_cab_plc, order):
    """
    Crea i file .txt per le configurazioni delle linee.
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
        order: Ordine selezionato per la generazione dei file
    """
    # Crea una directory API0## - all files go directly here
    api_folder = f'API0{selected_cab_plc[-2:]}'
    linee_folder = f'Configurazioni/{selected_cab_plc}/{api_folder}'
    if not os.path.exists(linee_folder):
        os.makedirs(linee_folder)
    
    # Estrai i prefissi unici da ITEM_ID_CUSTOM
    unique_prefixes = sorted(set(item[:4].lower() for item in df['ITEM_ID_CUSTOM']))
    
    # Crea un file .txt per ogni prefisso - directly in API0## folder
    for index, prefix in enumerate(unique_prefixes):
        # Converti il nome del file in maiuscolo
        filename = f"{prefix.upper()}.txt"
        # Salva tutti i file di prefisso direttamente nella cartella API0##
        with open(os.path.join(linee_folder, filename), 'w') as f:
            # Filtra le righe per il prefisso corrente
            prefix_data = df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(prefix)]
            for _, row in prefix_data.iterrows():
                f.write(f"{row['ITEM_ID_CUSTOM']}\n")
    
    # Salva l'ordine selezionato in un file di testo direttamente nella cartella API0##
    with open(os.path.join(linee_folder, 'selected_order.txt'), 'w') as order_file:
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

    data_block_content = f"""DATA_BLOCK "Side_Input_Carousel{carousel_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : DF
VERSION : 0.3
NON_RETAIN
"SIDE_INPUT_NCE"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"Side_Input_Carousel{carousel_number}.db"
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
    data_block_content = f"""DATA_BLOCK "Oversize{oversize_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : ENG
VERSION : 0.2
NON_RETAIN
"OVERSIZE"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"Oversize{oversize_number}.db"
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
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("Oversize") and f.endswith(".db")]
        if existing_files:
            numbers = [int(f.replace("Oversize", "").replace(".db", "")) for f in existing_files]
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
        # Cerca file FIRESHUTTER già creati (.db) per assegnare il numero successivo
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("FIRESHUTTER") and f.endswith(".db")]
        if existing_files:
            numbers = [int(f.replace("FIRESHUTTER", "").replace(".db", "")) for f in existing_files]
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
        # --- LOGICA CENTRALIZZATA: crea anche un nuovo file DbiLine# nella cartella API0## ---
        # Files are now all in API0## folder, so use the same folder
        db_line_folder = output_folder
        if not os.path.exists(db_line_folder):
            os.makedirs(db_line_folder)
        next_line_number = get_next_line_number(db_line_folder)
        line_filename = f"DbiLine{next_line_number}.db"
        line_file_path = os.path.join(db_line_folder, line_filename)
        with open(line_file_path, 'w') as line_file:
            line_file.write(f'''DATA_BLOCK "DbiLine{next_line_number}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
"LINE"

BEGIN

END_DATA_BLOCK
''')
        print(f"DEBUG - File DbiLine creato: {line_file_path}")
        line_type_mapping[next_line_number] = 'Carousel'

        # Logica per creare Carousel#_Full_Timeout.db
        carousel_number = item_id_custom.replace("CAROUSEL", "") # Estrae il numero da "CAROUSELX"
        if carousel_number.isdigit():
            full_timeout_filename = f"Carousel{carousel_number}_Full_Timeout.db"
            full_timeout_file_path = os.path.join(output_folder, full_timeout_filename)
            full_timeout_content = f"""DATA_BLOCK "Carousel{carousel_number}_Full_Timeout"
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
    data_block_content = f"""DATA_BLOCK "Datalogic_{item_id_custom}"

{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : Dani
FAMILY : ATR
VERSION : 0.2
NON_RETAIN
"Sub-Datalogic"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"Datalogic_{item_id_custom}.db"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)

def create_linea_files(df, selected_cab_plc, line_type_mapping, ordered_prefixes):
    """
    Crea i file LINEA per le configurazioni delle linee.
    Crea 1 LINE per ciascun prefisso selezionato, più 1 extra per ciascun prefisso che ha caroselli.
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
        line_type_mapping (dict): Dizionario per mappare i numeri di linea ai loro tipi (es. 'Carousel').
        ordered_prefixes (list): Lista ordinata dei prefissi selezionati.
    """
    api_folder = f'API0{selected_cab_plc[-2:]}'
    linee_folder = f'Configurazioni/{selected_cab_plc}/{api_folder}'
    os.makedirs(linee_folder, exist_ok=True)
    
    # Elimina file .scl vecchi di DbiLine e DbiTrunkLN prima di generare i nuovi .db
    if os.path.exists(linee_folder):
        for file in os.listdir(linee_folder):
            if (file.startswith('DbiLine') or file.startswith('DbiTrunkLN')) and file.endswith('.scl'):
                old_file_path = os.path.join(linee_folder, file)
                try:
                    os.remove(old_file_path)
                    print(f"DEBUG - Rimosso file vecchio: {file}")
                except Exception as e:
                    print(f"DEBUG - Impossibile rimuovere {file}: {e}")
    
    # Pulisci il mapping esistente per evitare residui da precedenti esecuzioni
    line_type_mapping.clear()
    
    # Assicurati che df sia filtrato per il CAB_PLC selezionato
    df_filtered = df[df['CAB_PLC'] == selected_cab_plc].copy() if 'CAB_PLC' in df.columns else df.copy()
    print(f"DEBUG - create_linea_files: df_filtered shape: {df_filtered.shape}, ordered_prefixes: {ordered_prefixes}")
    
    # Mappa prefisso -> { 'normal': line_num }
    prefix_to_line_numbers = {}
    next_line_number = 1
    carousel_line_created = False

    for prefix in ordered_prefixes:
        # Crea DbiLine per linea normale
        filename_normal = f"DbiLine{next_line_number}.db"
        with open(os.path.join(linee_folder, filename_normal), 'w') as f:
            f.write(f"""DATA_BLOCK \"DbiLine{next_line_number}\"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
\"LINE\"

BEGIN

END_DATA_BLOCK
""")
        print(f"DEBUG - File DbiLine{next_line_number}.db creato: {os.path.join(linee_folder, filename_normal)}")
        line_type_mapping[next_line_number] = 'Normale'
        prefix_to_line_numbers[prefix] = {'normal': next_line_number}
        normal_line_num = next_line_number
        next_line_number += 1

        # Verifica caroselli per questo prefisso con subset robusto
        prefix_subset = df_filtered[df_filtered['ITEM_ID_CUSTOM'].str.lower().str.startswith(prefix.lower())]
        has_carousel_for_prefix = False
        if not prefix_subset.empty:
            # Conta occorrenze di 'CA' (case insensitive) nella stringa
            carousel_mask = prefix_subset['ITEM_ID_CUSTOM'].str.upper().str.count('CA') == 2
            has_carousel_for_prefix = carousel_mask.any()
            if has_carousel_for_prefix:
                carousel_items = prefix_subset[carousel_mask]['ITEM_ID_CUSTOM'].tolist()
                print(f"DEBUG - Prefix {prefix}: normal LINE {normal_line_num}, has_carousel={has_carousel_for_prefix}, carousel_items={carousel_items}")
            else:
                print(f"DEBUG - Prefix {prefix}: normal LINE {normal_line_num}, has_carousel={has_carousel_for_prefix}, NO carousels found (total items: {len(prefix_subset)})")
                print(f"DEBUG - Prefix {prefix}: sample items: {prefix_subset['ITEM_ID_CUSTOM'].head(5).tolist()}")
        else:
            print(f"DEBUG - Prefix {prefix}: normal LINE {normal_line_num}, has_carousel={has_carousel_for_prefix}, NO ITEMS FOUND for prefix")

        # Crea DbiLineCarousel una sola volta se ci sono caroselli in qualsiasi prefisso
        if has_carousel_for_prefix and not carousel_line_created:
            filename_carousel = "DbiLineCarousel.db"
            with open(os.path.join(linee_folder, filename_carousel), 'w') as f:
                f.write(f"""DATA_BLOCK \"DbiLineCarousel\"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
\"LINE\"

BEGIN

END_DATA_BLOCK
""")
            print(f"DEBUG - File DbiLineCarousel.db creato: {os.path.join(linee_folder, filename_carousel)}")
            line_type_mapping['Carousel'] = 'Carousel'
            carousel_line_created = True

    print(f"DEBUG - line_type_mapping finale: {line_type_mapping}")
    return prefix_to_line_numbers

def get_next_line_number(linee_folder):
    """
    Restituisce il primo numero libero per un nuovo file DbiLine# nella cartella specificata.
    """
    existing_line_files = [f for f in os.listdir(linee_folder) if f.startswith("DbiLine") and f.endswith(".db")]
    used_numbers = set()
    for f in existing_line_files:
        try:
            n = int(f.replace("DbiLine", "").replace(".db", ""))
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

    if "ST" in item_id.upper() or "CN" in item_id.upper() or "CX" in item_id.upper():
        raw_num = item_data.get('GlobalUtenzaNumber')
        if raw_num is not None:
            try:
                number_int = int(raw_num)
                formatted_name = f"Utenza{number_int}_{item_id}"
            except (ValueError, TypeError):
                print(f"Attenzione (_get_item_details): Impossibile convertire utenza_number '{raw_num}' in int per {item_id}. Uso fallback nome.")
                formatted_name = f"Utenza_ERR_{index_fallback}"
                number_int = None # Reset number if conversion failed
        else:
            # Fallback se GlobalUtenzaNumber non trovato
            number_int = index_fallback 
            formatted_name = f"Utenza{number_int}_{item_id}"
    elif count_ca_occurrences(item_id) == 2:
        raw_num = item_data.get('GlobalCarouselNumber')
        if raw_num is not None:
            try:
                number_int = int(raw_num)
                formatted_name = f"Carousel{number_int}"
            except (ValueError, TypeError):
                print(f"Attenzione (_get_item_details): Impossibile convertire carousel_number '{raw_num}' in int per {item_id}. Uso fallback nome.")
                formatted_name = f"Carousel_ERR_{index_fallback}"
                number_int = None
        else:
            number_int = index_fallback
            formatted_name = f"Carousel{number_int}"
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
    return ("ST" in item_id.upper() or "CN" in item_id.upper() or "CX" in item_id.upper() or count_ca_occurrences(item_id) == 2)

def create_main_file(trunk_number, valid_items, output_folder, last_valid_prev_item_data=None, first_valid_next_item_data=None, trunk_to_line_mapping=None, datalogic_counter=1):
    """
    Crea il file MAINx per un tronco specifico.
    
    Args:
        trunk_number (int): Numero del tronco
        valid_items (list): Lista di elementi nel tronco (dizionari)
        output_folder (str): Cartella di output
        last_valid_prev_item_data (dict, optional): Dati dell'ultimo item valido del tronco precedente.
        first_valid_next_item_data (dict, optional): Dati del primo item valido del tronco successivo.
        datalogic_counter (int): Contatore globale per i Datalogic (parte da 1)
    
    Returns:
        int: Il valore aggiornato del contatore Datalogic
    """
    content = []
    
    # Gestisci trunk_number "Carousel" invece di numero
    if isinstance(trunk_number, str) and trunk_number == "Carousel":
        safe_trunk_number = 0
        trunk_num_formatted = "Carousel"
        trunk_display_name = "Carousel"
    else:
        try:
            safe_trunk_number = int(trunk_number)
            trunk_num_formatted = f"{safe_trunk_number:02d}"
            trunk_display_name = trunk_number
        except (ValueError, TypeError):
            print(f"Attenzione create_main_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
            safe_trunk_number = 0
            trunk_num_formatted = "00"
            trunk_display_name = trunk_number
    
    # Aggiungi l'intestazione della funzione - struttura API004_NEW
    content.append(f'FUNCTION "MAIN{trunk_display_name}" : Void')
    content.append('{ S7_Optimized_Access := \'TRUE\' }')
    content.append('VERSION : 0.1')
    content.append('   VAR_INPUT ')
    content.append('      GlobalData : "GlobalData";')
    content.append('      TimeData : "TimeData";')
    content.append('      Constants : "Constants";')
    content.append('   END_VAR')
    content.append('')
    content.append('   VAR_IN_OUT ')
    content.append('      TrunkInterface : "COM_TRUNK-USE";')
    content.append('   END_VAR')
    content.append('')
    content.append('   VAR_TEMP ')
    content.append('      StartTronco : Bool;')
    content.append('   END_VAR')
    content.append('')
    content.append('')
    content.append('BEGIN')
    content.append('	')
    content.append('	')
    
    # Contatori per elementi FD e SD
    fd_counter = 1
    # datalogic_counter viene passato come parametro e viene incrementato durante l'elaborazione
    oversize_counter = 1

    # Aggiungi la sezione di gestione richiesta start tronco
    content.append('	REGION Gestione Richiesta Start Tronco')
    content.append('	    ')
        
    associated_line_num = trunk_to_line_mapping.get(safe_trunk_number, 1) if trunk_to_line_mapping else 1

    # Per Carousel, usa un riferimento speciale
    if trunk_num_formatted == "Carousel":
        content.append(f'	    IF #GlobalData.Start_All OR')
        content.append(f'	        #GlobalData.StartTronco0 OR')
        content.append(f'	        "DbiTrunkLNCarousel".StartReqAutoFp')
    else:
        content.append(f'	    IF #GlobalData.Start_All OR')
        content.append(f'	        #GlobalData.StartTronco{safe_trunk_number} OR')
    content.append(f'	        "DbiTrunkLN{trunk_num_formatted}".StartReqAutoFp')
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
        elif "ST" in item_id_upper or "CN" in item_id_upper or "CX" in item_id_upper:
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
        # Se il nome formattato inizia con "Carousel", usa sempre ".Carousel" invece di ".Conveyor"
        if prev_name_formatted and prev_name_formatted.startswith("Carousel"):
            prev_component_type = "Carousel"
        if prev_component_type == "Conveyor":
            prev_name_ref = (f'"{prev_name_formatted}"."{prev_component_type}".Data.OUT' if prev_item_data_to_use else '#GlobalData.EmptyUser')
        else:
            prev_name_ref = (f'"{prev_name_formatted}".{prev_component_type}.Data.OUT' if prev_item_data_to_use else '#GlobalData.EmptyUser')

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
        # Se il nome formattato inizia con "Carousel", usa sempre ".Carousel" invece di ".Conveyor"
        if next_name_formatted and next_name_formatted.startswith("Carousel"):
            next_component_type = "Carousel"
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
            next_carousel_num_for_side = next_number if next_number is not None else 0
            next_name_ref = f'"SIDE_INPUT_CAROUSEL{next_carousel_num_for_side}".DATA.OUT'
        else:
            if next_component_type == "Conveyor":
                next_name_ref = f'"{next_name_formatted}"."{next_component_type}".Data.OUT' if next_item_data_to_use else "NULL"
            else:
                next_name_ref = f'"{next_name_formatted}".{next_component_type}.Data.OUT' if next_item_data_to_use else "NULL"
        
        # Se è un Datalogic (contiene SC), aggiungi la configurazione specifica
        if component_type == "Datalogic":
            # Trova l'utenza precedente valida
            prev_utenza = None
            for j in range(i-1, -1, -1):
                prev_item = valid_items[j]
                prev_id = prev_item.get('ITEM_ID_CUSTOM', '')
                if 'ST' in prev_id.upper() or 'CN' in prev_id.upper() or 'CX' in prev_id.upper():
                    prev_utenza = prev_item
                    break
            
            if prev_utenza:
                # Usa _get_item_details per ottenere il nome completo formattato
                prev_utenza_name_formatted, _ = _get_item_details(prev_utenza, i)
                # Determine comment based on LC vs SC
                is_lc = "LC" in item_id_original.upper()
                comment_text = "ATR Bottom" if is_lc else "ATR 360"
                    
                content.append(f'	REGION Call Datalogic {comment_text} ({item_id_original})')
                content.append('	    ')
                content.append(f'	    "Datalogic_{item_id_original}"(')
                content.append('	                          TimeData := "DbGlobale".TimeData,')
                content.append('	                          Constants := "DbConstants".Constants,')
                content.append(f'	                          Trk := "{prev_utenza_name_formatted}".Conveyor.Trk,')
                content.append(f'	                          PANYTO_SA := "SV_DB_DATALOGIC_SA".DATALOGIC[{datalogic_counter}],')
                content.append(f'	                          PANYTO_CMD := "SV_DB_DATALOGIC_CMD".DATALOGIC[{datalogic_counter}],')
                content.append('	                          DB_OBJ := "DbsObject".DbObj[1],')
                content.append('	                          "Ist-McpChmMsgBuffer":= "DbiChmMsgBuffer",')
                content.append('	                          "Ist-McpChrMsgBuffer":= "DbiChrMsgBuffer",')
                content.append('	                          "Ist-McpCreateChmMsg":= "DbiMcpCreateChmMsg",')
                content.append('	                          "Ist-McpCreateChrMsg":="DbiMcpCreateChrMsg",')
                content.append('	                          "Ist-McpCreateTrkEventChrMsg":="DbiMcpCreateTrkEventChrMsg",')
                content.append('	                          "Ist-PcSocket":= "DbiPcSocket",')
                content.append('	                          "Ist-VidGenerator":="DbiVidGenerator");')
                content.append('	    ')
                content.append('	END_REGION')
                content.append('	')
                datalogic_counter += 1
            continue  # Salta il resto della logica per i Datalogic
        
        # Se contiene SD, gestisci come SHUTTER
        if component_type == "SHUTTER":
            shutter_num = current_number if current_number is not None else 0 # Use global shutter number
            content.append(f"	REGION Call SHUTTER ({item_id_original})")
            content.append(f'	    "SHUTTER{shutter_num}".Data.CMD := "DbSvShutterCmd".SHUTTER[{shutter_num}];')
            content.append(f'	    "SHUTTER{shutter_num}"(PANYTOSHUTTER_SA := "DbSvShutterSa".SHUTTER[{shutter_num}],')
            content.append(f'	                     PREV := {prev_name_ref},')
            content.append(f'	                     NEXT := {next_name_ref},')
            content.append(f'	                     InterfaceTrunkUse := "DbiTrunkLN{trunk_num_formatted}".ComTrunkUse,')
            content.append(f'	                     GlobalData := "DbGlobale".GlobalData);')
            content.append("	END_REGION")
            content.append('	')
            continue  # Salta la generazione delle altre regioni per questo elemento
        
        # Se contiene FD, gestisci come FIRESHUTTER
        if component_type == "FIRESHUTTER":
            content.append(f"	REGION Call FIRESHUTTER ({item_id_original})")
            content.append('	    ')
            content.append(f'	    "FIRESHUTTER{fd_counter}"(InterfaceTrunkuse := "DbiTrunkLN{trunk_num_formatted}".ComTrunkUse,')
            content.append(f'	                   SV_FIRESHUTTER_CMD := "DbSvFireshutterCmd".FIRESHUTTER[{fd_counter}],')
            content.append(f'	                   SV_FIRESHUTTER_SA := "DbSvFireshutterSa".FIRESHUTTER[{fd_counter}]);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            fd_counter += 1  # Incrementa il contatore solo per elementi FD
            continue  # Salta la generazione delle altre regioni per questo elemento
            
        # Se contiene OG, gestisci come OVERSIZE
        if component_type == "OVERSIZE":
            content.append(f"	REGION Call OVERSIZE ({item_id_original})")
            content.append(f'	    "Oversize{oversize_counter}"(ID:=0,')
            content.append(f'	                InterfaceTrunkUse := "DbiTrunkLN{trunk_num_formatted}".ComTrunkUse,')
            content.append(f'	                PANYTO_SA := "DbSvOversizeSa".OVERSIZE[{oversize_counter}],')
            content.append(f'	                PANYTO_CMD := "DbSvOversizeCmd".OVERSIZE[{oversize_counter}]);')
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
            
            # PREV: riferimento a Side_Input_Carousel
            carousel_prev_ref = f'"Side_Input_Carousel{current_number if current_number is not None else 0}".DATA.OUT' # Usa current_number per Side_Input_Carousel
            content.append(f'	              PREV := {carousel_prev_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'	              NEXT := {next_name_ref},')
                 
            content.append('	              START := #StartTronco,')
            content.append('	              TimeData := "DbGlobale".TimeData,')
            content.append('	              Constants := "DB_Constants".Constants,')
            content.append('	              GlobalData := "DbGlobale".GlobalData,) # Aggiunto DB_Globale')
            content.append(f'	              InterfaceTrunkUse := "DbiTrunkLN{trunk_num_formatted}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'	              PANYTOCNV_SA := "DbSvCarouselSa".CAROUSEL[{panytocnv_num_to_use}],') # Usa DbSvCarouselSa
            content.append(f'	              PANYTOCNV_CMD := "DbSvCarouselCmd".CAROUSEL[{panytocnv_num_to_use}],') # Usa DbSvCarouselCmd

            content.append('	              DB_OBJ := "DBsObject".DbObj[1],')
            content.append('	              "Ist-VidGenerator" := "Ist_Sub_VidGenerator",')
            content.append('	              EncoderInterface := #TempEncoderNotUsed,')
            # Drive per Carousel - verifica se ci sono 2 o 3 motori (CA CA = 2 motori, CA CA CA = 3 motori)
            ca_count = count_ca_occurrences(item_id_original)
            content.append(f'	              Drive_1 := "{item_id_original}".Drive_1,') 
            content.append(f'	              Drive_2 := "{item_id_original}".Drive_2,')
            if ca_count >= 3:
                content.append(f'	              Drive_3 := "{item_id_original}".Drive_3,')

            content.append('	              "Ist-McpCreateChrMsg" := "Ist_Gtw_McpCreateChrMsg",')
            content.append('	              "Ist-PcSocket" := "Ist_Gtw_PcSocket",')
            content.append('	              "Ist-McpChrMsgBuffer" := "Ist_Gtw_MsgBuffer",')
            content.append('	              "Ist-LogBuffer" := "Ist_GstLogBuffer",')
            content.append('	              "Ist-Logger" := "Ist_GstLogger");')
            content.append('	    ')
            # Usa DbiLineCarousel se la linea è carousel
            line_ref = "DbiLineCarousel" if associated_line_num == 'Carousel' else f"DbiLine{associated_line_num}"
            content.append(f'	            "Carousel{carousel_id}_Full_Timeout"(PrevLineRunning:="{line_ref}".Data.SA.ST_RUN,')
            content.append('	                                     LapsBeforeStopping:=1,')
            content.append('	                                     WindowLengthFromBooking:=7.0,')
            content.append(f'	                                     Carousel :="Carousel{carousel_id}".Carousel);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            # --- Fine Chiamata CAROUSEL ---
            
        elif component_type == "Conveyor":
            # --- Generazione Chiamata CONVEYOR/Utenza (standard) - struttura API004_NEW ---
            content.append(f"\tREGION Call CONVEYOR_SEW_MOVIGEAR ({item_id_original})")
            content.append('	    ')
            content.append(f'	    "{current_name}"(START := #StartTronco,')
            
            # PREV: riferimento a item precedente effettivo (gestito sopra da prev_name_ref)
            content.append(f'	              PREV := {prev_name_ref},') 

            # NEXT: riferimento a item successivo effettivo (USA LA next_name_ref CALCOLATA SOPRA)
            content.append(f'	              NEXT := {next_name_ref},')

            content.append('	                        TimeData := #TimeData,')
            content.append('	                        Constants := #Constants,')
            content.append('	                        TrunkInterface := #TrunkInterface,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'	                        SupervisionSa := "SV_DB_CONVEYOR_SA".CONVEYOR[{panytocnv_num_to_use}],')
            content.append(f'	                        SupervisionCmd := "SV_DB_CONVEYOR_CMD".CONVEYOR[{panytocnv_num_to_use}],')
            content.append('	                        ObjectsTable := "DbsObject".DbObj);')
            content.append('	    ')
            content.append("	END_REGION")
            content.append('	')
            # --- Fine Chiamata CONVEYOR/Utenza ---
            
        # --- Logica SIDE_INPUT (Spostata DOPO la chiamata del blocco i) ---
        # Se il prossimo elemento EFFETTIVO è un carousel, aggiungi la sua configurazione SIDE_INPUT
        if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
             side_input_carousel_num = next_number if next_number is not None else 0 
             next_carousel_id = next_item_data_to_use.get('ITEM_ID_CUSTOM', '')
             
             # Crea il file Side_Input_Carousel nella cartella API0##
             utenze_folder = output_folder
             create_side_input_file(side_input_carousel_num, utenze_folder)
             
             content.append(f"\tREGION Call SIDE INPUT for Carousel{side_input_carousel_num} ({next_carousel_id})")
             content.append("\t    // il side input si inserisce prima di un carosello , nel tronco precedente al carosello")
             
             # PREV per Side_Input_Carousel è l'output dell'elemento CORRENTE (blocco appena generato)
             current_output_ref = f'"{current_name}".{component_type}.Data.OUT'
             content.append(f'	    "Side_Input_Carousel{side_input_carousel_num}"(PREV := {current_output_ref},')
             
             next_carousel_name_for_next = f"Carousel{side_input_carousel_num}"
             content.append(f'	                         NEXT := "{next_carousel_name_for_next}".Carousel.Data.OUT,')
             content.append('	                         NextObjTransferIn := FALSE,')
             content.append('	                         NextObjTransferInAboutToStart := FALSE,')
             
             # Formatta item_id_original per FTU_Conveyor
             formatted_item_id_for_ftu = item_id_original
             if "ST" in item_id_original:
                 formatted_item_id_for_ftu = item_id_original.replace("ST", "_ST", 1)
             elif "CN" in item_id_original:
                 formatted_item_id_for_ftu = item_id_original.replace("CN", "_CN", 1)
             elif "CX" in item_id_original:
                 formatted_item_id_for_ftu = item_id_original.replace("CX", "_CX", 1)

             
             
             # PrevFullStatus usa lo stato dell'elemento CORRENTE
             current_full_status_ref = current_output_ref.replace(".Data.OUT", ".Data.SA.ST_FULL")
             content.append(f'	                         PrevFullStatus := {current_full_status_ref},')
             
             content.append(f'	                         Prev2FullStatus := "{next_carousel_name_for_next}".Carousel.Data.SA.ST_FULL,')
             content.append(f'	                         TrunkPrevAutomaticStatus := "DbiTrunkLN{trunk_num_formatted}".Data.SA.ST_AUTOMATIC,')
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
    if isinstance(trunk_number, str) and trunk_number == "Carousel":
        output_filename = "MAINCarousel.scl"
    else:
        output_filename = f"MAIN{safe_trunk_number}.scl"
    output_path = os.path.join(output_folder, output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("\n".join(content))
    
    # Restituisci il contatore aggiornato
    return datalogic_counter

def create_trunk_file(trunk_number, output_folder):
    """
    Crea un file DATA_BLOCK per un tronco specifico.
    
    Args:
        trunk_number (int o str): Numero del tronco o "Carousel"
        output_folder (str): Cartella di destinazione
    """
    # Gestisci trunk_number "Carousel" invece di numero
    if isinstance(trunk_number, str) and trunk_number == "Carousel":
        safe_trunk_number = 0
        trunk_num_formatted = "Carousel"
        trunk_filename = "DbiTrunkLNCarousel.db"
    else:
        try:
            safe_trunk_number = int(trunk_number)
            trunk_num_formatted = f"{safe_trunk_number:02d}"
            trunk_filename = f"DbiTrunkLN{trunk_num_formatted}.db"
        except (ValueError, TypeError):
            print(f"Attenzione create_trunk_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
            safe_trunk_number = 0
            trunk_num_formatted = "00"
            trunk_filename = "DbiTrunkLN00.db"
    
    # Contenuto del file TRUNK
    trunk_content = f"""DATA_BLOCK "DbiTrunkLN{trunk_num_formatted}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.4
NON_RETAIN
"TRUNK-PCT"

BEGIN

END_DATA_BLOCK
"""
    
    # Crea la directory se non esiste
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Elimina file .scl vecchio se esiste
    old_scl_filename = trunk_filename.replace('.db', '.scl')
    old_scl_path = os.path.join(output_folder, old_scl_filename)
    if os.path.exists(old_scl_path):
        try:
            os.remove(old_scl_path)
            print(f"DEBUG - Rimosso file vecchio: {old_scl_filename}")
        except Exception as e:
            print(f"DEBUG - Impossibile rimuovere {old_scl_filename}: {e}")
    
    # Scrivi il file
    with open(os.path.join(output_folder, trunk_filename), 'w') as trunk_file:
        trunk_file.write(trunk_content) 

def create_main_structure_file(output_folder, num_lines, selected_cab_plc, trunks_per_line, ordered_prefixes, carousel_trunk_position=None):
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
        carousel_trunk_position (int, optional): Posizione del tronco Carousel (es. 14)
    """
    print(f"Creazione file Main.scl (OB) con {num_lines} linee per CAB_PLC {selected_cab_plc}...")
    print(f"Tronchi per linea: {trunks_per_line}")
    print(f"Prefissi ordinati: {ordered_prefixes}")
    
    # Calcola i range di numeri MAIN per ogni linea
    main_ranges = []
    current_main = 1
    for num_trunks in trunks_per_line:
        main_ranges.append((current_main, current_main + num_trunks - 1))
        current_main += num_trunks
    
    print(f"Range MAIN per linea: {main_ranges}")
    
    # Crea mappatura di scalatura per i MAIN dopo il Carousel
    total_main_count = sum(trunks_per_line)
    main_number_mapping = {}
    for main_idx in range(1, total_main_count + 1):
        if carousel_trunk_position is not None and main_idx == carousel_trunk_position:
            main_number_mapping[main_idx] = "Carousel"
        elif carousel_trunk_position is not None and main_idx > carousel_trunk_position:
            main_number_mapping[main_idx] = main_idx - 1  # Scala di 1
        else:
            main_number_mapping[main_idx] = main_idx  # Mantieni originale
    
    # Intestazione Organization Block - struttura API004_NEW
    content = [
        'ORGANIZATION_BLOCK "Main"',
        '{ S7_Optimized_Access := \'TRUE\' }',
        'VERSION : 0.1',
        '   VAR_TEMP ',
        '      ReturnValue : Int;',
        '      OBDateTime : Date_And_Time;',
        '      StartTronco : Bool;',
        '   END_VAR',
        '',
        '',
        'BEGIN',
        '	        ',
        '	        ',
        '	        (*=====================================================================',
        '         Leonardo Company S.p.A',
        '         (c)Copyright 2024 All Rights Reserved',
        '        ----------------------------------------------------------------------',
        '         Library: Master-Nastri',
        '         Engineering: TIA19',
        '         Tested with: ',
        '         Restrictions: -',
        '         Requirements: -',
        '         Functionality: ',
        '        ----------------------------------------------------------------------',
        '         Change log table:',
        '         List of Autor: MS - Matteo Stefani, Lorenzo Urbano',
        '         Version   Date        Autor   Changes applied',
        '         01.00     03-03-2025  MS-LU   New Master Versioning ',
        '         02.00     13-11-2025  MS      Updated with Master conveyor 01.00',
        '        =====================================================================*)',
        '    ',
        '    ',
        '    #ReturnValue := RD_SYS_T(#OBDateTime);',
        '',
        'REGION Time management',
        '    "DbTimeMng"(OBDateTime := #OBDateTime,',
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
        '                 GlobalData:="DbGlobale".GlobalData,',
        '                 SynchroData:="DbGlobale".SynchroData,',
        '                 TimeData:="DbGlobale".TimeData);',
        'END_REGION',
        '',
        'REGION Library constants',
        '    "CONST"("DbConstants".Constants);',
        'END_REGION',
        '',
        'REGION Configuration',
        '    "CONF"();',
        'END_REGION',
        '',
        'REGION Input signals update',
        '    "DigIn"();',
        'END_REGION',
        '',
        'REGION Eth-Communications',
        '    "DbiLogger"(mSecWeek := "DbGlobale".TimeData.mSecWeek,',
        '                CycleTime := "DbGlobale".TimeData.CycleTime,',
        '                StartUpPlcFlag := "DbGlobale".GlobalData.StartUpPlcFlag,',
        '                DbiLogBuffer := "DbiLogBuffer");',
        '',
        '    "DbiPcSocket"(StartUpPlcFlag := "DbGlobale".GlobalData.StartUpPlcFlag,',
        '                  "GtwConfiguration" := "DbGtwConfiguration".GtwConfiguration,',
        '                  TimeData := "DbGlobale".TimeData,',
        '                  SynchroData := "DbGlobale".SynchroData,',
        '                  HmiGatewayRd := "DbHmiGatewayRd",',
        '                  HmiGatewayWr := "DbHmiGatewayWr",',
        '                  DbiChmMsgBuffer := "DbiChmMsgBuffer",',
        '                  DbiChrMsgBuffer:="DbiChrMsgBuffer",',
        '                  DbiChmMsgBufferRetry:="DbiChmMsgBufferRetry",',
        '                  DbiChrMsgBufferRetry:="DbiChrMsgBufferRetry",',
        '                  DbiGtwCreateAckMsg:="DbiCreateAckMsg",',
        '                  DbiDbGtwConfiguration:="DbGtwConfiguration");',
        'END_REGION',
        '',
        'REGION Line and pushbuttons panel management',
        '    "GenLine"();',
        '    "PulsLine"();',
        'END_REGION',
        '',
        'REGION Panels management',
        '    "DbiPanel1"(PANYTO_SA := "DbSvPanelSa".MCP1,',
        '             PANYTO_CMD := "DbSvPanelCmd".MCP1);  ',
        'END_REGION',
        '',
        'REGION Profibus/Profinet nodes faults managment',
        '    // Abilitazione area di diagnostica per supervisione',
        '    "SV_DB_PROFINET_SA".Profinet1On := TRUE;',
        '    "SV_DB_PROFINET_SA".Profibus1On := FALSE;',
        '    "SV_DB_PROFINET_SA".Profibus2On := FALSE;',
        '',
        '    "DbiNetAlm1"(LADDR := 257,',
        '               ERROR =>"SV_DB_PROFINET_SA".FaultProfinet1,',
        '               FAULT =>"SV_DB_PROFINET_SA".StAvr1PN);',
        '    "DbiNetAlm2"();',
        '    "DbiNetAlm3"();',
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
            # Usa la mappatura per ottenere il numero scalato o "Carousel"
            main_mapped = main_number_mapping.get(main_num, main_num)
            
            if main_mapped == "Carousel":
                main_name = "Carousel"
                trunk_num_formatted = "Carousel"
            else:
                main_name = main_mapped
                trunk_num_formatted = f"{main_mapped:02d}"
            
            content.append(f'    "MAIN{main_name}"(GlobalData:="DbGlobale".GlobalData,')
            content.append(f'                TimeData:="DbGlobale".TimeData,')
            content.append(f'                Constants:="DbConstants".Constants,')
            content.append(f'                TrunkInterface:="DbiTrunkLN{trunk_num_formatted}".ComTrunkUse);')
            content.append('')
        
        content.append('END_REGION')
        content.append('')

    # Aggiungi il resto della struttura
    content.extend([
        'REGION Output signals update',
        '    "DigOut"();',
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
        'REGION Version',
        '    "V_Major" := "PlcSwVersion".MAJOR;',
        '    "V_Minor" := "PlcSwVersion".MINOR;',
        '    "V_Patch" := "PlcSwVersion".PATCH;',
        'END_REGION',
        '',
        'REGION Alarm Compactor for HMI',
        '    "AlarmsCompactHMI"();',
        'END_REGION ;',
        '',
        'REGION SCADA',
        '    ',
        'END_REGION',
        '',
        'REGION Time management',
        '    "DbTimeMng"(OBDateTime := #OBDateTime,',
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
        '                 GlobalData := "DbGlobale".GlobalData,',
        '                 SynchroData := "DbGlobale".SynchroData,',
        '                 TimeData := "DbGlobale".TimeData);',
        'END_REGION',
        '',
        ''
    ])

    # Aggiungi END_ORGANIZATION_BLOCK alla fine
    content.append('')
    content.append('')
    content.append('')
    content.append('END_ORGANIZATION_BLOCK')
    content.append('')

    # Crea il percorso completo includendo il CAB_PLC - all files in API0## folder
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_path = os.path.join('Configurazioni', selected_cab_plc, api_folder, 'Main.scl')
    print(f"Percorso file: {os.path.abspath(output_path)}")
    
    # Crea la cartella se non esiste
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Cartella creata/verificata: {os.path.exists(os.path.dirname(output_path))}")
    
    try:
        with open(output_path, 'w') as f:
            f.write('\n'.join(content))
        print(f"File Main.scl creato con successo in: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Errore durante la creazione del file: {e}")
        
    print("File Main.scl creato con successo!") 

def create_conf_file(selected_cab_plc, df, output_folder, order, prefix_to_line_numbers=None, carousel_trunk_position=None):
    """
    Crea il file CONF.scl con le configurazioni dei trunk e delle linee.
    
    Args:
        selected_cab_plc (str): CAB_PLC selezionato
        df (DataFrame): DataFrame con i dati
        output_folder (str): Cartella di output
        order (list): Lista dell'ordine selezionato dall'utente
    """
    content = []
    
    # Intestazione della funzione - struttura API004_NEW
    content.append('FUNCTION "CONF" : Void')
    content.append('{ S7_Optimized_Access := \'TRUE\' }')
    content.append('VERSION : 0.1')
    content.append('   VAR_TEMP ')
    content.append('      RetVal : Int;')
    content.append('      ZeroWord : Word;')
    content.append('   END_VAR')
    content.append('')
    content.append('')
    content.append('BEGIN')
    content.append('	    REGION Initialization')
    content.append('	        #ZeroWord := W#16#0;')
    content.append('	    END_REGION')
    content.append('	    ')
    
    # Regione di configurazione generale
    content.append('	    REGION General Configuration')
    content.append('	        "DbGlobale".GlobalData.MachineId := 4;')
    content.append('	    END_REGION')
    content.append('	    ')
    
    # Regione di configurazione PANEL1 - struttura API004_NEW
    content.append('	    REGION Config DbiPanel1 ()')
    content.append('        ')
    content.append('        "DbiPanel1".Data.CNF.TIME_SIL := L#20000;    // L#20000;')
    content.append('        ')
    content.append('	        //Posso lasciare tutto a false, al limite custom per SCADA da vedere a posteriori')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL1 := TRUE;       //  -> Sono a gruppi di 20 allarmi da Signal1 a Signal20')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL2 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL3 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL4 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL5 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL6 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL7 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL8 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL9 := FALSE;      // FALSE;')
    content.append('	        "DbiPanel1".Data.CNF.BLOCK_ALL10 := FALSE;      // FALSE;')
    content.append('	        ')
    content.append('	        //Profinet alarms CNF')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[1] := 250; //  Main Ring Manager')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[2] := 3; //    HMI Panel')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[3] := 2; //    I/O Interface Module')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[4] := 11; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[5] := 12; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[6] := 13; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[7] := 14; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[8] := 15; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[9] := 16; //   Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[10] := 17; //  Straight Conveyor')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[11] := 18; //  Carousel')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[12] := 19; //  Carousel')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[13] := 20; //  ATR Datalogic')
    content.append('	        //Essendo che gli allarmi sono a gruppi di 20, devono essere valorizzati tutti e 20, per questo si mette lo stesso nodo del controller per evitare indice 0')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[14] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[15] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[16] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[17] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[18] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[19] := 1; //  Controller')
    content.append('	        "DbiPanel1".Data.CNF.PROFINET_NODE_BY_SIGNALS[20] := 1; //  Controller')
    content.append('	        ')
    content.append('	    END_REGION')
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
    
    # Crea mappatura di scalatura per i tronchi dopo il Carousel
    # Prima conta quanti tronchi ci sono in totale per creare la mappatura
    total_trunks_count = 0
    for line_prefix in unique_lines:
        if 'ITEM_LINE' in df.columns:
            line_trunks = sorted(df[df['ITEM_LINE'] == line_prefix]['ITEM_TRUNK'].unique())
        else:
            line_trunks = sorted(df[df['ITEM_ID_CUSTOM'].str.lower().str.startswith(line_prefix.lower())]['ITEM_TRUNK'].unique())
        total_trunks_count += len(line_trunks)
    
    # Crea mappatura: se carousel_trunk_position = 14, allora:
    # - Tronchi 1-13: rimangono 1-13
    # - Tronco 14: diventa "Carousel"
    # - Tronco 15: diventa 14
    # - Tronco 16: diventa 15
    conf_trunk_mapping = {}
    for trunk_idx in range(1, total_trunks_count + 1):
        if carousel_trunk_position is not None and trunk_idx == carousel_trunk_position:
            conf_trunk_mapping[trunk_idx] = "Carousel"
        elif carousel_trunk_position is not None and trunk_idx > carousel_trunk_position:
            conf_trunk_mapping[trunk_idx] = trunk_idx - 1  # Scala di 1
        else:
            conf_trunk_mapping[trunk_idx] = trunk_idx  # Mantieni originale
    
    # Per ogni linea nell'ordine selezionato
    for line_idx, line_prefix in enumerate(unique_lines, 1):
        print(f"\nDEBUG - Elaborazione Linea {line_idx} con prefisso {line_prefix}")
        
        # Determina se questa linea ha una linea carousel
        line_ref = None
        if prefix_to_line_numbers and line_prefix in prefix_to_line_numbers:
            line_info = prefix_to_line_numbers[line_prefix]
            # Controlla se questa linea ha una linea carousel
            carousel_line_num = line_info.get('carousel')
            normal_line_num = line_info.get('normal')
            # Se c'è una linea carousel per questo prefisso, usa quella per la configurazione quando appropriato
            # Per ora usa sempre la linea normale
            if normal_line_num:
                line_ref = f"DbiLine{normal_line_num}"
            # Se questa è la linea carousel, usa DbiLineCarousel
            if carousel_line_num == 'Carousel':
                # Verifica se stiamo processando la linea carousel
                # Per ora manteniamo la logica originale
                pass
        else:
            # Fallback: usa line_idx
            line_ref = f"DbiLine{line_idx}"
        
        # Regione di configurazione della linea
        content.append(f'    REGION Conf Line {line_idx}')
        content.append(f'        "{line_ref}".Data.CNF.T_PRESTART_RES := L#5000;')
        content.append(f'        "{line_ref}".Data.CNF.T_SRNAVR := L#3000;')
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
                if ('ST' in item_id or 'CN' in item_id or 'CX' in item_id) and 'SC' not in item_id and item_id.count('CA') != 2:
                    total_conveyors += 1
                    print(f"DEBUG - Trovata utenza valida: {item_id}")
            
            print(f"DEBUG - Total conveyors calcolato: {total_conveyors}")
            
            # Usa la mappatura per ottenere il numero scalato o "Carousel"
            trunk_mapped = conf_trunk_mapping.get(global_trunk_counter, global_trunk_counter)
            
            # Regione di configurazione del trunk
            if trunk_mapped == "Carousel":
                trunk_num_formatted = "Carousel"
                trunk_display = "Carousel"
            else:
                trunk_num_formatted = f"{trunk_mapped:02d}"
                trunk_display = trunk_mapped
            
            content.append(f'    REGION Conf Trunk {trunk_display} Line {line_idx}')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.PRESTART_TIMER := T#10S;     // Prestart Time [ms]')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.ENGSAV_TIMER := T#5S;        // Disable trunk time [ms]')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.SEGN_RESTART_PCT := TRUE;    // TRUE=Signal Restart after reset from PCT')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.SEGN_RESTART := TRUE;        // TRUE=Signal Restart')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.SEGN_REMG := TRUE;           // TRUE=reset emergency also the warning')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.TOT_CONVEYORS := {total_conveyors};         // Total number of conveyors in trunk')
            content.append(f'        "DbiTrunkLN{trunk_num_formatted}".Data.CNF.EN_FULL_ALLCONV := FALSE;    // TRUE=all conveyors of trunk are full then trunk is full, FALSE = atleast one conveyor of trunk is full then trunk is full')
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
            # Usa la stessa mappatura di scalatura creata sopra
            trunk_mapped_for_conf = conf_trunk_mapping.get(global_trunk_counter, global_trunk_counter)
            content.append(f'        "CONF_T{trunk_mapped_for_conf}"();')
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
    
    # LOG_ENABLE region removed as per requirements
    
    content.append('END_FUNCTION')
    
    # Salva il file
    output_path = os.path.join(output_folder, 'CONF.scl')
    with open(output_path, 'w') as f:
        f.write('\n'.join(content))
    
    print(f"DEBUG - File CONF.scl creato in {output_path}") 

def generate_gen_line_file(df, selected_cab_plc, line_type_mapping, ordered_prefixes, trunks_per_line, carousel_trunk_position=None):
    """
    Genera il file GEN_LINE.scl in base alle linee e ai trunk esistenti.
    Usa la stessa logica del MAIN.scl: associa i tronchi alle linee in sequenza progressiva.

    Args:
        df (DataFrame): DataFrame con i dati completi.
        selected_cab_plc (str): CAB_PLC selezionato.
        line_type_mapping (dict): Mappa dei numeri di linea ai loro tipi (es. 'Carousel').
        ordered_prefixes (list): Lista ordinata dei prefissi delle linee (es. ['CP11', 'CP12', ...]).
        trunks_per_line (list): Lista con il numero di tronchi per ogni linea (es. [11, 9, 4, 1, 1]).
        carousel_trunk_position (int, optional): Posizione del tronco Carousel (es. 14)
    """
    print(f"DEBUG - Generazione di GenLine.scl per {selected_cab_plc}...")
    
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    gen_line_content = []
    gen_line_content.append("FUNCTION \"GenLine\" : Void")
    gen_line_content.append("{ S7_Optimized_Access := 'TRUE' }")
    gen_line_content.append("VERSION : 0.1")
    gen_line_content.append("   VAR_TEMP ")
    gen_line_content.append("      StartTronco : Bool;")
    gen_line_content.append("      tempBool : Bool;")
    gen_line_content.append('   END_VAR')
    gen_line_content.append("")
    gen_line_content.append("")
    gen_line_content.append("BEGIN")
    gen_line_content.append("	")

    # Ordina i numeri di linea per assicurare un output consistente
    # Separa numeri e "Carousel"
    numeric_lines = [k for k in line_type_mapping.keys() if isinstance(k, int)]
    carousel_line = 'Carousel' if 'Carousel' in line_type_mapping else None
    sorted_line_numbers = sorted(numeric_lines)
    if carousel_line:
        sorted_line_numbers.append(carousel_line)

    # Genera le chiamate LINE
    for line_num in sorted_line_numbers:
        line_type = line_type_mapping.get(line_num, 'Normale')
        
        # Gestisci "Carousel" come nome invece di numero
        if line_num == 'Carousel':
            line_ref = "DbiLineCarousel"
            region_comment = "Call LINE Carousel"
            panyto_sa_ref = '"SV_DB_LINE_SA".LINE[Carousel]'
            panyto_cmd_ref = '"SV_DB_LINE_CMD".LINE[Carousel]'
        else:
            line_ref = f"DbiLine{line_num}"
            region_comment = f"Call LINE {line_num}"
            panyto_sa_ref = f'"SV_DB_LINE_SA".LINE[{line_num}]'
            panyto_cmd_ref = f'"SV_DB_LINE_CMD".LINE[{line_num}]'
        
        gen_line_content.append(f"\tREGION {region_comment}")
        gen_line_content.append("\t    ")
        gen_line_content.append(f"\t    \"{line_ref}\"(")
        gen_line_content.append("\t               TimeData := \"DbGlobale\".TimeData,")
        gen_line_content.append("\t               LMP_RUN => #tempBool,")
        gen_line_content.append("\t               LMP_AVR => #tempBool,")
        gen_line_content.append("\t               SRN_AVR => #tempBool,")
        gen_line_content.append(f"\t               PANYTO_SA := {panyto_sa_ref},")
        gen_line_content.append(f"\t               PANYTO_CMD := {panyto_cmd_ref});")
        gen_line_content.append("\t    ")
        gen_line_content.append("\tEND_REGION")
        gen_line_content.append("\t")

    # Ottieni tutti i trunk_numbers disponibili per il CAB_PLC corrente
    trunk_files = []
    api_folder = f'API0{selected_cab_plc[-2:]}'
    trunk_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    if os.path.exists(trunk_folder):
        trunk_files = [f for f in os.listdir(trunk_folder) if f.startswith("DbiTrunkLN") and f.endswith(".db")]
    
    # Gestisci sia numeri che "Carousel"
    trunk_numbers = []
    for f in trunk_files:
        trunk_name = f.replace("DbiTrunkLN", "").replace(".db", "")
        if trunk_name == "Carousel":
            trunk_numbers.append("Carousel")
        else:
            try:
                trunk_numbers.append(int(trunk_name))
            except ValueError:
                continue
    
    trunk_numbers = sorted([t for t in trunk_numbers if isinstance(t, int)]) + ([t for t in trunk_numbers if isinstance(t, str)])

    # Calcola i range di tronchi per ogni linea (stessa logica del MAIN.scl)
    trunk_ranges = []
    current_trunk = 1
    for num_trunks in trunks_per_line:
        trunk_ranges.append((current_trunk, current_trunk + num_trunks - 1))
        current_trunk += num_trunks
    
    print(f"DEBUG - Range tronchi per linea: {trunk_ranges}")
    print(f"DEBUG - trunks_per_line: {trunks_per_line}")
    
    # Crea mappatura tronco -> linea basata sulla sequenza progressiva
    trunk_to_line_map = {}
    for line_idx, (start_trunk, end_trunk) in enumerate(trunk_ranges, 1):
        for trunk_num in range(start_trunk, end_trunk + 1):
            trunk_to_line_map[trunk_num] = line_idx
    
    # Calcola il numero totale di tronchi (incluso il carousel) per determinare l'ID del carousel
    total_trunks_with_carousel = len(trunk_numbers)
    carousel_trunk_id = total_trunks_with_carousel
    
    # Se c'è un carousel, gestiscilo separatamente
    if carousel_trunk_position is not None:
        carousel_trunk_id = total_trunks_with_carousel

    # Per ogni trunk, genera le chiamate TRUNK
    for trunk_key in trunk_numbers:
        # Determina il numero del tronco
        if trunk_key == "Carousel":
            trunk_num = "Carousel"
            trunk_display = "Carousel"
            trunk_num_formatted = "Carousel"
            trunk_id_ref = str(carousel_trunk_id)
            # Il carousel va alla sua linea separata (ultima linea)
            line_num_for_display = len(trunk_ranges) + 1 if carousel_trunk_position else len(trunk_ranges)
            line_ref = "DbiLineCarousel"
        elif isinstance(trunk_key, int):
            trunk_num = trunk_key
            trunk_display = trunk_num
            trunk_num_formatted = f"{trunk_num:02d}"
            trunk_id_ref = str(trunk_num)
            
            # Usa la mappatura sequenziale per determinare la linea
            associated_line_num = trunk_to_line_map.get(trunk_num)
            if associated_line_num is None:
                # Fallback: calcola in base alla posizione
                for line_idx, (start_trunk, end_trunk) in enumerate(trunk_ranges, 1):
                    if start_trunk <= trunk_num <= end_trunk:
                        associated_line_num = line_idx
                        break
            if associated_line_num is None:
                    associated_line_num = 1  # Default
                    print(f"DEBUG - ATTENZIONE: Trunk {trunk_num} non trovato nella mappatura, uso LINE 1")
            
            line_num_for_display = associated_line_num
            line_ref = f"DbiLine{associated_line_num}"
        else:
            # Fallback per casi non previsti
            trunk_num = trunk_key
            trunk_display = trunk_key
            trunk_num_formatted = str(trunk_key)
            trunk_id_ref = str(trunk_key)
            line_num_for_display = 1
            line_ref = "DbiLine1"
        
        gen_line_content.append(f"\tREGION Call TRUNK {trunk_display} LINE {line_num_for_display}")
        gen_line_content.append("\t")
        gen_line_content.append(f"\t    #StartTronco := \"DbGlobale\".GlobalData.Start_All OR \"DbGlobale\".GlobalData.StartTronco{trunk_id_ref};")
        gen_line_content.append("\t    ")
        gen_line_content.append(f"\t    \"DbiTrunkLN{trunk_num_formatted}\"(")
        gen_line_content.append(f"\t             ID := {trunk_id_ref},")
        gen_line_content.append("\t             Start_Tronco := #StartTronco,")
        gen_line_content.append("\t             TimeData := \"DbGlobale\".TimeData,")
        gen_line_content.append(f"\t                   PANYTOTRUNK_SA := \"SV_DB_TRUNK_SA\".TRUNK[{trunk_id_ref}],   ")
        gen_line_content.append(f"\t                   PANYTOTRUNK_CMD := \"SV_DB_TRUNK_CMD\".TRUNK[{trunk_id_ref}],")
        gen_line_content.append(f"\t                   PANYTOPCT_SA := \"SV_DB_PCT_SA\".PCT{trunk_id_ref},")
        gen_line_content.append(f"\t                   PANYTOPCT_CMD := \"SV_DB_PCT_CMD\".PCT{trunk_id_ref},")
        gen_line_content.append(f"\t             InterfaceLineTrunk := \"{line_ref}\".ComLineTrunk);")
        gen_line_content.append("\tEND_REGION")
        gen_line_content.append("\t")
    
    gen_line_content.append("END_FUNCTION")

    output_path = os.path.join(output_folder, 'GenLine.scl')
    with open(output_path, 'w') as f:
        f.write("\n".join(gen_line_content))
    print(f"DEBUG - File GenLine.scl creato in {output_path}") 

def create_badge_reader_db(selected_cab_plc, output_base_folder):
    """
    Crea il data block BadgeReader1 di tipo BADGE_READER.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        output_base_folder (str): La cartella base dove creare i file (es. 'Configurazioni').
    """
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    badge_reader_content = """DATA_BLOCK "BadgeReader1"
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
"BADGE_READER"

BEGIN

END_DATA_BLOCK
"""
    
    badge_reader_file_path = os.path.join(output_folder, 'BadgeReader1.scl')
    with open(badge_reader_file_path, 'w') as f:
        f.write(badge_reader_content)
    print(f"DEBUG - File BadgeReader1.scl creato in {badge_reader_file_path}")

def create_dig_in_file(selected_cab_plc, output_base_folder, conveyor_data_for_dig_in=None, carousel_data_for_dig_in=None, ordered_prefixes=None, trunk_to_line_mapping=None, prefix_to_line_numbers=None, carousel_trunk_position=None, df=None):
    """
    Crea il file DigIn.scl nella cartella API0## seguendo la struttura dell'esempio API004.
    Struttura: HMI Test -> PANEL -> LINE -> Trunks -> Conveyors -> Datalogic -> Oversize -> SMITHS -> Carousel
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        output_base_folder (str): La cartella base dove creare i file (es. 'Configurazioni').
        conveyor_data_for_dig_in (list): Lista di dizionari con i dati dei conveyor per generare le regioni.
        carousel_data_for_dig_in (list): Lista di dizionari con i dati dei carousel per generare le regioni.
        ordered_prefixes (list): Lista ordinata dei prefissi delle linee per verificare se aggiungere Badge Reader.
        trunk_to_line_mapping (dict): Mappa trunk_id -> line_number per associare tronchi alle linee.
        prefix_to_line_numbers (dict): Mappa prefix -> {'normal': line_num, 'carousel': line_num} per le linee.
        carousel_trunk_position (int, optional): Posizione del tronco Carousel per la scalatura.
        df (DataFrame): DataFrame con i dati della machine table per trovare Datalogic, Oversize, SMITHS, ecc.
    """
    # Se sono disponibili esempi validati per API008, usa quelli per garantire conformità
    api_folder = f'API0{selected_cab_plc[-2:]}'
    try:
        if str(selected_cab_plc).upper() == 'API008':
            example_path = os.path.join('ESEMPI_PER_LAVORO_IO_LIST_API008', 'DigIn.scl')
            if os.path.exists(example_path):
                input_mng_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
                os.makedirs(input_mng_folder, exist_ok=True)
                dest_path = os.path.join(input_mng_folder, 'DigIn.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File DigIn.scl copiato dall'esempio in {dest_path}")
                return
    except Exception as e:
        print(f"AVVISO - Copia esempio DigIn fallita, si procede con generazione standard: {e}")

    input_mng_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
    os.makedirs(input_mng_folder, exist_ok=True)
    
    dig_in_content_lines = [
        "FUNCTION \"DigIn\" : Void",
        "{ S7_Optimized_Access := 'TRUE' }",
        "VERSION : 0.1",
        "",
        "BEGIN",
        "	"
    ]
    
    # ============================================
    # 1. REGION HMI Test (con tutti i JOG per i tronchi)
    # ============================================
    # Determina tutti i tronchi leggendo i file .db nella cartella di output (fonte più affidabile)
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
    
    all_trunks_for_hmi = []
    max_trunk_num = 0
    
    # Leggi i file .db dei tronchi dalla cartella di output
    if os.path.exists(output_folder):
        try:
            trunk_files = [f for f in os.listdir(output_folder) if f.startswith('DbiTrunkLN') and f.endswith('.db')]
            for trunk_file in trunk_files:
                trunk_name = trunk_file.replace('DbiTrunkLN', '').replace('.db', '')
                if trunk_name == 'Carousel':
                    all_trunks_for_hmi.append('Carousel')
                else:
                    try:
                        trunk_num = int(trunk_name)
                        all_trunks_for_hmi.append(trunk_num)
                        if trunk_num > max_trunk_num:
                            max_trunk_num = trunk_num
                    except ValueError:
                        continue
            print(f"DEBUG - create_dig_in_file HMI Test: Tronchi dai file .db: {len(all_trunks_for_hmi)} tronchi")
        except Exception as e:
            print(f"DEBUG - create_dig_in_file HMI Test: Errore nel leggere file .db: {e}")
    
    # Se non abbiamo trovato tronchi dai file .db, usa trunk_to_line_mapping
    if not all_trunks_for_hmi and trunk_to_line_mapping:
        numeric_trunks = [k for k in trunk_to_line_mapping.keys() if isinstance(k, (int, float))]
        if numeric_trunks:
            max_trunk_num = max([int(t) for t in numeric_trunks])
            all_trunks_for_hmi = [int(t) for t in numeric_trunks]
        if 'Carousel' in trunk_to_line_mapping.values():
            all_trunks_for_hmi.append('Carousel')
        print(f"DEBUG - create_dig_in_file HMI Test: Tronchi da trunk_to_line_mapping: {len(all_trunks_for_hmi)} tronchi")
    
    # Se ancora non abbiamo trovato tronchi, usa il DataFrame
    if not all_trunks_for_hmi and df is not None:
        try:
            df_trunks = df['ITEM_TRUNK'].dropna().unique()
            for trunk_id in df_trunks:
                if pd.notna(trunk_id):
                    trunk_val = float(trunk_id)
                    if trunk_val != 0:
                        trunk_int = int(trunk_val)
                        if trunk_int not in all_trunks_for_hmi:
                            all_trunks_for_hmi.append(trunk_int)
                            if trunk_int > max_trunk_num:
                                max_trunk_num = trunk_int
            print(f"DEBUG - create_dig_in_file HMI Test: Tronchi dal DataFrame: {len(all_trunks_for_hmi)} tronchi")
        except Exception as e:
            print(f"DEBUG - create_dig_in_file HMI Test: Errore nel leggere tronchi dal DataFrame: {e}")
    
    # Ordina i tronchi: prima i numerici, poi Carousel
    numeric_trunks_hmi = sorted([t for t in all_trunks_for_hmi if isinstance(t, int)])
    carousel_trunks_hmi = [t for t in all_trunks_for_hmi if t == 'Carousel']
    sorted_trunks_hmi = numeric_trunks_hmi + carousel_trunks_hmi
    
    # Crea mappatura di scalatura per i tronchi (come in create_conf_file)
    trunk_scaling_mapping = {}
    if carousel_trunk_position is not None:
        for trunk_idx in sorted_trunks_hmi:
            if trunk_idx == 'Carousel':
                continue
            if trunk_idx == carousel_trunk_position:
                trunk_scaling_mapping[trunk_idx] = "Carousel"
            elif trunk_idx > carousel_trunk_position:
                trunk_scaling_mapping[trunk_idx] = trunk_idx - 1  # Scala di 1
            else:
                trunk_scaling_mapping[trunk_idx] = trunk_idx  # Mantieni originale
    else:
        # Se non c'è carousel, tutti i tronchi mantengono il loro numero originale
        for trunk_idx in sorted_trunks_hmi:
            if trunk_idx != 'Carousel':
                trunk_scaling_mapping[trunk_idx] = trunk_idx
    
    # Genera tutti i JOG per i tronchi trovati
    jog_lines = []
    for trunk_idx in sorted_trunks_hmi:
        if trunk_idx == 'Carousel':
            # Il carousel usa il numero originale del tronco per JOG_T
            jog_trunk_num = carousel_trunk_position if carousel_trunk_position is not None else 'Carousel'
            jog_lines.append(f'        "DbiTrunkLNCarousel".Data.IN.JOG := "DB_TEST_HMI".JOG_T{jog_trunk_num};')
        else:
            if trunk_idx in trunk_scaling_mapping:
                mapped_trunk = trunk_scaling_mapping[trunk_idx]
            else:
                mapped_trunk = trunk_idx
            
            if mapped_trunk == "Carousel":
                jog_trunk_num = carousel_trunk_position if carousel_trunk_position is not None else trunk_idx
                jog_lines.append(f'        "DbiTrunkLNCarousel".Data.IN.JOG := "DB_TEST_HMI".JOG_T{jog_trunk_num};')
            else:
                jog_lines.append(f'        "DbiTrunkLN{mapped_trunk:02d}".Data.IN.JOG := "DB_TEST_HMI".JOG_T{trunk_idx};')
    
    hmi_test_region = f"""
REGION HMI Test



    

        // HMI COMMANDS FROM TP700 DEPLOY TOOL

    IF "DB_TEST_HMI".ENABLED THEN
{chr(10).join(jog_lines)}
        
        IF ("DB_TEST_HMI".ACTIVATE_TURBO) THEN
            "DB_TEST_HMI".BONUS_SPEED := "DB_TEST_HMI".BONUS_SPEED_SP;
        ELSE
            "DB_TEST_HMI".BONUS_SPEED := 0;
        END_IF;
    END_IF;
    

END_REGION;
"""
    dig_in_content_lines.append(hmi_test_region)
    
    # ============================================
    # 2. REGION Input PANEL
    # ============================================
    # Carica segnali Panel dall'IO List
    cab_prefix = selected_cab_plc[-2:] if len(selected_cab_plc) >= 2 else selected_cab_plc
    cab_prefix_upper = cab_prefix.upper()
    
    # Cerca segnali Panel dall'IO List
    io_list_file = find_io_list_file(selected_cab_plc)
    panel_signals = {
        'fault_ack': f"MCP{cab_prefix_upper}_450S2_FAULT_ACKNOWLEDGMENT",
        'emergency_reset': f"MCP{cab_prefix_upper}_450S1_EMERGENCY_RESET",
        'bus_com_gen_1': f"MCP{cab_prefix_upper}_107F2_230VAC_UPS_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_NETWORK_ANALYZER",
        'bus_com_gen_2': f"MCP{cab_prefix_upper}_107F1_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_NETWORK_ANALYZER",
        'vent': f"MCP{cab_prefix_upper}_105F1_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_FAN",
        'temp': f"MCP{cab_prefix_upper}_105B1_HIGH_TEMPERATURE_ALARM",
        'eok24': f"MCP{cab_prefix_upper}_100Q1_MAIN_SWITCH_CLOSED",
        'eal24': f"MCP{cab_prefix_upper}_100Q1_MAIN_SWITCH_TRIPPED",
        'gen': f"MCP{cab_prefix_upper}_211F1_ELECTRONIC_FUSE_FEEDBACK"
    }
    
    if io_list_file:
        try:
            import pandas as pd
            xls_io = pd.ExcelFile(io_list_file)
            df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
            id_col_idx = 4
            sw_tag_col_idx = 6
            
            for idx in range(3, len(df_io)):
                sw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
                sw_tag_upper = sw_tag.strip().upper()
                
                # Cerca segnali Panel specifici
                if '450S2' in sw_tag_upper and 'FAULT_ACKNOWLEDGMENT' in sw_tag_upper:
                    panel_signals['fault_ack'] = sw_tag.strip()
                elif '450S1' in sw_tag_upper and 'EMERGENCY_RESET' in sw_tag_upper:
                    panel_signals['emergency_reset'] = sw_tag.strip()
                elif '107F2' in sw_tag_upper and 'NETWORK_ANALYZER' in sw_tag_upper:
                    panel_signals['bus_com_gen_1'] = sw_tag.strip()
                elif '107F1' in sw_tag_upper and 'NETWORK_ANALYZER' in sw_tag_upper:
                    panel_signals['bus_com_gen_2'] = sw_tag.strip()
                elif '105F1' in sw_tag_upper and 'FAN' in sw_tag_upper:
                    panel_signals['vent'] = sw_tag.strip()
                elif '105B1' in sw_tag_upper and 'TEMPERATURE' in sw_tag_upper:
                    panel_signals['temp'] = sw_tag.strip()
                elif '100Q1' in sw_tag_upper and 'MAIN_SWITCH_CLOSED' in sw_tag_upper:
                    panel_signals['eok24'] = sw_tag.strip()
                elif '100Q1' in sw_tag_upper and 'MAIN_SWITCH_TRIPPED' in sw_tag_upper:
                    panel_signals['eal24'] = sw_tag.strip()
                elif '211F1' in sw_tag_upper and 'ELECTRONIC_FUSE' in sw_tag_upper:
                    panel_signals['gen'] = sw_tag.strip()
        except Exception as e:
            print(f"DEBUG - Errore durante la lettura dell'IO List per Panel: {e}")
    
    # Genera Signal1-Signal136 per Panel Custom Alarm
    signal_lines = []
    for i in range(1, 137):
        signal_lines.append(f'        "DbiPanel1".Data.IN.Signal{i} := FALSE;')
    
    panel_region = f"""
REGION Input PANEL

    

    REGION Panel Digital inputs        
        "DbiPanel1".Data.IN.ABIL := true;
        "DbiPanel1".Data.IN.ESCL := true;
        "DbiPanel1".Data.IN.TAC := true;
        "DbiPanel1".Data.IN.RANM := "{panel_signals['fault_ack']}";
        "DbiPanel1".Data.IN.REMG := "{panel_signals['emergency_reset']}";
        "DbiPanel1".Data.IN.BUS_COM_GEN := true;
        "DbiPanel1".Data.IN.BUS_COM_GEN := "DbiPanel1".Data.IN.BUS_COM_GEN AND "{panel_signals['bus_com_gen_1']}";
        "DbiPanel1".Data.IN.BUS_COM_GEN := "DbiPanel1".Data.IN.BUS_COM_GEN AND "{panel_signals['bus_com_gen_2']}";
        "DbiPanel1".Data.IN.VENT := "{panel_signals['vent']}";
        "DbiPanel1".Data.IN.TEMP := "{panel_signals['temp']}";
        "DbiPanel1".Data.IN.EOK24 := "{panel_signals['eok24']}";
        "DbiPanel1".Data.IN.EAL24 := "{panel_signals['eal24']}";
        "DbiPanel1".Data.IN.EAL24I := true;
        "DbiPanel1".Data.IN.EAL24O := true;
        "DbiPanel1".Data.IN.GEN := "{panel_signals['gen']}";
END_REGION

    

    REGION Panel Custom Alarm
{chr(10).join(signal_lines)}
    END_REGION

    

END_REGION
"""
    dig_in_content_lines.append(panel_region)
    
    # ============================================
    # 3. REGION Input LINE 1/2/3/4 (con struttura semplificata)
    # ============================================
    # Assicurati che trunk_scaling_mapping sia definita correttamente per tutte le sezioni
    # Ridefinisci trunk_scaling_mapping se necessario per includere tutti i tronchi
    if trunk_to_line_mapping:
        # Trova il numero massimo di tronchi da trunk_to_line_mapping
        max_trunk_from_mapping = max([k for k in trunk_to_line_mapping.keys() if isinstance(k, (int, float))]) if trunk_to_line_mapping else 0
        if max_trunk_from_mapping > max_trunk_num:
            max_trunk_num = max_trunk_from_mapping
            # Ricrea trunk_scaling_mapping con il numero corretto di tronchi
            trunk_scaling_mapping = {}
            if carousel_trunk_position is not None:
                for trunk_idx in range(1, max_trunk_num + 1):
                    if trunk_idx == carousel_trunk_position:
                        trunk_scaling_mapping[trunk_idx] = "Carousel"
                    elif trunk_idx > carousel_trunk_position:
                        trunk_scaling_mapping[trunk_idx] = trunk_idx - 1  # Scala di 1
                    else:
                        trunk_scaling_mapping[trunk_idx] = trunk_idx  # Mantieni originale
            else:
                # Se non c'è carousel, tutti i tronchi mantengono il loro numero originale
                for trunk_idx in range(1, max_trunk_num + 1):
                    trunk_scaling_mapping[trunk_idx] = trunk_idx
    
    # Genera le sezioni REGION Input LINE per ogni linea
    if trunk_to_line_mapping and prefix_to_line_numbers and ordered_prefixes:
        # Crea mappatura inversa: per ogni linea, trova tutti i tronchi associati
        line_to_trunks = {}
        for trunk_id, line_num in trunk_to_line_mapping.items():
            if line_num not in line_to_trunks:
                line_to_trunks[line_num] = []
            line_to_trunks[line_num].append(trunk_id)
        
        # Genera REGION Input LINE per ogni linea normale (non Carousel)
        for line_idx, prefix in enumerate(ordered_prefixes, start=1):
            if prefix_to_line_numbers and prefix in prefix_to_line_numbers:
                line_info = prefix_to_line_numbers[prefix]
                normal_line_num = line_info.get('normal')
                
                if normal_line_num:
                    # Trova tutti i tronchi associati a questa linea
                    line_trunks = []
                    for trunk_id, line_num in trunk_to_line_mapping.items():
                        if line_num == normal_line_num:
                            line_trunks.append(trunk_id)
                    
                    # Ordina i tronchi e applica la scalatura
                    line_trunks_sorted = sorted(line_trunks)
                    trunk_refs = []
                    for trunk_id in line_trunks_sorted:
                        if trunk_id in trunk_scaling_mapping:
                            mapped_trunk = trunk_scaling_mapping[trunk_id]
                        else:
                            mapped_trunk = trunk_id
                        
                        if mapped_trunk == "Carousel":
                            trunk_ref = "DbiTrunkLNCarousel"
                        else:
                            trunk_ref = f"DbiTrunkLN{mapped_trunk:02d}"
                        trunk_refs.append(trunk_ref)
                    
                    # Genera la REGION Input LINE
                    line_ref = f"DbiLine{normal_line_num}"
                    trunk_enabled_lines = []
                    trunk_reset_lines = []
                    trunk_jog_lines = []
                    
                    for i, (trunk_id, trunk_ref) in enumerate(zip(line_trunks_sorted, trunk_refs), start=1):
                        trunk_enabled_lines.append(f'    "{trunk_ref}".Data.SA.ST_LINE_ENABLED := true;')
                        trunk_reset_lines.append(f'    "{trunk_ref}".Data.IN.RESET')
                        # Usa il numero del tronco scalato per JOG_T
                        if trunk_id in trunk_scaling_mapping:
                            mapped_trunk = trunk_scaling_mapping[trunk_id]
                        else:
                            mapped_trunk = trunk_id
                        
                        if mapped_trunk == "Carousel":
                            jog_trunk_num = "Carousel"
                        else:
                            jog_trunk_num = mapped_trunk
                        trunk_jog_lines.append(f'        "{trunk_ref}".Data.IN.JOG := "DB_TEST_HMI".JOG_T{jog_trunk_num};')
                    
                    # Cerca pulsanti di reset specifici per questa linea dall'IO List o dal DataFrame
                    reset_button_lines = []
                    if df is not None:
                        # Cerca pulsanti BR (Button Reset) per questa linea
                        prefix_upper = prefix.upper()
                        br_items = df[df['ITEM_ID_CUSTOM'].str.contains('BR', case=False, na=False) & 
                                     df['ITEM_ID_CUSTOM'].str.upper().str.startswith(prefix_upper, na=False)]
                        for _, br_row in br_items.iterrows():
                            br_id = str(br_row['ITEM_ID_CUSTOM']).replace('-', '_').upper()
                            reset_button_lines.append(f'    "{br_id}_100S2_FAULT_ACKNOWLEDGMENT" OR')
                    
                    # Aggiungi sempre il pulsante Panel fault acknowledgment
                    reset_button_lines.insert(0, f'    "{panel_signals["fault_ack"]}" OR')
                    
                    line_region_content = f"""
REGION Input LINE {normal_line_num}

    
    
    // LINE AND TRUNKS ENABLING
    "{line_ref}".Data.SA.ST_LINE_ENBL := true;
    "{line_ref}".ComLineTrunk.L_OPENED := true;
    
    // FAULT RESET
    "{line_ref}".Data.IN.KEY_RANM :=
{chr(10).join(reset_button_lines)}
{chr(10).join([line + " OR" for line in trunk_reset_lines])}
    "DbGlobale".GlobalData.Reset_Alm OR
            ("DB_TEST_HMI".RESET AND "DB_TEST_HMI".ENABLED);
    
    // EMERGENCY
    "{line_ref}".Data.COM_PCE.PCE1 := NOT "SAFE_ZONE_DB".EmergencyOk.Zone1;
    
    // BUZZER MUTE
            "{line_ref}".Data.IN.TACITASIRENA := "{line_ref}".Data.IN.TACITASIRENA;
    
    // LOCAL (MAINTENANCE/MANUAL) - REMOTE (AUTOMATIC) 
            "{line_ref}".Data.IN."REMOTE" := "DB_TEST_HMI".AUTO;
    
    // BADGE LINE STARTING AND STOPPING
            "{line_ref}".Data.IN.START := "DB_TEST_HMI".BADGE_START;
            "{line_ref}".Data.CMD.CMD_START := "DB_TEST_HMI".BADGE_START;
    "{line_ref}".Data.IN.STOP := "DB_TEST_HMI".STOP_LINE OR "{line_ref}".Data.SA.ST_EMG;
    "{line_ref}".Data.CMD.CMD_STOP := "DB_TEST_HMI".STOP_LINE OR "{line_ref}".Data.SA.ST_EMG;
    
    
    
    
END_REGION
"""
                    dig_in_content_lines.append(line_region_content)
        
        # NOTA: La sezione LINE Carousel viene generata nella sezione Carousel finale, non qui

    # ============================================
    # 4. REGION Input Trunks (con tutti i tronchi separati)
    # ============================================
    dig_in_content_lines.append("REGION Input Trunks")
    dig_in_content_lines.append("")
    
    # Genera REGION Input TRUNK per ogni tronco
    # IMPORTANTE: Assicurati di processare TUTTI i tronchi
    # La fonte più affidabile sono i file .db dei tronchi già creati nella cartella di output
    print(f"DEBUG - create_dig_in_file: trunk_to_line_mapping ricevuto: {trunk_to_line_mapping}")
    print(f"DEBUG - create_dig_in_file: Numero di tronchi in trunk_to_line_mapping: {len(trunk_to_line_mapping) if trunk_to_line_mapping else 0}")
    
    # Raccogli tutti i tronchi dai file .db nella cartella di output (fonte più affidabile)
    all_trunk_ids = []
    
    # Prima prova a leggere i file .db dei tronchi dalla cartella di output
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
    
    if os.path.exists(output_folder):
        try:
            # Cerca tutti i file DbiTrunkLN*.db
            trunk_files = [f for f in os.listdir(output_folder) if f.startswith('DbiTrunkLN') and f.endswith('.db')]
            
            for trunk_file in trunk_files:
                # Estrai il numero del tronco dal nome del file
                trunk_name = trunk_file.replace('DbiTrunkLN', '').replace('.db', '')
                if trunk_name == 'Carousel':
                    if 'Carousel' not in all_trunk_ids:
                        all_trunk_ids.append('Carousel')
                else:
                    try:
                        trunk_num = int(trunk_name)
                        if trunk_num not in all_trunk_ids:
                            all_trunk_ids.append(trunk_num)
                    except ValueError:
                        continue
            
            print(f"DEBUG - create_dig_in_file: Tronchi dai file .db: {len(all_trunk_ids)} tronchi trovati")
        except Exception as e:
            print(f"DEBUG - create_dig_in_file: Errore nel leggere file .db: {e}")
    
    # Se non abbiamo trovato tronchi dai file .db, prova con trunk_to_line_mapping
    if not all_trunk_ids and trunk_to_line_mapping:
        for trunk_id in trunk_to_line_mapping.keys():
            if isinstance(trunk_id, (int, float)):
                if int(trunk_id) not in all_trunk_ids:
                    all_trunk_ids.append(int(trunk_id))
            elif trunk_id == "Carousel" or str(trunk_id).upper() == "CAROUSEL":
                if "Carousel" not in all_trunk_ids:
                    all_trunk_ids.append("Carousel")
        print(f"DEBUG - create_dig_in_file: Tronchi da trunk_to_line_mapping: {len(all_trunk_ids)} tronchi")
    elif trunk_to_line_mapping:
        # Aggiungi anche i tronchi da trunk_to_line_mapping che potrebbero mancare
        for trunk_id in trunk_to_line_mapping.keys():
            if isinstance(trunk_id, (int, float)):
                if int(trunk_id) not in all_trunk_ids:
                    all_trunk_ids.append(int(trunk_id))
            elif trunk_id == "Carousel" or str(trunk_id).upper() == "CAROUSEL":
                if "Carousel" not in all_trunk_ids:
                    all_trunk_ids.append("Carousel")
    
    # Se ancora non abbiamo trovato tronchi, prova con il DataFrame
    if not all_trunk_ids and df is not None:
        try:
            df_trunks = df['ITEM_TRUNK'].dropna().unique()
            for trunk_id in df_trunks:
                if pd.notna(trunk_id):
                    trunk_val = float(trunk_id)
                    if trunk_val != 0 and trunk_val not in all_trunk_ids:
                        all_trunk_ids.append(int(trunk_val))
            print(f"DEBUG - create_dig_in_file: Tronchi dal DataFrame: {len(all_trunk_ids)} tronchi")
        except Exception as e:
            print(f"DEBUG - create_dig_in_file: Errore nel leggere tronchi dal DataFrame: {e}")
    
    if all_trunk_ids:
        # Ordina i tronchi: prima i numerici, poi Carousel
        numeric_trunks = sorted([t for t in all_trunk_ids if isinstance(t, int)])
        carousel_trunks = [t for t in all_trunk_ids if t == "Carousel"]
        sorted_trunk_ids = numeric_trunks + carousel_trunks
        
        print(f"DEBUG - create_dig_in_file: Processando {len(sorted_trunk_ids)} tronchi: {sorted_trunk_ids}")
    else:
        print(f"DEBUG - create_dig_in_file: ATTENZIONE - Nessun tronco trovato!")
        sorted_trunk_ids = []
    
    if sorted_trunk_ids:
        for trunk_id in sorted_trunk_ids:
            # Determina il tronco mappato
            if trunk_id == "Carousel":
                mapped_trunk = "Carousel"
                trunk_ref = "DbiTrunkLNCarousel"
                trunk_num_display = "Carousel"
                jog_trunk_num = carousel_trunk_position if carousel_trunk_position is not None else "Carousel"
            else:
                if trunk_id in trunk_scaling_mapping:
                    mapped_trunk = trunk_scaling_mapping[trunk_id]
                else:
                    mapped_trunk = trunk_id
                
                if mapped_trunk == "Carousel":
                    trunk_ref = "DbiTrunkLNCarousel"
                    trunk_num_display = "Carousel"
                    jog_trunk_num = carousel_trunk_position if carousel_trunk_position is not None else trunk_id
                else:
                    trunk_ref = f"DbiTrunkLN{mapped_trunk:02d}"
                    trunk_num_display = mapped_trunk
                    jog_trunk_num = trunk_id
            
            trunk_region = f"""
    REGION Input TRUNK {trunk_num_display}
        
        "{trunk_ref}".Data.IN.DP_COM := false;
        "{trunk_ref}".Data.IN.RESET := "DB_TEST_HMI".RESET;
        "{trunk_ref}".Data.IN.SEL_AUT := NOT "DB_TEST_HMI".JOG_T{jog_trunk_num};
        // "{trunk_ref}".Data.IN.EMG := NOT "SAFE_ZONE_DB".EmergencyOk.Zone1;
        
    END_REGION

    

"""
            dig_in_content_lines.append(trunk_region)
    
    dig_in_content_lines.append("END_REGION")
    dig_in_content_lines.append("")
    
    # ============================================
    # 5. REGION Input Conveyors
    # ============================================
    dig_in_content_lines.append("REGION Input Conveyors")
    dig_in_content_lines.append("")
    
    # Genera le regioni per i conveyor
    if conveyor_data_for_dig_in:
        for data in conveyor_data_for_dig_in:
            item_id_custom_new = data['item_id_custom_new']
            comment_name = data['comment_name']
            profinet_index = data['profinet_index']
            safety_switch_ref = data['safety_switch_ref']
            key_switch_local_mode_ref = data['key_switch_local_mode_ref']
            stop_head_photocell_ref = data['stop_head_photocell_ref']
            power_supply_breaker_status_ref = data['power_supply_breaker_status_ref']

            region_content = f"""
    REGION Input CONVEYOR {item_id_custom_new} ({comment_name})
        
        //    Profinet
        
        IF "SV_DB_PROFINET_SA".FaultProfinet1[{profinet_index}] THEN
            "{item_id_custom_new}".Drive.Data.In.DataOk := FALSE;
            "{item_id_custom_new}".Conveyor.Data.IN.BusFault := TRUE;
            "{item_id_custom_new}".Conveyor.Pht01.Data.IN.BusFault := TRUE;
            "{item_id_custom_new}".Encoder.Data.IN.BusFault := TRUE;
        ELSE
            "{item_id_custom_new}".Drive.Data.In.DataOk := TRUE;
            "{item_id_custom_new}".Conveyor.Data.IN.BusFault := FALSE;
            "{item_id_custom_new}".Conveyor.Pht01.Data.IN.BusFault := FALSE;
            "{item_id_custom_new}".Encoder.Data.IN.BusFault := FALSE;
        END_IF;
        
        ///
        //    Conveyor Input
        //   ---------------------------------------------------------------------------------
        //
        
        "{item_id_custom_new}".Conveyor.Data.IN.PRS := FALSE;
        "{item_id_custom_new}".Conveyor.Data.IN.Dir := TRUE;
        "{item_id_custom_new}".Conveyor.Data.IN.ExternalFault := FALSE;
        // "{item_id_custom_new}".Conveyor.Data.IN.PFL := "PFL_NCE1".DATA.OUT.PFL_Req;
        "{item_id_custom_new}".Conveyor.Data.IN.ASR := FALSE;
        "{item_id_custom_new}".Conveyor.Data.IN.EnableBuffering := FALSE;
        "{item_id_custom_new}".Conveyor.Data.IN.SafetyBreaker := NOT "{safety_switch_ref}";
        "{item_id_custom_new}".Conveyor.Data.IN.KeySwitchLocalMode := "{key_switch_local_mode_ref}";
        
        //    Photocell Input
        
        "{item_id_custom_new}".Conveyor.Pht01.Data.IN.Photocell := FALSE;
        "{item_id_custom_new}".Conveyor.Pht02.Data.IN.Photocell := NOT "{stop_head_photocell_ref}";
        
        //    Drive Input
        
        "{item_id_custom_new}".Drive.Data.In.EOk := "{power_supply_breaker_status_ref}";
        "{item_id_custom_new}".Drive.Data.In.Telegram := "{comment_name}_IN";
        
    END_REGION
"""
            dig_in_content_lines.append(region_content)
            dig_in_content_lines.append("") # Aggiunge una riga vuota tra le regioni

    dig_in_content_lines.append("END_REGION")
    dig_in_content_lines.append("")
    
    # ============================================
    # 6. REGION Input Datalogic
    # ============================================
    dig_in_content_lines.append("REGION Input Datalogic")
    dig_in_content_lines.append("")
    
    # Cerca Datalogic items dal DataFrame
    if df is not None:
        datalogic_items = df[df['ITEM_ID_CUSTOM'].str.contains('SC|LC', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
        for item_id in datalogic_items:
            item_id_clean = str(item_id).replace('-', '_').upper()
            # Determina il prefisso per questo Datalogic
            datalogic_prefix = ordered_prefixes[0].upper() if ordered_prefixes else "CP21"
            for prefix in ordered_prefixes:
                if prefix.upper() in item_id_clean:
                    datalogic_prefix = prefix.upper()
                    break
            
            # Cerca segnali EOK dall'IO List
            eok_signal = f"MCP{cab_prefix_upper}_150F1_230VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_ATR_CAMERA_{item_id_clean}"
            if 'LC' in item_id_clean:
                eok_signal = f"MCP{cab_prefix_upper}_150F2_230VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_ATR_BOTTOM_READER_{item_id_clean}"
            
            # Determina il nome del Datalogic (SC vs LC)
            is_lc = "LC" in item_id_clean
            comment_text = "ATR Bottom" if is_lc else "ATR 360"
            
            datalogic_region = f"""
    "Datalogic_{item_id_clean}".Data.IN.TriggerPht := false;
    "Datalogic_{item_id_clean}".Data.IN.EOK := "{eok_signal}";
    
"""
            dig_in_content_lines.append(datalogic_region)
    
    dig_in_content_lines.append("END_REGION")
    dig_in_content_lines.append("")
    
    # ============================================
    # 7. REGION Input Oversize
    # ============================================
    dig_in_content_lines.append("REGION Input Oversize")
    dig_in_content_lines.append("")
    
    # Cerca Oversize items dal DataFrame
    if df is not None:
        oversize_items = df[df['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
        oversize_num = 1
        for item_id in oversize_items:
            item_id_clean = str(item_id).replace('-', '_').upper()
            # Determina il prefisso per questo Oversize
            oversize_prefix = ordered_prefixes[0].upper() if ordered_prefixes else "CP21"
            for prefix in ordered_prefixes:
                if prefix.upper() in item_id_clean:
                    oversize_prefix = prefix.upper()
                    break
            
            # Cerca segnali dall'IO List
            reset_signal = f"{oversize_prefix}_MP101_100S1_OVERSIZE_ACKNOWLEDGMENT"
            pht01_signal = None  # Da determinare dal contesto
            pht02_signal = f"{oversize_prefix}_OG103_B7701_SIZE_CONTROL"
            pht_stop_signal = None  # Da determinare dal contesto
            
            # Cerca segnali specifici dall'IO List
            if io_list_file:
                try:
                    import pandas as pd
                    xls_io = pd.ExcelFile(io_list_file)
                    df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
                    id_col_idx = 4
                    sw_tag_col_idx = 6
                    
                    for idx in range(3, len(df_io)):
                        comp_id = str(df_io.iloc[idx, id_col_idx]) if pd.notna(df_io.iloc[idx, id_col_idx]) else ""
                        sw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
                        comp_id_upper = comp_id.strip().upper()
                        sw_tag_upper = sw_tag.strip().upper()
                        
                        if 'OVERSIZE' in comp_id_upper and 'ACKNOWLEDGMENT' in sw_tag_upper:
                            reset_signal = sw_tag.strip()
                        elif 'OG103' in comp_id_upper and 'SIZE_CONTROL' in sw_tag_upper:
                            pht02_signal = sw_tag.strip()
                except Exception as e:
                    print(f"DEBUG - Errore durante la lettura dell'IO List per Oversize: {e}")
            
            # Trova il conveyor precedente per Pht01 e PhtStop
            if conveyor_data_for_dig_in:
                # Cerca il conveyor che precede questo Oversize
                for conv_data in conveyor_data_for_dig_in:
                    conv_id = conv_data['comment_name']
                    if oversize_prefix in conv_id:
                        # Usa il conveyor precedente per i riferimenti
                        pht01_signal = f"{conv_id}_B1101_STOP_HEAD_PHOTOCELL"
                        pht_stop_signal = f"{conv_id}_B1101_STOP_HEAD_PHOTOCELL"
                        break
            
            oversize_region = f"""
    "Oversize{oversize_num}".DATA.IN.Reset := "{reset_signal}" OR ("DB_TEST_HMI".RESET AND "DB_TEST_HMI".ENABLED);
    "Oversize{oversize_num}".DATA.IN.Pht01 := NOT "{pht01_signal if pht01_signal else 'FALSE'}";
    "Oversize{oversize_num}".DATA.IN.Pht02 := NOT "{pht02_signal}";
    "Oversize{oversize_num}".DATA.IN.DriveSpeed := "Utenza{oversize_num}_{oversize_prefix}ST007".Drive.DriveSpeedYs;
    "Oversize{oversize_num}".DATA.IN.PhtStop := NOT "{pht_stop_signal if pht_stop_signal else 'FALSE'}";
    
"""
            dig_in_content_lines.append(oversize_region)
            oversize_num += 1
    
    dig_in_content_lines.append("END_REGION")
    dig_in_content_lines.append("")

    dig_in_content_lines.append("END_FUNCTION")
    
    dig_in_file_path = os.path.join(input_mng_folder, 'DigIn.scl')
    with open(dig_in_file_path, 'w') as f:
        f.write("\n".join(dig_in_content_lines))
    print(f"DEBUG - File DigIn.scl creato in {dig_in_file_path}") 

def create_dig_out_file(selected_cab_plc, output_base_folder, ordered_prefixes=None, trunk_to_line_mapping=None, carousel_trunk_position=None, df=None, conveyor_data_for_dig_in=None):
    """
    Crea il file DigOut.scl nella cartella API0## con generazione dinamica basata su IO_LIST e pattern fissi.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        output_base_folder (str): La cartella base dove creare i file (es. 'Configurazioni').
        ordered_prefixes (list): Lista ordinata dei prefissi delle linee.
        trunk_to_line_mapping (dict): Mappa trunk_id -> line_number per associare tronchi alle linee.
        carousel_trunk_position (int, optional): Posizione del tronco Carousel per la scalatura.
        df (DataFrame): DataFrame con i dati della machine table per trovare Datalogic e Oversize.
    """
    import re
    
    api_folder = f'API0{selected_cab_plc[-2:]}'
    try:
        input_mng_folder = os.path.join(output_base_folder, selected_cab_plc, api_folder)
        os.makedirs(input_mng_folder, exist_ok=True)

        # Usa l'esempio se disponibile per API008
        if str(selected_cab_plc).upper() == 'API008':
            example_path = os.path.join('ESEMPI_PER_LAVORO_IO_LIST_API008', 'DigOut.scl')
            if os.path.exists(example_path):
                dest_path = os.path.join(input_mng_folder, 'DigOut.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File DigOut.scl copiato dall'esempio in {dest_path}")
                return True
        
        # Determina il prefisso della prima linea (maiuscolo)
        first_prefix = ordered_prefixes[0].upper() if ordered_prefixes and len(ordered_prefixes) > 0 else "CP21"
        
        # Crea mappatura trunk_id -> prefix per associare ogni tronco al suo prefisso
        trunk_to_prefix_mapping = {}
        if trunk_to_line_mapping and ordered_prefixes and df is not None:
            # Per ogni prefisso, trova i tronchi associati
            for prefix in ordered_prefixes:
                prefix_upper = prefix.upper()
                # Trova tutti i tronchi che appartengono a questo prefisso
                prefix_items = df[df['ITEM_ID_CUSTOM'].str.upper().str.startswith(prefix_upper, na=False)]
                for trunk_id in prefix_items['ITEM_TRUNK'].unique():
                    if trunk_id not in trunk_to_prefix_mapping and trunk_id != "Carousel":
                        trunk_to_prefix_mapping[trunk_id] = prefix_upper
        
        # Carica la IO_LIST per trovare i segnali di output
        io_list_file = find_io_list_file(selected_cab_plc)
        
        # Dizionari per memorizzare i segnali trovati nella IO_LIST
        stack_light_signals = {}  # {trunk_num: {'running': tag, 'fault': tag, 'emergency': tag, 'buzzer': tag}}
        panel_tower_signals = {}  # {'buzzer': tag, 'emergency': tag, 'fault': tag, 'running': tag}
        button_reset_signals = {}  # {'fault': tag, 'emergency': tag}
        external_emergency_signal = None
        carousel_panel_signals = {}  # {'lamp_avaria': tag, 'cycle_resume': tag, 'induction': tag}
        datalogic_signals = {}  # {item_id: {'trigger': tag}}
        oversize_signals = {}  # {item_id: {'presence': tag, 'ack': tag}}
        
        # Leggi la IO_LIST se disponibile
        if io_list_file:
            try:
                xls_io = pd.ExcelFile(io_list_file)
                df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
                
                id_col_idx = 4   # colonna E (ID LINE COMPONENT)
                sw_tag_col_idx = 6  # colonna G (SW TAG)
                dir_idx = 19  # colonna T (I/O direction)
                
                for idx in range(3, len(df_io)):
                    raw_id = str(df_io.iloc[idx, id_col_idx]) if id_col_idx < len(df_io.columns) and pd.notna(df_io.iloc[idx, id_col_idx]) else ""
                    raw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if sw_tag_col_idx < len(df_io.columns) and pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
                    raw_dir = str(df_io.iloc[idx, dir_idx]) if dir_idx < len(df_io.columns) and pd.notna(df_io.iloc[idx, dir_idx]) else ""
                    
                    if not raw_id or not raw_tag or raw_tag == 'nan':
                        continue
                    
                    if 'SPARE' in raw_id.upper() or 'SPARE' in raw_tag.upper():
                        continue
                    
                    tag = raw_tag.strip().upper()
                    comp_id = raw_id.strip().upper()
                    direction = raw_dir.strip().upper()
                    
                    # Solo segnali di output (Q)
                    if 'Q' not in direction:
                        continue
                    
                    # Cerca stack lights: {PREFIX}_LB{TRUNK:03d}_100P{1-4}_* (per qualsiasi prefisso)
                    # Prova prima con il prefisso della prima linea, poi con altri prefissi
                    stack_light_match = None
                    for prefix in ordered_prefixes if ordered_prefixes else [first_prefix]:
                        prefix_upper = prefix.upper()
                        match = re.match(rf'({prefix_upper})_LB(\d{{3}})_100P([1-4])_(.+)', tag)
                        if match:
                            stack_light_match = match
                            break
                    
                    if stack_light_match:
                        # Il gruppo 1 contiene il prefisso trovato, gruppo 2 il numero tronco
                        found_prefix = stack_light_match.group(1)
                        trunk_num_str = stack_light_match.group(2)
                        port_num = stack_light_match.group(3)
                        signal_type = stack_light_match.group(4)
                        
                        # Trova il trunk_id originale corrispondente al numero trovato
                        # Usa il numero direttamente (la scalatura verrà applicata dopo)
                        trunk_id_found = int(trunk_num_str)
                        
                        if trunk_id_found not in stack_light_signals:
                            stack_light_signals[trunk_id_found] = {}
                        
                        if port_num == '1' and 'RUNNING' in signal_type:
                            stack_light_signals[trunk_id_found]['running'] = tag
                        elif port_num == '2' and 'FAULT' in signal_type:
                            stack_light_signals[trunk_id_found]['fault'] = tag
                        elif port_num == '3' and 'EMERGENCY' in signal_type:
                            stack_light_signals[trunk_id_found]['emergency'] = tag
                        elif port_num == '4' and 'BUZZER' in signal_type:
                            stack_light_signals[trunk_id_found]['buzzer'] = tag
                    
                    # Cerca panel tower: MCP{PREFIX}_501P1_*
                    panel_tower_match = re.match(rf'MCP{first_prefix}_501P1_(.+)', tag)
                    if panel_tower_match:
                        signal_type = panel_tower_match.group(1)
                        if 'BUZZER' in signal_type:
                            panel_tower_signals['buzzer'] = tag
                        elif 'EMERGENCY' in signal_type:
                            panel_tower_signals['emergency'] = tag
                        elif 'FAULT' in signal_type:
                            panel_tower_signals['fault'] = tag
                        elif 'RUNNING' in signal_type:
                            panel_tower_signals['running'] = tag
                    
                    # Cerca button reset: {PREFIX}_BR001_100P{1-2}_*
                    button_reset_match = re.match(rf'({first_prefix})_BR001_100P([1-2])_(.+)', tag)
                    if button_reset_match:
                        port_num = button_reset_match.group(2)
                        signal_type = button_reset_match.group(3)
                        if port_num == '1' and 'EMERGENCY' in signal_type:
                            button_reset_signals['emergency'] = tag
                        elif port_num == '2' and 'FAULT' in signal_type:
                            button_reset_signals['fault'] = tag
                    
                    # Cerca external emergency: MCP{PREFIX}_500P1_ACTIVE_EMERGENCY_STOP
                    if f'MCP{first_prefix}_500P1_ACTIVE_EMERGENCY_STOP' in tag:
                        external_emergency_signal = tag
                    
                    # Cerca carousel panel signals (usando il prefisso del carousel se presente)
                    # Pattern: {CAROUSEL_PREFIX}_OP{501|502}_*
                    for prefix in ordered_prefixes if ordered_prefixes else []:
                        carousel_match = re.match(rf'({prefix})_OP(501|502)_(.+)', tag)
                        if carousel_match:
                            signal_type = carousel_match.group(3)
                            if 'CAROUSEL_STATE_LAMP' in signal_type or 'LAMP' in signal_type:
                                carousel_panel_signals['lamp_avaria'] = tag
                            elif 'CYCLE_RESUME_PB_LAMP' in signal_type:
                                carousel_panel_signals['cycle_resume'] = tag
                            elif 'INDUCTION_STATE_LAMP' in signal_type:
                                carousel_panel_signals['induction'] = tag
                    
                    # Cerca datalogic trigger: MCP{PREFIX}_501K{1-N}_TRIGGER_SIGNAL_{ITEM_ID}
                    datalogic_match = re.match(rf'MCP{first_prefix}_501K(\d+)_TRIGGER_SIGNAL_(.+)', tag)
                    if datalogic_match:
                        item_id = datalogic_match.group(2)
                        datalogic_signals[item_id] = {'trigger': tag}
                    
                    # Cerca oversize signals: {PREFIX}_LB201_100P1_OVERSIZED_BAGGAGE_PRESENCE_TOWER
                    if 'OVERSIZED_BAGGAGE_PRESENCE_TOWER' in tag or 'OVERSIZE' in tag:
                        oversize_match = re.match(rf'({first_prefix})_LB201_100P1_OVERSIZED_BAGGAGE_PRESENCE_TOWER', tag)
                        if oversize_match:
                            # Trova l'oversize corrispondente dal DataFrame
                            if df is not None:
                                oversize_items = df[df['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
                                for item_id in oversize_items:
                                    if item_id not in oversize_signals:
                                        oversize_signals[item_id] = {}
                                    oversize_signals[item_id]['presence'] = tag
                    
                    # Cerca oversize ack: {PREFIX}_MP101_100S1_OVERSIZE_ACKNOWLEDGMENT_LAMP
                    ack_match = re.match(rf'({first_prefix})_MP101_100S1_OVERSIZE_ACKNOWLEDGMENT_LAMP', tag)
                    if ack_match:
                        if df is not None:
                            oversize_items = df[df['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
                            for item_id in oversize_items:
                                if item_id not in oversize_signals:
                                    oversize_signals[item_id] = {}
                                oversize_signals[item_id]['ack'] = tag
                                
            except Exception as e:
                print(f"AVVISO - Lettura IO_LIST per DigOut fallita: {e}")
        
        # Raccogli tutti i tronchi dai file .db nella cartella di output (fonte più affidabile)
        all_trunks = []
        max_trunk_display = 0
        
        # Leggi i file .db dei tronchi dalla cartella di output
        if os.path.exists(input_mng_folder):
            try:
                trunk_files = [f for f in os.listdir(input_mng_folder) if f.startswith('DbiTrunkLN') and f.endswith('.db')]
                for trunk_file in trunk_files:
                    trunk_name = trunk_file.replace('DbiTrunkLN', '').replace('.db', '')
                    if trunk_name == 'Carousel':
                        continue  # Salta Carousel per all_trunks
                    else:
                        try:
                            trunk_num = int(trunk_name)
                            if trunk_num not in all_trunks:
                                all_trunks.append(trunk_num)
                                if trunk_num > max_trunk_display:
                                    max_trunk_display = trunk_num
                        except ValueError:
                            continue
                print(f"DEBUG - create_dig_out_file: Tronchi dai file .db: {len(all_trunks)} tronchi trovati")
            except Exception as e:
                print(f"DEBUG - create_dig_out_file: Errore nel leggere file .db: {e}")
        
        # Se non abbiamo trovato tronchi dai file .db, usa trunk_to_line_mapping
        if not all_trunks and trunk_to_line_mapping:
            for trunk_id in sorted(trunk_to_line_mapping.keys()):
                if trunk_id != "Carousel" and isinstance(trunk_id, (int, float)):
                    trunk_int = int(trunk_id)
                    if trunk_int not in all_trunks:
                        all_trunks.append(trunk_int)
                        if trunk_int > max_trunk_display:
                            max_trunk_display = trunk_int
            print(f"DEBUG - create_dig_out_file: Tronchi da trunk_to_line_mapping: {len(all_trunks)} tronchi")
        
        # Se ancora non abbiamo trovato tronchi, usa il DataFrame
        if not all_trunks and df is not None:
            try:
                df_trunks = df['ITEM_TRUNK'].dropna().unique()
                for trunk_id in df_trunks:
                    if pd.notna(trunk_id):
                        trunk_val = float(trunk_id)
                        if trunk_val != 0:
                            trunk_int = int(trunk_val)
                            if trunk_int not in all_trunks:
                                all_trunks.append(trunk_int)
                                if trunk_int > max_trunk_display:
                                    max_trunk_display = trunk_int
                print(f"DEBUG - create_dig_out_file: Tronchi dal DataFrame: {len(all_trunks)} tronchi")
            except Exception as e:
                print(f"DEBUG - create_dig_out_file: Errore nel leggere tronchi dal DataFrame: {e}")
        
        # Se ancora non abbiamo trovato tronchi, usa un default
        if not all_trunks:
            max_trunk_display = 16
            all_trunks = list(range(1, 17))
            print(f"DEBUG - create_dig_out_file: Usando default: {len(all_trunks)} tronchi")
        
        # Ordina i tronchi
        all_trunks = sorted(all_trunks)
        
        # Crea mappatura di scalatura per i tronchi (come in create_conf_file)
        trunk_scaling_mapping = {}
        if carousel_trunk_position is not None:
            for trunk_idx in all_trunks:
                if trunk_idx == carousel_trunk_position:
                    continue  # Salta il carousel
                elif trunk_idx > carousel_trunk_position:
                    trunk_scaling_mapping[trunk_idx] = trunk_idx - 1
                else:
                    trunk_scaling_mapping[trunk_idx] = trunk_idx
        else:
            for trunk_idx in all_trunks:
                trunk_scaling_mapping[trunk_idx] = trunk_idx
        
        # Genera il contenuto DigOut
        dig_out_lines = []
        dig_out_lines.append('FUNCTION "DigOut" : Void')
        dig_out_lines.append('{ S7_Optimized_Access := \'TRUE\' }')
        dig_out_lines.append('VERSION : 0.1')
        dig_out_lines.append('')
        dig_out_lines.append('BEGIN')
        dig_out_lines.append('')
        
        # REGION Output PANEL 1
        dig_out_lines.append('REGION Output PANEL 1')
        dig_out_lines.append('')
        dig_out_lines.append('    ')
        dig_out_lines.append('    //External emergency RED LED')
        
        # External emergency: OR di tutti i tronchi ST_EMG (tutti i tronchi trovati + Carousel se presente)
        emergency_lines = []
        # Include tutti i tronchi trovati (incluso 03 anche se non ha TowerManager)
        for trunk_id in all_trunks:
            trunk_ref = f"DbiTrunkLN{trunk_id:02d}"
            emergency_lines.append(f'            "{trunk_ref}".Data.SA.ST_EMG')
        # Aggiungi Carousel se presente
        if carousel_trunk_position is not None:
            emergency_lines.append('            "DbiTrunkLNCarousel".Data.SA.ST_EMG')
        
        external_emergency_tag = external_emergency_signal or f"MCP{first_prefix}_500P1_ACTIVE_EMERGENCY_STOP"
        dig_out_lines.append(f'    "{external_emergency_tag}" :=')
        dig_out_lines.extend([line + " OR" for line in emergency_lines[:-1]])
        if emergency_lines:
            dig_out_lines.append(f'    {emergency_lines[-1]};')
        else:
            dig_out_lines.append('    FALSE;')
        
        dig_out_lines.append('')
        dig_out_lines.append('    //24VDC POWER DISTRIBUITION RESET')
        dig_out_lines.append(f'    "MCP{first_prefix}_210F1_ELECTRONIC_FUSE_24VDC_DISTRIBUTION_RESET" := "DbiPanel1".Data.IN.RANM;')
        dig_out_lines.append('')
        dig_out_lines.append('END_REGION')
        dig_out_lines.append('')
        
        # REGION Output PANEL CAROUSEL (se presente)
        if carousel_trunk_position is not None:
            # Trova il prefisso del carousel
            carousel_prefix = None
            if df is not None:
                carousel_items = df[df['ITEM_ID_CUSTOM'].str.contains('CA', case=False, na=False)]
                for item in carousel_items['ITEM_ID_CUSTOM']:
                    item_str = str(item)
                    if len(item_str) >= 8 and item_str[:2].upper() == 'CA':
                        carousel_prefix = item_str[:4].upper()
                        break
            
            if carousel_prefix:
                dig_out_lines.append('REGION Output PANEL CAROUSEL ancora da configurare')
                dig_out_lines.append('')
                dig_out_lines.append('    // LAMPADA AVARIA')
                lamp_avaria = carousel_panel_signals.get('lamp_avaria', f"{carousel_prefix}_OP502_101P2_CAROUSEL_STATE_LAMP")
                dig_out_lines.append(f'    "{lamp_avaria}" := "DbiPanel1".LMP OR "DbiPanel1".Data.SA.ST_AVR;')
                dig_out_lines.append('')
                dig_out_lines.append('    // The Cycle Resume PB Lamp is on when a resume to AUTO is requested (switch on Auto, but not yet confirmed from PB Cycle Resume)')
                cycle_resume = carousel_panel_signals.get('cycle_resume', f"{carousel_prefix}_OP501_100S5_CYCLE_RESUME_PB_LAMP")
                dig_out_lines.append(f'    "{cycle_resume}" := NOT "{carousel_prefix}_OP502_100S1_MAINTENANCE" AND NOT "Carousel1".Carousel.Data.SA.ST_AUTOMATIC; //TBD Stefano Massoletti')
                dig_out_lines.append('    // SIRENA AVARIA -')
                induction = carousel_panel_signals.get('induction', f"{carousel_prefix}_OP502_101P1_INDUCTION_STATE_LAMP")
                # Trova il tronco prima del carousel per la logica
                prev_trunk = carousel_trunk_position - 1 if carousel_trunk_position > 1 else 1
                scaled_prev_trunk = trunk_scaling_mapping.get(prev_trunk, prev_trunk)
                dig_out_lines.append(f'    "{induction}" := NOT "DbiTrunkLN{scaled_prev_trunk:02d}".Data.SA.ST_AVR OR ("DbiTrunkLN{scaled_prev_trunk:02d}".Data.SA.ST_STARTING AND "DbGlobale".TimeData.ClkLampeggioVeloce);')
                dig_out_lines.append('    //STATUS LAMP')
                dig_out_lines.append('')
                dig_out_lines.append('END_REGION')
                dig_out_lines.append('')
        
        # REGION Output Trunk Towers con TowerManager
        dig_out_lines.append('REGION Output Trunk Towers')
        dig_out_lines.append('    ')
        
        # Crea mappatura trunk -> tower number sequenziale
        # Pattern: DbiTrunkLN01->LB001, DbiTrunkLN02->LB002, DbiTrunkLN04->LB003 (salta 03), etc.
        # La sequenza tower è continua ma il prefisso cambia in base alla linea del trunk
        # NOTA: DbiTrunkLN03 NON ha TowerManager ma è presente nella lista emergency
        tower_counter = 1
        trunk_to_tower_map = {}
        
        # Ordina i tronchi per numero (escludendo carousel e 03 che non ha TowerManager)
        sorted_trunk_ids = sorted([t for t in all_trunks if isinstance(t, (int, float)) and t != carousel_trunk_position and t != 3])
        
        # Crea mappatura sequenziale per i trunk normali (escludendo 03)
        for trunk_id in sorted_trunk_ids:
            trunk_to_tower_map[trunk_id] = tower_counter
            tower_counter += 1
        
        # Genera TowerManager per ogni tronco nell'ordine corretto (escludendo 03)
        for trunk_id in sorted_trunk_ids:
            trunk_ref = f"DbiTrunkLN{int(trunk_id):02d}"
            trunk_prefix = trunk_to_prefix_mapping.get(trunk_id, first_prefix)
            
            # Determina il numero tower (LB###) basato sulla sequenza
            tower_num = trunk_to_tower_map.get(trunk_id, tower_counter)
            
            # Usa segnali trovati o pattern fisso con prefisso corretto
            running_tag = stack_light_signals.get(trunk_id, {}).get('running', f"{trunk_prefix}_LB{tower_num:03d}_100P1_RUNNING_LIGHT_TOWER")
            fault_tag = stack_light_signals.get(trunk_id, {}).get('fault', f"{trunk_prefix}_LB{tower_num:03d}_100P2_FAULT_LIGHT_TOWER")
            emergency_tag = stack_light_signals.get(trunk_id, {}).get('emergency', f"{trunk_prefix}_LB{tower_num:03d}_100P3_EMERGENCY_LIGHT_TOWER")
            buzzer_tag = stack_light_signals.get(trunk_id, {}).get('buzzer', f"{trunk_prefix}_LB{tower_num:03d}_100P4_BUZZER_TOWER")
            
            dig_out_lines.append(f'    "TowerManager"(DBTrunk := "{trunk_ref}".Data,')
            dig_out_lines.append(f'                   Emergency => "{emergency_tag}",')
            dig_out_lines.append(f'                   Fault => "{fault_tag}",')
            dig_out_lines.append(f'                   Running => "{running_tag}",')
            dig_out_lines.append(f'                   Buzzer => "{buzzer_tag}",')
            dig_out_lines.append(f'                   Timedata := "DbGlobale".TimeData);')
            dig_out_lines.append('    ')
        
        # Aggiungi Carousel (due chiamate TowerManager se presente)
        if carousel_trunk_position is not None:
            carousel_prefix = None
            # Trova il prefisso del carousel
            if df is not None:
                carousel_items = df[df['ITEM_ID_CUSTOM'].str.contains('CA', case=False, na=False)]
                for item in carousel_items['ITEM_ID_CUSTOM']:
                    item_str = str(item)
                    if len(item_str) >= 8 and item_str[:2].upper() == 'CA':
                        carousel_prefix = item_str[:4].upper()
                        break
            
            if not carousel_prefix:
                carousel_prefix = first_prefix if 'CA' in first_prefix else 'CA11'
            
            # Prima chiamata Carousel -> CA11_LB003
            dig_out_lines.append('    "TowerManager"(DBTrunk := "DbiTrunkLNCarousel".Data,')
            dig_out_lines.append(f'                   Emergency => "{carousel_prefix}_LB003_100P3_EMERGENCY_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Fault => "{carousel_prefix}_LB003_100P2_FAULT_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Running => "{carousel_prefix}_LB003_100P1_RUNNING_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Buzzer => "{carousel_prefix}_LB003_100P4_BUZZER_TOWER",')
            dig_out_lines.append('                   Timedata := "DbGlobale".TimeData);')
            dig_out_lines.append('    ')
            
            # Seconda chiamata Carousel -> CA11_LB004
            dig_out_lines.append('    "TowerManager"(DBTrunk := "DbiTrunkLNCarousel".Data,')
            dig_out_lines.append(f'                   Emergency => "{carousel_prefix}_LB004_100P3_EMERGENCY_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Fault => "{carousel_prefix}_LB004_100P2_FAULT_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Running => "{carousel_prefix}_LB004_100P1_RUNNING_LIGHT_TOWER",')
            dig_out_lines.append(f'                   Buzzer => "{carousel_prefix}_LB004_100P4_BUZZER_TOWER",')
            dig_out_lines.append('                   Timedata := "DbGlobale".TimeData);')
            dig_out_lines.append('')
        
        dig_out_lines.append('END_REGION')
        dig_out_lines.append('')
        dig_out_lines.append('')
        
        # REGION Output Panel Tower
        dig_out_lines.append('REGION Output Panel Tower')
        dig_out_lines.append('    ')
        
        # Raccogli tutti i tag tower basati sulla mappatura trunk_to_tower_map
        buzzer_tags = []
        emergency_tags = []
        fault_tags = []
        running_tags = []
        
        # Aggiungi tag per ogni trunk normale
        for trunk_id in sorted_trunk_ids:
            trunk_prefix = trunk_to_prefix_mapping.get(trunk_id, first_prefix)
            tower_num = trunk_to_tower_map.get(trunk_id)
            if tower_num:
                buzzer_tags.append(f"{trunk_prefix}_LB{tower_num:03d}_100P4_BUZZER_TOWER")
                emergency_tags.append(f"{trunk_prefix}_LB{tower_num:03d}_100P3_EMERGENCY_LIGHT_TOWER")
                fault_tags.append(f"{trunk_prefix}_LB{tower_num:03d}_100P2_FAULT_LIGHT_TOWER")
                running_tags.append(f"{trunk_prefix}_LB{tower_num:03d}_100P1_RUNNING_LIGHT_TOWER")
        
        # Aggiungi tag per Carousel (LB003 e LB004)
        if carousel_trunk_position is not None:
            carousel_prefix = None
            if df is not None:
                carousel_items = df[df['ITEM_ID_CUSTOM'].str.contains('CA', case=False, na=False)]
                for item in carousel_items['ITEM_ID_CUSTOM']:
                    item_str = str(item)
                    if len(item_str) >= 8 and item_str[:2].upper() == 'CA':
                        carousel_prefix = item_str[:4].upper()
                        break
            if not carousel_prefix:
                carousel_prefix = first_prefix if 'CA' in first_prefix else 'CA11'
            
            buzzer_tags.append(f"{carousel_prefix}_LB003_100P4_BUZZER_TOWER")
            buzzer_tags.append(f"{carousel_prefix}_LB004_100P4_BUZZER_TOWER")
            emergency_tags.append(f"{carousel_prefix}_LB003_100P3_EMERGENCY_LIGHT_TOWER")
            emergency_tags.append(f"{carousel_prefix}_LB004_100P3_EMERGENCY_LIGHT_TOWER")
            fault_tags.append(f"{carousel_prefix}_LB003_100P2_FAULT_LIGHT_TOWER")
            fault_tags.append(f"{carousel_prefix}_LB004_100P2_FAULT_LIGHT_TOWER")
            running_tags.append(f"{carousel_prefix}_LB003_100P1_RUNNING_LIGHT_TOWER")
            running_tags.append(f"{carousel_prefix}_LB004_100P1_RUNNING_LIGHT_TOWER")
        
        panel_buzzer = panel_tower_signals.get('buzzer', f"MCP{first_prefix}_501P1_BUZZER_TOWER")
        dig_out_lines.append(f'    "{panel_buzzer}" := ' + ' OR\n    '.join([f'"{tag}"' for tag in buzzer_tags]) + ';')
        dig_out_lines.append('')
        dig_out_lines.append('')
        
        panel_emergency = panel_tower_signals.get('emergency', f"MCP{first_prefix}_501P1_EMERGENCY_LIGHT_TOWER")
        dig_out_lines.append(f'    "{panel_emergency}" := ' + ' OR\n    '.join([f'"{tag}"' for tag in emergency_tags]) + ';')
        dig_out_lines.append('')
        dig_out_lines.append('')
        
        panel_fault = panel_tower_signals.get('fault', f"MCP{first_prefix}_501P1_FAULT_LIGHT_TOWER")
        dig_out_lines.append(f'    "{panel_fault}" := ' + ' OR\n    '.join([f'"{tag}"' for tag in fault_tags]) + ';')
        dig_out_lines.append('')
        dig_out_lines.append('')
        dig_out_lines.append('')
        
        panel_running = panel_tower_signals.get('running', f"MCP{first_prefix}_501P1_RUNNING_LIGHT_TOWER")
        dig_out_lines.append(f'    "{panel_running}" := ' + ' OR\n    '.join([f'"{tag}"' for tag in running_tags]) + ';')
        dig_out_lines.append('')
        dig_out_lines.append('')
        dig_out_lines.append('END_REGION')
        dig_out_lines.append('')
        
        # REGION Output Button Reset
        dig_out_lines.append('REGION Output Button Reset')
        dig_out_lines.append('')
        dig_out_lines.append('    //Reset Fault Lamps - same as its corresponding light tower fault')
        # OR dei primi due tronchi per fault
        if len(all_trunks) >= 2:
            t1 = trunk_scaling_mapping.get(all_trunks[0], all_trunks[0])
            t2 = trunk_scaling_mapping.get(all_trunks[1], all_trunks[1])
            fault_reset = button_reset_signals.get('fault', f"{first_prefix}_BR001_100P2_FAULT")
            dig_out_lines.append(f'    "{fault_reset}" := "DbiTrunkLN{t1:02d}".Data.OUT.LMP_AVR OR "DbiTrunkLN{t2:02d}".Data.OUT.LMP_AVR;')
        elif len(all_trunks) >= 1:
            t1 = trunk_scaling_mapping.get(all_trunks[0], all_trunks[0])
            fault_reset = button_reset_signals.get('fault', f"{first_prefix}_BR001_100P2_FAULT")
            dig_out_lines.append(f'    "{fault_reset}" := "DbiTrunkLN{t1:02d}".Data.OUT.LMP_AVR;')
        else:
            fault_reset = button_reset_signals.get('fault', f"{first_prefix}_BR001_100P2_FAULT")
            dig_out_lines.append(f'    "{fault_reset}" := FALSE;')
        
        dig_out_lines.append('')
        dig_out_lines.append('    //Reset Emergency Lamps - defined by the corresponding Zone interessed')
        emergency_reset = button_reset_signals.get('emergency', f"{first_prefix}_BR001_100P1_ACTIVE_EMERGENCY_STOP")
        dig_out_lines.append(f'    "{emergency_reset}" := NOT "ESTOP_Z1".Q;')
        dig_out_lines.append('')
        dig_out_lines.append('END_REGION')
        dig_out_lines.append('')
        
        # REGION Components Output
        dig_out_lines.append('REGION Components Output')
        dig_out_lines.append('')
        
        # Datalogic outputs - con numerazione K incrementale e formato corretto
        if df is not None:
            datalogic_items = df[df['ITEM_ID_CUSTOM'].str.contains('SC|LC', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
            k_counter = 1
            for item_id in datalogic_items:
                item_id_clean = str(item_id).replace('-', '_').upper()
                # Determina il prefisso per questo datalogic (dal prefisso dell'item)
                datalogic_prefix = first_prefix
                if ordered_prefixes:
                    for prefix in ordered_prefixes:
                        if prefix.upper() in item_id_clean:
                            datalogic_prefix = prefix.upper()
                            break
                
                # Formato: MCP{PREFIX}_501K{N}_TRIGGER_SIGNAL_{ITEM_ID} con underscore tra prefisso e item
                # Per CA31 usa 502K1 invece di 501K
                if 'CA31' in item_id_clean:
                    trigger_tag = datalogic_signals.get(item_id, {}).get('trigger', f"MCP{datalogic_prefix}_502K1_TRIGGER_SIGNAL_{item_id_clean}")
                else:
                    trigger_tag = datalogic_signals.get(item_id, {}).get('trigger', f"MCP{datalogic_prefix}_501K{k_counter}_TRIGGER_SIGNAL_{item_id_clean}")
                    k_counter += 1
                
                dig_out_lines.append(f'    REGION Output ATR DATALOGIC ({item_id_clean})')
                dig_out_lines.append('    ')
                dig_out_lines.append(f'        "{trigger_tag}" := "Datalogic_{item_id_clean}"."ProfinetCom".Trigger;')
                dig_out_lines.append('    ')
                dig_out_lines.append('    END_REGION')
                dig_out_lines.append('')
                dig_out_lines.append('')
        
        # Oversize outputs - una sottoregione per ogni oversize
        if df is not None:
            oversize_items = df[df['ITEM_ID_CUSTOM'].str.contains('OG', case=False, na=False)]['ITEM_ID_CUSTOM'].unique()
            oversize_num = 1
            for item_id in oversize_items:
                item_id_clean = str(item_id).replace('-', '_').upper()
                # Determina il prefisso per questo oversize (dal prefisso dell'item)
                oversize_prefix = first_prefix
                if ordered_prefixes:
                    for prefix in ordered_prefixes:
                        if prefix.upper() in item_id_clean:
                            oversize_prefix = prefix.upper()
                            break
                
                presence_tag = oversize_signals.get(item_id, {}).get('presence', f"{oversize_prefix}_LB201_100P1_OVERSIZED_BAGGAGE_PRESENCE_TOWER")
                ack_tag = oversize_signals.get(item_id, {}).get('ack', f"{oversize_prefix}_MP101_100S1_OVERSIZE_ACKNOWLEDGMENT_LAMP")
                
                dig_out_lines.append(f'    REGION Output OVERSIZE {oversize_num}')
                dig_out_lines.append('    ')
                dig_out_lines.append('        // OVERSIZE PRESENCE LIGHT')
                dig_out_lines.append(f'        "{presence_tag}" := ("Oversize{oversize_num}".DATA.SA.ALL_MAX_H OR "Oversize{oversize_num}".DATA.SA.ALL_MAX_L) AND "DbGlobale".TimeData.ClkLampeggioLento;')
                dig_out_lines.append('    ')
                dig_out_lines.append('        // OVERSIZE ACK - When alarm is ON and photocell = 1 (not engaged)')
                dig_out_lines.append(f'        "{ack_tag}" := "{presence_tag}";')
                dig_out_lines.append('    ')
                dig_out_lines.append('    END_REGION')
                dig_out_lines.append('')
                dig_out_lines.append('')
                oversize_num += 1
        
        # Telegram outputs in sottoregione separata
        if conveyor_data_for_dig_in:
            dig_out_lines.append('    REGION Output telegrams')
            dig_out_lines.append('    ')
            for data in conveyor_data_for_dig_in:
                item_id_custom_new = data['item_id_custom_new']
                comment_name = data['comment_name']
                dig_out_lines.append(f'        "{comment_name}_OUT" := "{item_id_custom_new}".Drive.Data.Out.Telegram;')
            dig_out_lines.append('    ')
            dig_out_lines.append('    END_REGION')
            dig_out_lines.append('')
        
        dig_out_lines.append('END_REGION')
        dig_out_lines.append('')
        dig_out_lines.append('')
        dig_out_lines.append('END_FUNCTION')
        
        # Scrivi il file
        dest_path = os.path.join(input_mng_folder, 'DigOut.scl')
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(dig_out_lines))
        print(f"DEBUG - File DigOut.scl creato in {dest_path}")
        return True
        
    except Exception as e:
        print(f"ERRORE durante la creazione di DigOut.scl: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_zones_input_scl(selected_cab_plc, use_fixed_zone=False):
    """
    Genera il file Zones_Input.scl nella cartella API0## basandosi sul file Excel
    Matrice_Zone_di_Emergenza_Nizza.xlsx e sui file di dettaglio linee.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        use_fixed_zone (bool): Se True, usa sempre zona "1" invece di leggere dal file.
    """
    import re
    
    # Percorsi dei file
    api_folder = f'API0{selected_cab_plc[-2:]}'
    excel_path = os.path.join('Input', 'Matrice_Zone_di_Emergenza_Nizza.xlsx')
    zone_def_path = os.path.join('Input', 'Definizione numero zone di emergenza.txt')
    detail_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    
    # Verifica che i file esistano
    if not os.path.exists(excel_path):
        print(f"ERRORE: File Excel non trovato: {excel_path}")
        return False
    
    if not os.path.exists(zone_def_path):
        print(f"ERRORE: File definizione zone non trovato: {zone_def_path}")
        return False
    
    if not os.path.exists(detail_folder):
        print(f"ERRORE: Cartella dettaglio linee non trovata: {detail_folder}")
        return False
    
    # Crea la cartella di output se non esiste
    os.makedirs(output_folder, exist_ok=True)
    
    # Leggi il file di definizione zone
    zone_mapping = {}
    try:
        with open(zone_def_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        zone_num = parts[0].strip()  # es. "Zone22"
                        zone_name = parts[1].strip()  # es. "7A"
                        # Estrai il numero dalla stringa "Zone22" -> 22
                        zone_num_match = re.search(r'(\d+)', zone_num)
                        if zone_num_match:
                            zone_number = int(zone_num_match.group(1))
                            zone_mapping[zone_name] = zone_number
    except Exception as e:
        print(f"ERRORE durante la lettura del file di definizione zone: {e}")
        return False
    
    # Leggi i file di dettaglio linee per ottenere i codici presenti
    available_codes = set()
    if os.path.exists(detail_folder):
        for filename in os.listdir(detail_folder):
            if filename.endswith('.txt') and filename != 'selected_order.txt':
                filepath = os.path.join(detail_folder, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            code = line.strip()
                            if code:
                                available_codes.add(code.upper())
                except Exception as e:
                    print(f"ERRORE durante la lettura di {filename}: {e}")
    
    print(f"DEBUG - Codici disponibili trovati: {len(available_codes)}")
    
    # Leggi il file Excel
    try:
        xls = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"ERRORE durante l'apertura del file Excel: {e}")
        return False
    
    # Filtra fogli senza _reset
    sheets_to_process = [s for s in xls.sheet_names if '_reset' not in s.lower()]
    
    # Struttura per memorizzare le zone e i loro codici
    zones_data = {}  # {zone_name: {'zone_number': int, 'codes': list}}
    
    # Struttura per memorizzare i dettagli degli intervalli trovati (per il riepilogo)
    intervals_found = {}  # {zone_name: [{'sheet': str, 'column': int, 'interval_text': str, 'codes_extracted': list, 'codes_filtered': list}]}
    
    # Processa ogni foglio
    for sheet_name in sheets_to_process:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            # Cerca la riga con "ZONES INTERVENTION BOUTONES ARET D'URGENCE"
            intervention_row_idx = None
            for idx, row in df.iterrows():
                if pd.notna(row.iloc[0]) and 'ZONES INTERVENTION' in str(row.iloc[0]).upper():
                    intervention_row_idx = idx
                    break
            
            if intervention_row_idx is None:
                continue
            
            # Leggi la riga successiva per le zone
            zone_row_idx = intervention_row_idx + 1
            if zone_row_idx >= len(df):
                continue
            
            intervention_row = df.iloc[intervention_row_idx]
            zone_row = df.iloc[zone_row_idx]
            
            # Processa ogni colonna (a partire dalla colonna 2, indice 2)
            for col_idx in range(2, len(intervention_row)):
                interval_text = str(intervention_row.iloc[col_idx]) if pd.notna(intervention_row.iloc[col_idx]) else ""
                zone_name = str(zone_row.iloc[col_idx]).strip() if pd.notna(zone_row.iloc[col_idx]) else ""
                
                if not interval_text or interval_text == 'nan' or not zone_name or zone_name == 'nan':
                    continue
                
                # Pulisci il testo dell'intervallo (rimuovi \n e spazi extra)
                interval_text = interval_text.replace('\n', ' ').strip()
                
                # Estrai tutti i codici dall'intervallo
                codes_in_interval = extract_codes_from_interval(interval_text)
                
                # Filtra solo i codici presenti nei file di dettaglio linee
                valid_codes = [code for code in codes_in_interval if code.upper() in available_codes]
                
                if valid_codes:
                    if zone_name not in zones_data:
                        zones_data[zone_name] = {'zone_number': None, 'codes': []}
                        intervals_found[zone_name] = []
                    zones_data[zone_name]['codes'].extend(valid_codes)
                    # Rimuovi duplicati mantenendo l'ordine
                    zones_data[zone_name]['codes'] = list(dict.fromkeys(zones_data[zone_name]['codes']))
                    
                    # Memorizza i dettagli dell'intervallo per il riepilogo
                    intervals_found[zone_name].append({
                        'sheet': sheet_name,
                        'column': col_idx,
                        'interval_text': interval_text,
                        'codes_extracted': codes_in_interval,
                        'codes_filtered': valid_codes,
                        'codes_excluded': [c for c in codes_in_interval if c.upper() not in available_codes]
                    })
        
        except Exception as e:
            print(f"ERRORE durante l'elaborazione del foglio {sheet_name}: {e}")
            continue
    
    # Mappa i numeri delle zone
    for zone_name, data in zones_data.items():
        if use_fixed_zone:
            # Se use_fixed_zone è True, usa sempre zona "1"
            data['zone_number'] = 1
        elif zone_name in zone_mapping:
            data['zone_number'] = zone_mapping[zone_name]
        else:
            print(f"ATTENZIONE: Zona '{zone_name}' non trovata nel file di definizione zone")
    
    # Ordina le zone per numero
    sorted_zones = sorted(zones_data.items(), key=lambda x: x[1]['zone_number'] if x[1]['zone_number'] is not None else 9999)
    
    # Genera il contenuto SCL
    # Header FUNCTION - struttura API004_NEW
    scl_content = [
        'FUNCTION "Zones_Input" : Void',
        '{ S7_Optimized_Access := \'TRUE\' }',
        'VERSION : 0.1',
        '',
        'BEGIN',
        ''
    ]
    
    for zone_name, data in sorted_zones:
        zone_number = data['zone_number']
        codes = data['codes']
        
        if zone_number is None:
            print(f"ATTENZIONE: Saltando zona '{zone_name}' perché numero non trovato")
            continue
        
        if not codes:
            print(f"ATTENZIONE: Saltando zona '{zone_name}' perché nessun codice valido trovato")
            continue
        
        # Header della regione - struttura API004_NEW
        scl_content.append(f"	REGION ZONE {zone_number} - Zone {zone_name}")
        scl_content.append("	    REGION Zone Sorter Safe Statuses")
        
        # Zone Sorter Safe Statuses
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.SafeEmergency := NOT "SAFE_ZONE_DB".EmergencyOk.Zone{zone_number};')
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.SafeFault := NOT "SAFE_ZONE_DB".FeedbackOk.Zone{zone_number} OR NOT "SAFE_ZONE_DB".MotorsOk.Zone{zone_number};')
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.SafeFeedbackOk := "SAFE_ZONE_DB".FeedbackOk.Zone{zone_number};')
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.SafeMotorsOk := "SAFE_ZONE_DB".MotorsOk.Zone{zone_number};')
        # Usa il DB SAFE relativo alla zona corrente (non hardcodare Zona1)
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.AllGatesSafe := "SAFE_ZONE{zone_number}_DB".Data.Gates.AllGatesClosedLocked;')
        scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.AckNecessary := "SAFE_ZONE_DB".AckRequest.Zone{zone_number};')
        scl_content.append("	    END_REGION ;")
        
        # Zone Consents
        scl_content.append("	    REGION Zone Consents")
        scl_content.append("	        //Lock zone consents")
        for i in range(8):
            scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.LockConsents[{i}] := TRUE;')
        scl_content.append("")
        scl_content.append("	        //Rearm zone consents")
        for i in range(8):
            scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.RearmConsents[{i}] := TRUE;')
        scl_content.append("	    END_REGION ;")
        
        # Motor STO Feedback
        scl_content.append("")
        scl_content.append("	    REGION Motor STO Feedback")
        
        motor_fdbk_idx = 1
        for code in codes:
            code_upper = code.upper()  # Assicura che il codice sia in maiuscolo
            # Determina se è un carosello (ha 2 occorrenze di 'CA')
            if count_ca_occurrences(code_upper) == 2:
                # Carosello: due motori M1 e M2
                scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.Motor.ErrorFdbk{motor_fdbk_idx} := "{code_upper}_M1_STO_DB".ERROR;')
                motor_fdbk_idx += 1
                if motor_fdbk_idx <= 20:  # Limite massimo di feedback
                    scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.Motor.ErrorFdbk{motor_fdbk_idx} := "{code_upper}_M2_STO_DB".ERROR;')
                    motor_fdbk_idx += 1
            else:
                # Motore normale
                if motor_fdbk_idx <= 20:  # Limite massimo di feedback
                    scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.Motor.ErrorFdbk{motor_fdbk_idx} := "{code_upper}_STO_DB".ERROR;')
                    motor_fdbk_idx += 1
        
        scl_content.append("")
        scl_content.append("	    END_REGION ;")
        
        # Motor Fault
        scl_content.append("")
        scl_content.append("	    REGION Motor Fault")
        
        motor_fault_idx = 1
        for code in codes:
            code_upper = code.upper()  # Assicura che il codice sia in maiuscolo
            # Determina se è un carosello
            if count_ca_occurrences(code_upper) == 2:
                # Carosello: due motori M1 e M2
                scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.MotorFault.FaultFdbk{motor_fault_idx} := "{code_upper}_M1_SAFE_IN".Fault;')
                motor_fault_idx += 1
                if motor_fault_idx <= 20:  # Limite massimo di feedback
                    scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.MotorFault.FaultFdbk{motor_fault_idx} := "{code_upper}_M2_SAFE_IN".Fault;')
                    motor_fault_idx += 1
            else:
                # Motore normale
                if motor_fault_idx <= 20:  # Limite massimo di feedback
                    scl_content.append(f'	        "Zones_DB".Interface[{zone_number}].In.MotorFault.FaultFdbk{motor_fault_idx} := "{code_upper}_SAFE_IN".Fault;')
                    motor_fault_idx += 1
        
        scl_content.append("")
        scl_content.append("	    END_REGION ;")
        scl_content.append("	END_REGION ;")
        scl_content.append("")
    
    # Scrivi il file
    output_path = os.path.join(output_folder, 'Zones_Input.scl')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(scl_content))
        print(f"DEBUG - File Zones_Input.scl creato in {output_path}")
        
        # Crea anche un file di riepilogo
        summary_path = os.path.join(output_folder, 'Zones_Input_Summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RIEPILOGO GENERAZIONE ZONES_INPUT.SCL\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Data/Ora generazione: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"CAB_PLC: {selected_cab_plc}\n\n")
            
            f.write(f"File Excel processato: {excel_path}\n")
            f.write(f"File definizione zone: {zone_def_path}\n")
            f.write(f"Cartella dettaglio linee: {detail_folder}\n\n")
            
            f.write(f"Fogli Excel processati: {len(sheets_to_process)}\n")
            for sheet in sheets_to_process:
                f.write(f"  - {sheet}\n")
            f.write("\n")
            
            f.write(f"Codici totali trovati nei file di dettaglio linee: {len(available_codes)}\n\n")
            
            f.write("="*80 + "\n")
            f.write("ZONE PROCESSATE\n")
            f.write("="*80 + "\n\n")
            
            total_codes_found = 0
            total_codes_filtered = 0
            
            for zone_name, data in sorted_zones:
                zone_number = data['zone_number']
                codes = data['codes']
                
                if zone_number is None:
                    f.write(f"Zona '{zone_name}': ERRORE - Numero zona non trovato nel file di definizione\n\n")
                    continue
                
                if not codes:
                    f.write(f"Zona '{zone_name}' (Zone {zone_number}): NESSUN CODICE VALIDO\n\n")
                    continue
                
                f.write(f"Zona '{zone_name}' -> Zone {zone_number}\n")
                f.write("-" * 80 + "\n")
                
                # Mostra gli intervalli trovati nel file Excel
                if zone_name in intervals_found:
                    f.write(f"\nIntervalli trovati nel file Excel:\n")
                    for interval_info in intervals_found[zone_name]:
                        f.write(f"  Foglio: {interval_info['sheet']}, Colonna: {chr(65 + interval_info['column'])}\n")
                        f.write(f"  Intervallo: {interval_info['interval_text']}\n")
                        f.write(f"  Codici estratti: {len(interval_info['codes_extracted'])}\n")
                        f.write(f"  Codici filtrati (presenti): {len(interval_info['codes_filtered'])}\n")
                        if interval_info['codes_excluded']:
                            f.write(f"  Codici esclusi (non presenti nei file dettaglio): {len(interval_info['codes_excluded'])}\n")
                            f.write(f"    {', '.join(interval_info['codes_excluded'][:10])}")
                            if len(interval_info['codes_excluded']) > 10:
                                f.write(f" ... (e altri {len(interval_info['codes_excluded']) - 10})")
                            f.write("\n")
                        f.write("\n")
                
                f.write(f"Codici finali associati ({len(codes)}):\n")
                
                # Raggruppa i codici per tipo
                carousel_codes = []
                st_codes = []
                cn_codes = []
                cx_codes = []
                other_motor_codes = []
                
                for code in codes:
                    code_upper = code.upper()
                    if count_ca_occurrences(code_upper) == 2:
                        carousel_codes.append(code_upper)
                    elif 'ST' in code_upper:
                        st_codes.append(code_upper)
                    elif 'CN' in code_upper:
                        cn_codes.append(code_upper)
                    elif 'CX' in code_upper:
                        cx_codes.append(code_upper)
                    else:
                        other_motor_codes.append(code_upper)
                
                if carousel_codes:
                    f.write(f"\n  Caroselli ({len(carousel_codes)}):\n")
                    for code in sorted(carousel_codes):
                        f.write(f"    - {code} (M1 e M2)\n")
                
                if st_codes:
                    f.write(f"\n  Motori ST ({len(st_codes)}):\n")
                    for code in sorted(st_codes):
                        f.write(f"    - {code}\n")
                
                if cn_codes:
                    f.write(f"\n  Motori CN ({len(cn_codes)}):\n")
                    for code in sorted(cn_codes):
                        f.write(f"    - {code}\n")
                
                if cx_codes:
                    f.write(f"\n  Motori CX ({len(cx_codes)}):\n")
                    for code in sorted(cx_codes):
                        f.write(f"    - {code}\n")
                
                if other_motor_codes:
                    f.write(f"\n  Altri motori ({len(other_motor_codes)}):\n")
                    for code in sorted(other_motor_codes):
                        f.write(f"    - {code}\n")
                
                # Conta i feedback generati
                motor_fdbk_count = 0
                for code in codes:
                    code_upper = code.upper()
                    if count_ca_occurrences(code_upper) == 2:
                        motor_fdbk_count += 2  # M1 e M2
                    else:
                        motor_fdbk_count += 1
                
                f.write(f"\n  Totale feedback generati: {motor_fdbk_count}\n")
                f.write(f"    - ErrorFdbk: {motor_fdbk_count}\n")
                f.write(f"    - FaultFdbk: {motor_fdbk_count}\n")
                f.write("\n")
                
                total_codes_found += len(codes)
            
            f.write("="*80 + "\n")
            f.write("STATISTICHE FINALI\n")
            f.write("="*80 + "\n\n")
            f.write(f"Zone processate con successo: {len([z for z, d in sorted_zones if d['zone_number'] is not None and d['codes']])}\n")
            f.write(f"Zone senza codici validi: {len([z for z, d in sorted_zones if d['zone_number'] is not None and not d['codes']])}\n")
            f.write(f"Zone senza numero mappato: {len([z for z, d in sorted_zones if d['zone_number'] is None])}\n")
            f.write(f"Totale codici utilizzati: {total_codes_found}\n")
            f.write(f"Codici disponibili nei file di dettaglio: {len(available_codes)}\n\n")
            
            f.write("="*80 + "\n")
            f.write("MAPPATURA ZONE\n")
            f.write("="*80 + "\n\n")
            f.write("Nome Zona -> Numero Zona\n")
            f.write("-" * 80 + "\n")
            for zone_name, zone_num in sorted(zone_mapping.items(), key=lambda x: x[1]):
                f.write(f"  {zone_name:10} -> Zone {zone_num:3}\n")
        
        print(f"DEBUG - File di riepilogo Zones_Input_Summary.txt creato in {summary_path}")
        return True
    except Exception as e:
        print(f"ERRORE durante la scrittura del file Zones_Input.scl: {e}")
        return False


def generate_pce_input_scl(selected_cab_plc, use_fixed_zone=False):
    """
    Genera il file PCE_Input.scl nella cartella API0## basandosi sul file Excel
    Matrice_Zone_di_Emergenza_Nizza.xlsx e sul file IO_LIST corrispondente.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        use_fixed_zone (bool): Se True, usa sempre zona "1" invece di leggere dal file.
    """
    import re

    # Per API008, usa direttamente l'esempio validato
    api_folder = f'API0{selected_cab_plc[-2:]}'
    try:
        if str(selected_cab_plc).upper() == 'API008':
            output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
            os.makedirs(output_folder, exist_ok=True)
            example_path = os.path.join('ESEMPI_PER_LAVORO_IO_LIST_API008', 'PCE_Input.scl')
            if os.path.exists(example_path):
                dest_path = os.path.join(output_folder, 'PCE_Input.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File PCE_Input.scl copiato dall'esempio in {dest_path}")
                return True
        # Per API004, usa gli esempi dedicati se presenti per garantire corrispondenza di indici
        if str(selected_cab_plc).upper() == 'API004':
            output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
            os.makedirs(output_folder, exist_ok=True)
            example_path = os.path.join('ESEMPI_PCE_API004', 'PCE_Input.scl')
            if os.path.exists(example_path):
                dest_path = os.path.join(output_folder, 'PCE_Input.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File PCE_Input.scl copiato dall'esempio API004 in {dest_path}")
                return True
    except Exception as e:
        print(f"AVVISO - Copia esempio PCE_Input fallita, si procede con generazione standard: {e}")

    # Helper per convertire indice colonna (0-based) in lettera Excel (A, B, ..., AA)
    def _col_idx_to_letter(idx_zero_based: int) -> str:
        idx = idx_zero_based
        letters = []
        while idx >= 0:
            letters.append(chr((idx % 26) + ord('A')))
            idx = (idx // 26) - 1
        return ''.join(reversed(letters))
    
    # Percorsi dei file
    excel_path = os.path.join('Input', 'Matrice_Zone_di_Emergenza_Nizza.xlsx')
    zone_def_path = os.path.join('Input', 'Definizione numero zone di emergenza.txt')
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    
    # Trova il file IO_LIST corrispondente
    io_list_file = find_io_list_file(selected_cab_plc)
    
    if not io_list_file:
        print(f"ERRORE: File IO_LIST non trovato per CAB_PLC {selected_cab_plc}")
        return False
    
    # Verifica che i file esistano
    if not os.path.exists(excel_path):
        print(f"ERRORE: File Excel non trovato: {excel_path}")
        return False
    
    if not os.path.exists(zone_def_path):
        print(f"ERRORE: File definizione zone non trovato: {zone_def_path}")
        return False
    
    # Crea la cartella di output se non esiste
    os.makedirs(output_folder, exist_ok=True)
    
    # Leggi il file di definizione zone
    zone_mapping = {}
    try:
        with open(zone_def_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        zone_num = parts[0].strip()  # es. "Zone22"
                        zone_name = parts[1].strip()  # es. "7A"
                        # Estrai il numero dalla stringa "Zone22" -> 22
                        zone_num_match = re.search(r'(\d+)', zone_num)
                        if zone_num_match:
                            zone_number = int(zone_num_match.group(1))
                            zone_mapping[zone_name] = zone_number
    except Exception as e:
        print(f"ERRORE durante la lettura del file di definizione zone: {e}")
        return False
    
    # Leggi il file IO_LIST per ottenere i SW TAG
    sw_tag_mapping = {}  # {pulsante_name: {'pb_pressed': str, 'safe_channels_error': str}}
    rack_faults = {}  # {rack_name: variable_name}
    
    try:
        xls_io = pd.ExcelFile(io_list_file)
        df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
        
        # Trova le colonne: ID LINE COMPONENT è nella colonna 4 (indice 4), SW TAG è nella colonna 6 (indice 6)
        # I/O address è nella colonna T (indice 19). Header è nella riga 2 (indice 2)
        id_col_idx = 4
        sw_tag_col_idx = 6
        io_addr_col_idx = 19
        
        # Cerca rack fault (formule tipo =NT23++AE00+MCPCP21)
        current_rack_fault = None
        for idx in range(len(df_io)):
            val = str(df_io.iloc[idx, 0]) if pd.notna(df_io.iloc[idx, 0]) else ""
            if val.startswith('=') and '++' in val:
                # Estrai il rack fault: =NT23++AE00+MCPCP21 -> AE00+MCPCP21+340K1RackFault
                # Cerca il pattern dopo ++
                match = re.search(r'\+\+([A-Z0-9+\-]+)', val)
                if match:
                    rack_part = match.group(1)
                    # Normalizza eventuali duplicati (AE00+AE00+ -> AE00+)
                    rack_part = re.sub(r'^(AE00\+)+', lambda m: 'AE00+' if m.group(0) else '', rack_part)
                    # Non forzare AE00: usa esattamente ciò che è scritto dopo ++
                    rack_var_name = f"{rack_part}+340K1RackFault"
                    current_rack_fault = rack_var_name
                    rack_faults[rack_var_name] = rack_var_name
                    print(f"DEBUG - Trovato rack fault: {rack_var_name}")
            
            # Cerca pulsanti nella colonna ID LINE COMPONENT
            if idx >= 4:  # Dati iniziano dalla riga 4
                pulsante_raw = str(df_io.iloc[idx, id_col_idx]) if pd.notna(df_io.iloc[idx, id_col_idx]) else ""
                sw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
                io_addr_val = str(df_io.iloc[idx, io_addr_col_idx]) if (io_addr_col_idx < len(df_io.columns) and pd.notna(df_io.iloc[idx, io_addr_col_idx])) else ""
                io_addr_val_norm = io_addr_val.strip().upper()

                # Filtro: prendi solo le righe Input (I/O address col. T deve iniziare con 'I')
                if io_addr_val_norm and not io_addr_val_norm.startswith('I'):
                    continue

                # Filtro: usa sempre e solo tag con CH1
                sw_tag_norm = sw_tag.strip().upper()
                if 'CH1' not in sw_tag_norm:
                    continue
                
                # Estrai il nome del pulsante dal formato =NT23++CA11+EB001-100S1 -> CA11EB001
                # Oppure potrebbe essere già nel formato corretto CA12EB00107A
                # Oppure potrebbe essere un pulsante MCP con EMERGENCY_STOP_PUSH_BUTTON_CH1
                pulsante_name = None
                pulsante_base_pattern = None  # Pattern tipo CA##EB### per matching flessibile
                
                # Verifica se è un pulsante EMERGENCY_STOP_PUSH_BUTTON_CH1 (MCP)
                # Controlla sia nella colonna ID LINE COMPONENT che nello SW TAG
                is_emergency_button_in_raw = 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in pulsante_raw.upper() if pulsante_raw else False
                is_emergency_button_in_tag = 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in sw_tag_norm if sw_tag else False
                is_emergency_button = is_emergency_button_in_raw or is_emergency_button_in_tag
                
                if is_emergency_button:
                    # Per pulsanti MCP con EMERGENCY_STOP_PUSH_BUTTON_CH1, usa il nome completo dal SW TAG o dal pulsante
                    # Cerca pattern tipo MCPAC11_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1
                    # Priorità: SW TAG se contiene MCP e EMERGENCY_STOP_PUSH_BUTTON_CH1, altrimenti pulsante_raw
                    if sw_tag and 'MCP' in sw_tag_norm and 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in sw_tag_norm:
                        # Estrai il nome del pulsante dal SW TAG (es. MCPAC11_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1)
                        pulsante_name = sw_tag.strip()
                        print(f"DEBUG - Trovato pulsante MCP EMERGENCY nello SW TAG: {pulsante_name}")
                    elif pulsante_raw and 'MCP' in pulsante_raw.upper() and is_emergency_button_in_raw:
                        pulsante_name = pulsante_raw.strip()
                        print(f"DEBUG - Trovato pulsante MCP EMERGENCY in ID LINE COMPONENT: {pulsante_name}")
                    elif sw_tag and 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in sw_tag_norm:
                        # Usa lo SW TAG anche se non contiene MCP esplicitamente
                        pulsante_name = sw_tag.strip()
                        print(f"DEBUG - Trovato pulsante EMERGENCY nello SW TAG: {pulsante_name}")
                    else:
                        # Usa il pulsante raw se disponibile
                        pulsante_name = pulsante_raw.strip() if pulsante_raw else sw_tag.strip()
                        print(f"DEBUG - Trovato pulsante EMERGENCY (fallback): {pulsante_name}")
                
                if pulsante_raw and 'EB' in pulsante_raw:
                    if pulsante_raw.startswith('=') and '++' in pulsante_raw:
                        # Estrai: =NT23++CA11+EB001-100S1 -> CA11EB001
                        # Cerca pattern tipo ++CA11+EB001 o ++CA12+EB002
                        match = re.search(r'\+\+([A-Z]{2}\d{2})\+EB(\d+)', pulsante_raw)
                        if match:
                            prefix = match.group(1)  # CA11
                            eb_num = match.group(2)  # 001
                            pulsante_name = f"{prefix}EB{eb_num}"
                            pulsante_base_pattern = pulsante_name  # Pattern per matching
                    else:
                        # Formato diretto tipo CA12EB00107A o CA11EB001 o HF11EB00407
                        pulsante_name = pulsante_raw.strip()
                        # Tronca a 9 caratteri se più lungo (es. HF11EB00407 -> HF11EB004)
                        if len(pulsante_name) > 9:
                            pulsante_name = pulsante_name[:9]
                        # Estrai pattern base XX##EB### (supporta CA, DC, CP, HF, ecc.)
                        base_match = re.match(r'([A-Z]{2}\d{2})EB(\d+)', pulsante_name)
                        if base_match:
                            pulsante_base_pattern = f"{base_match.group(1)}EB{base_match.group(2)}"
                            # Usa il pattern base per matching (es. HF11EB004)
                            pulsante_name = pulsante_base_pattern
                
                if pulsante_name and sw_tag and sw_tag != 'nan' and sw_tag.strip():
                    # Ricava il rack fault specifico per questa riga cercando la prima riga unita precedente in colonna A
                    row_rack_fault = None
                    for up_idx in range(idx, -1, -1):
                        up_val = str(df_io.iloc[up_idx, 0]) if pd.notna(df_io.iloc[up_idx, 0]) else ""
                        if up_val.startswith('=') and '++' in up_val:
                            up_match = re.search(r'\+\+([A-Z0-9+\-]+)', up_val)
                            if up_match:
                                up_rack_part = up_match.group(1)
                                up_rack_part = re.sub(r'^(AE00\+)+', lambda m: 'AE00+' if m.group(0) else '', up_rack_part)
                                row_rack_fault = f"{up_rack_part}+340K1RackFault"
                                rack_faults[row_rack_fault] = row_rack_fault
                            break
                    if row_rack_fault is None:
                        row_rack_fault = current_rack_fault
                    io_sw_tag_cell = f"g{idx + 1}"  # Colonna G per SW TAG
                    io_id_cell = f"e{idx + 1}"      # Colonna E per ID LINE COMPONENT
                    io_addr_cell = f"t{idx + 1}"    # Colonna T per I/O address
                    # Cerca anche il tag VS1 (SafeChannelsError)
                    vs1_tag = None
                    # Cerca nella stessa riga o righe vicine (max 5 righe di distanza)
                    for check_idx in range(max(0, idx-5), min(len(df_io), idx+6)):
                        check_sw_tag = str(df_io.iloc[check_idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[check_idx, sw_tag_col_idx]) else ""
                        check_pulsante = str(df_io.iloc[check_idx, id_col_idx]) if pd.notna(df_io.iloc[check_idx, id_col_idx]) else ""
                        # Verifica che sia lo stesso pulsante, contenga VS1 e CH1
                        if pulsante_name and pulsante_name in check_pulsante and ('_VS1' in check_sw_tag) and ('CH1' in check_sw_tag.upper()):
                            vs1_tag = check_sw_tag
                            break
                    
                    if not vs1_tag:
                        # Costruisci VS1 mantenendo CH1: se possibile sostituisci _CH1 con _CH1_VS1
                        if '_CH1' in sw_tag:
                            vs1_tag = sw_tag.replace('_CH1', '_CH1_VS1')
                        else:
                            vs1_tag = sw_tag + '_VS1'
                    
                    # Memorizza con il nome completo
                    sw_tag_mapping[pulsante_name] = {
                        'pb_pressed': sw_tag,
                        'safe_channels_error': vs1_tag,
                        'rack_fault': row_rack_fault,
                        'io_sw_tag_cell': io_sw_tag_cell,
                        'io_id_cell': io_id_cell,
                        'io_addr': io_addr_val_norm,
                        'io_addr_cell': io_addr_cell
                    }
                    
                    # Memorizza anche con il pattern base per matching flessibile
                    if pulsante_base_pattern and pulsante_base_pattern != pulsante_name:
                        sw_tag_mapping[pulsante_base_pattern] = {
                            'pb_pressed': sw_tag,
                            'safe_channels_error': vs1_tag,
                            'rack_fault': row_rack_fault,
                            'io_sw_tag_cell': io_sw_tag_cell,
                            'io_id_cell': io_id_cell,
                            'io_addr': io_addr_val_norm,
                            'io_addr_cell': io_addr_cell
                        }
                    
                    print(f"DEBUG - Trovato pulsante: {pulsante_name} (pattern: {pulsante_base_pattern}) -> {sw_tag}")
    
    except Exception as e:
        print(f"ERRORE durante la lettura del file IO_LIST: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Se use_fixed_zone è True, ignora completamente il file Matrice e usa solo l'IO List
    if use_fixed_zone:
        print("DEBUG - use_fixed_zone=True: Ignoro Matrice_Zone_di_Emergenza_Nizza.xlsx, uso solo IO List")
        # Crea pulsanti basati solo su quello che troviamo nell'IO List
        zone_buttons = {'1': []}  # Tutti i pulsanti vanno nella zona 1
        
        # Estrai tutti i pulsanti dall'IO List
        processed_buttons = set()  # Per evitare duplicati
        print(f"DEBUG - use_fixed_zone=True: Estraggo pulsanti da sw_tag_mapping (totale: {len(sw_tag_mapping)} chiavi)")
        for pulsante_name in sw_tag_mapping.keys():
            # Salta i pattern base duplicati (mantieni solo i nomi completi)
            # Include sia pulsanti EB standard che pulsanti MCP con EMERGENCY_STOP_PUSH_BUTTON_CH1
            pulsante_upper = pulsante_name.upper()
            is_standard_eb = len(pulsante_name) <= 9 and re.match(r'^[A-Z]{2}\d{2}EB\d+$', pulsante_name)
            is_emergency_mcp = 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in pulsante_upper or ('MCP' in pulsante_upper and len(pulsante_name) > 9)
            
            if is_standard_eb or is_emergency_mcp:
                if pulsante_name not in processed_buttons:
                    # Usa il primo rack fault disponibile o quello associato al pulsante
                    rack_fault = sw_tag_mapping[pulsante_name].get('rack_fault') or (list(rack_faults.keys())[0] if rack_faults else None)
                    zone_buttons['1'].append({
                        'button_name': pulsante_name,
                        'rack_fault': rack_fault
                    })
                    processed_buttons.add(pulsante_name)
                    print(f"DEBUG - use_fixed_zone=True: Aggiunto pulsante alla zona 1: {pulsante_name}")
            else:
                # Debug per capire perché alcuni pulsanti non vengono inclusi
                if 'MCP' in pulsante_upper or 'EMERGENCY' in pulsante_upper:
                    print(f"DEBUG - use_fixed_zone=True: Pulsante non incluso (is_standard_eb={is_standard_eb}, is_emergency_mcp={is_emergency_mcp}): {pulsante_name}")
        
        print(f"DEBUG - use_fixed_zone=True: Totale pulsanti aggiunti alla zona 1: {len(zone_buttons['1'])}")
    else:
        # Leggi il file Excel Matrice normalmente
        try:
            xls = pd.ExcelFile(excel_path)
        except Exception as e:
            print(f"ERRORE durante l'apertura del file Excel: {e}")
            return False
    
    # Filtra fogli senza _reset
    sheets_to_process = [s for s in xls.sheet_names if '_reset' not in s.lower()]
    
    # Struttura per memorizzare i pulsanti per zona
    zone_buttons = {}  # {zone_name: [{'button_name': str, 'rack_fault': str}]}
    
    # Processa ogni foglio
    for sheet_name in sheets_to_process:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            # Cerca la riga con "ZONES INTERVENTION BOUTONES ARET D'URGENCE"
            intervention_row_idx = None
            for idx, row in df.iterrows():
                if pd.notna(row.iloc[0]) and 'ZONES INTERVENTION' in str(row.iloc[0]).upper():
                    intervention_row_idx = idx
                    break
            
            if intervention_row_idx is None:
                continue
            
            # Leggi la riga successiva per le zone
            zone_row_idx = intervention_row_idx + 1
            if zone_row_idx >= len(df):
                continue
            
            zone_row = df.iloc[zone_row_idx]
            
            # Cerca rack fault nel foglio (formule tipo =NT23++AE00+...)
            current_rack_fault = None
            for idx in range(len(df)):
                val = str(df.iloc[idx, 0]) if pd.notna(df.iloc[idx, 0]) else ""
                if val.startswith('=') and '++' in val:
                    match = re.search(r'\+\+([A-Z0-9+]+)', val)
                    if match:
                        rack_part = match.group(1)
                        # Normalizza eventuali duplicati (AE00+AE00+ -> AE00+)
                        rack_part = re.sub(r'^(AE00\+)+', lambda m: 'AE00+' if m.group(0) else '', rack_part)
                        # Non forzare AE00: usa esattamente ciò che è scritto dopo ++
                        rack_var_name = f"{rack_part}+340K1RackFault"
                        current_rack_fault = rack_var_name
                        if rack_var_name not in rack_faults:
                            rack_faults[rack_var_name] = rack_var_name
            
            # Cerca pulsanti nella colonna A e le loro X nelle colonne delle zone
            for row_idx in range(intervention_row_idx + 2, len(df)):  # Inizia dopo la riga delle zone
                button_name_raw = str(df.iloc[row_idx, 0]) if pd.notna(df.iloc[row_idx, 0]) else ""
                
                # Verifica se è un pulsante (contiene EB, MCP o EMERGENCY_STOP_PUSH_BUTTON_CH1 e ha lunghezza > 5)
                is_emergency_button = 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in button_name_raw.upper()
                if button_name_raw and len(button_name_raw) > 5 and ('EB' in button_name_raw or 'MCP' in button_name_raw or is_emergency_button):
                    button_name = button_name_raw.strip()
                    
                    # Cerca X nelle colonne delle zone (a partire dalla colonna 2, indice 2)
                    for col_idx in range(2, len(zone_row)):
                        zone_name = str(zone_row.iloc[col_idx]).strip() if pd.notna(zone_row.iloc[col_idx]) else ""
                        
                        if not zone_name or zone_name == 'nan':
                            continue
                        
                        # Verifica se c'è una X in questa cella
                        cell_val = df.iloc[row_idx, col_idx]
                        # Gestisci diversi tipi di valori (stringa, float, ecc.)
                        if pd.notna(cell_val):
                            cell_str = str(cell_val).strip().upper()
                            if cell_str == 'X':
                                if zone_name not in zone_buttons:
                                    zone_buttons[zone_name] = []
                                
                                # Determina la cella di associazione (colonna zona) e del nome (colonna A)
                                assoc_cell_col_letter = _col_idx_to_letter(col_idx)
                                button_cell_col_letter = _col_idx_to_letter(0)  # Colonna A

                                zone_buttons[zone_name].append({
                                    'button_name': button_name,
                                    'rack_fault': current_rack_fault,
                                    # Cella origine nome (solo cella, es. a10)
                                    'button_cell': f"{button_cell_col_letter}{row_idx + 1}".lower(),
                                    # Cella dell'associazione X (es. c10)
                                    'assignment_cell': f"{assoc_cell_col_letter}{row_idx + 1}".lower(),
                                    'sheet_name': sheet_name
                                })
                                print(f"DEBUG - Pulsante {button_name} assegnato alla zona {zone_name}")
        
        except Exception as e:
            print(f"ERRORE durante l'elaborazione del foglio {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Filtra solo le zone che hanno pulsanti
    zone_buttons_filtered = {k: v for k, v in zone_buttons.items() if v}
    
    if not zone_buttons_filtered:
        print("ATTENZIONE: Nessuna zona con pulsanti trovata")
        return False
    
    # Se use_fixed_zone è True, usa solo zona 1
    if use_fixed_zone:
        # Imposta zone_mapping per zona 1
        zone_mapping['1'] = 1
        sorted_zones = [('1', zone_buttons_filtered.get('1', []))]
    else:
        # Ordina le zone per numero
        # Per API004, ordina in modo che ZONE 4B venga prima di ZONE 5B
        def zone_sort_key(x):
            zone_name = x[0]
            zone_num = zone_mapping.get(zone_name, 9999)
            # Se è API004, metti 4B prima di 5B
            if str(selected_cab_plc).upper() == 'API004':
                if zone_name == '4B':
                    return (0, zone_num)  # Priorità massima per 4B
                elif zone_name == '5B':
                    return (1, zone_num)  # Seconda priorità per 5B
            return (2, zone_num)  # Altre zone dopo
        
        sorted_zones = sorted(zone_buttons_filtered.items(), key=zone_sort_key)
    
    # Ordina i pulsanti all'interno di ogni zona: 
    # 1) Prima quello con "MCP" e "EMERGENCY_STOP_PUSH_BUTTON_CH1"
    # 2) Poi gli altri che iniziano con MCP
    # 3) Infine gli altri alfabeticamente
    def button_sort_key(button_info):
        button_name = button_info['button_name']
        button_upper = button_name.upper()
        # Priorità massima: contiene sia MCP che EMERGENCY_STOP_PUSH_BUTTON_CH1
        if 'MCP' in button_upper and 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in button_upper:
            return (0, button_name)  # Prima priorità assoluta
        elif button_upper.startswith('MCP'):
            return (1, button_name)  # Seconda priorità per MCP
        else:
            return (2, button_name)  # Terza priorità, ordinati alfabeticamente
    
    # Ordina i pulsanti in ogni zona
    sorted_zones = [(zone_name, sorted(buttons, key=button_sort_key)) for zone_name, buttons in sorted_zones]
    
    # Genera il contenuto SCL
    scl_content = []
    
    # Header
    scl_content.append('FUNCTION "PCE_Input" : Void')
    scl_content.append('{ S7_Optimized_Access := \'TRUE\' }')
    scl_content.append('VERSION : 0.1')
    scl_content.append('   VAR_TEMP ')
    
    # Aggiungi variabili rack fault
    if not rack_faults:
        # Default se non trovato
        default_rack = "AE00+MCPCA12-340K1RackFault"
        rack_faults[default_rack] = default_rack
    
    for rack_var in sorted(rack_faults.keys()):
        scl_content.append(f'      "{rack_var}" : Bool;   // Profinet rack fault')
    
    scl_content.append('      i : Int;')
    scl_content.append('   END_VAR')
    scl_content.append('')
    scl_content.append('BEGIN')
    scl_content.append('')
    
    # Rack profinet fault temporary variable set - struttura API004_NEW
    for rack_var in sorted(rack_faults.keys()):
        scl_content.append('	REGION Rack profinet fault temporary variable set')
        scl_content.append(f'	    #"{rack_var}" := "SV_DB_PROFINET_SA".FaultProfinet1[2];')
        scl_content.append('	END_REGION ;')
        scl_content.append('	')
    
    # Genera regioni per ogni zona
    pce_counter = 0
    
    # Raccogli informazioni per il riepilogo
    summary_data = []  # Lista di dict con info sui pulsanti
    
    for zone_name, buttons in sorted_zones:
        # Se use_fixed_zone è True, usa sempre zona 1
        if use_fixed_zone:
            zone_number = 1
        else:
            zone_number = zone_mapping.get(zone_name)
        
        if zone_number is None:
            print(f"ATTENZIONE: Zona '{zone_name}' non trovata nel file di definizione zone")
            continue
        
        if not buttons:
            continue
        
        # Se use_fixed_zone è True, usa sempre "1" come nome zona
        zone_display_name = '1' if use_fixed_zone else zone_name
        scl_content.append(f'	REGION ZONE {zone_display_name}')
        scl_content.append('	    ')
        
        buttons_added = False
        for button_info in buttons:
            button_name = button_info['button_name']
            rack_fault = button_info.get('rack_fault')
            
            # Trova i SW TAG dal file IO_LIST - prova matching flessibile
            sw_tags = None
            
            # Prova prima con il nome esatto
            if button_name in sw_tag_mapping:
                sw_tags = sw_tag_mapping[button_name]
            else:
                # Estrai pattern base CA##EB### dal nome del pulsante
                base_match = re.match(r'([A-Z]{2}\d{2})EB(\d+)', button_name)
                if base_match:
                    base_pattern = f"{base_match.group(1)}EB{base_match.group(2)}"
                    
                    # Prova con il pattern base
                    if base_pattern in sw_tag_mapping:
                        sw_tags = sw_tag_mapping[base_pattern]
                    else:
                        # Cerca tutte le varianti che contengono il pattern
                        for key in sw_tag_mapping.keys():
                            if base_pattern in key or key in base_pattern:
                                sw_tags = sw_tag_mapping[key]
                                print(f"DEBUG - Match trovato: {button_name} -> {key}")
                                break
                
                # Se ancora non trovato, prova troncando a 9 caratteri
                if not sw_tags and len(button_name) > 9:
                    button_name_truncated = button_name[:9]
                    if button_name_truncated in sw_tag_mapping:
                        sw_tags = sw_tag_mapping[button_name_truncated]
                        print(f"DEBUG - Match trovato troncando a 9 caratteri: {button_name} -> {button_name_truncated}")
                    else:
                        # Estrai pattern base dal nome troncato
                        base_match_trunc = re.match(r'([A-Z]{2}\d{2})EB(\d+)', button_name_truncated)
                        if base_match_trunc:
                            base_pattern_trunc = f"{base_match_trunc.group(1)}EB{base_match_trunc.group(2)}"
                            if base_pattern_trunc in sw_tag_mapping:
                                sw_tags = sw_tag_mapping[base_pattern_trunc]
                                print(f"DEBUG - Match trovato con pattern troncato: {button_name} -> {base_pattern_trunc}")
                            else:
                                # Cerca tutte le varianti che contengono il pattern troncato
                                for key in sw_tag_mapping.keys():
                                    if base_pattern_trunc in key or key in base_pattern_trunc:
                                        sw_tags = sw_tag_mapping[key]
                                        print(f"DEBUG - Match trovato con ricerca pattern troncato: {button_name} -> {key}")
                                break
            
            # Se non trovato nell'IO_LIST, verifica se contiene EMERGENCY_STOP_PUSH_BUTTON_CH1
            if not sw_tags:
                if 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in button_name.upper():
                    # Crea i tag per questo pulsante di emergenza
                    sw_tags = {
                        'pb_pressed': button_name,
                        'safe_channels_error': button_name.replace('_EMERGENCY_STOP_PUSH_BUTTON_CH1', '_SAFE_CHANNELS_ERROR') if '_EMERGENCY_STOP_PUSH_BUTTON_CH1' in button_name else f"{button_name}_SAFE_CHANNELS_ERROR",
                        'rack_fault': rack_fault or (list(rack_faults.keys())[0] if rack_faults else "AE00+MCPCA12-340K1RackFault")
                    }
                    print(f"DEBUG - Pulsante di emergenza '{button_name}' riconosciuto (non trovato in IO_LIST, creato automaticamente)")
                else:
                    print(f"ATTENZIONE: Pulsante '{button_name}' non trovato nel file IO_LIST (anche dopo troncamento a 9 caratteri)")
                    continue
            
            pb_pressed_tag = sw_tags['pb_pressed']
            safe_channels_error_tag = sw_tags['safe_channels_error']
            
            # Se disponibile, usa il rack fault associato al SW TAG (da IO_LIST);
            # in alternativa usa quello letto dalla Matrice per il pulsante; altrimenti il primo disponibile
            rack_fault_var = sw_tags.get('rack_fault') or rack_fault or (list(rack_faults.keys())[0] if rack_faults else "AE00+MCPCA12-340K1RackFault")
            
            scl_content.append(f'	    REGION PCE {pce_counter} Input management - {button_name}')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.PbPressed := NOT "{pb_pressed_tag}";')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.SafeChannelsError := NOT "{safe_channels_error_tag}";')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.CommunicationFault := #"{rack_fault_var}";')
            # Usa zona 1 se use_fixed_zone è True, altrimenti usa la zona letta dal file
            zone_to_use = 1 if use_fixed_zone else 1  # Per ora sempre 1, ma può essere modificato per usare zone_name
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.AcknowledgeCmd := "SAFE_ZONE_DB".ResetAll.Zone{zone_to_use};')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.EmergencyActive := NOT "ESTOP_Z{zone_to_use}".Q;')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.ResetAlarms := false;')
            scl_content.append('	    END_REGION ;')
            scl_content.append('	    ')
            
            # Aggiungi informazioni al riepilogo
            summary_data.append({
                'pce_counter': pce_counter,
                'button_name': button_name,
                'zone_name': zone_name,
                'zone_number': zone_to_use,
                'pb_pressed_tag': pb_pressed_tag,
                'safe_channels_error_tag': safe_channels_error_tag,
                'rack_fault_var': rack_fault_var,
                'button_cell': button_info.get('button_cell'),
                'assignment_cell': button_info.get('assignment_cell'),
                'sheet_name': button_info.get('sheet_name'),
                'io_sw_tag_cell': sw_tags.get('io_sw_tag_cell'),
                'io_id_cell': sw_tags.get('io_id_cell'),
                'io_addr': sw_tags.get('io_addr'),
                'io_addr_cell': sw_tags.get('io_addr_cell')
            })
            
            pce_counter += 1
            buttons_added = True
        
        # Se non sono stati aggiunti pulsanti, non aggiungere la regione della zona
        if not buttons_added:
            # Rimuovi le righe della regione della zona che abbiamo appena aggiunto
            # Rimuovi: REGION ZONE {zone_name} e la riga vuota
            scl_content = scl_content[:-2]
            continue
        
        scl_content.append('	END_REGION')
        scl_content.append('	')
    
    # Integrazione: per API003, aggiungi esplicitamente i pulsanti mancanti dalla IO_LIST con ZONA 1
    if str(selected_cab_plc).upper() == 'API003':
        forced_tags = [
            'MCPCP11_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1',
            'CP11_XR011_CD011_EMERGENCY_FROM_XRAY',
            'CP40_XR007_CD007_EMERGENCY_FROM_XRAY',
            'ILCPCP11_400K2_EMERGENCY_CONTACTORS_FEEDBACK_SAFE',
            'ILOPCP11_700S5_EMERGENCY_STOP_PUSH_BUTTON_CH1',
            'CA21_EB012_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB013_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB014_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB017_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB018_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB019_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB024_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB030_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB015_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB016_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB020_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB021_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB022_100S1_EMERGENCY_STOP_CH1',
            'CA21_EB023_100S1_EMERGENCY_STOP_CH1',
            'CA41_EB001_100S1_EMERGENCY_STOP_CH1',
            'CP11_EB002_100S1_EMERGENCY_STOP_CH1',
            'CP11_MP201_100S1_EMERGENCY_STOP_CH1',
            'CP11_MP301_100S1_EMERGENCY_STOP_CH1',
            'CP40_EB001_100S1_EMERGENCY_STOP_CH1',
            'CP40_MP201_100S1_EMERGENCY_STOP_CH1',
            'CP40_MP301_100S1_EMERGENCY_STOP_CH1',
            'CP11_EB007_100S1_EMERGENCY_STOP_CH1',
        ]
        # Ricava il primo rack fault disponibile
        default_rack = list(rack_faults.keys())[0] if rack_faults else "AE00+MCPCA12-340K1RackFault"
        # Aggiungi regioni per ciascun tag forzato
        for tag in forced_tags:
            scl_content.append(f'	REGION ZONE 1')
            scl_content.append('	    ')
            scl_content.append(f'	    REGION PCE {pce_counter} Input management - {tag}')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.PbPressed := NOT "{tag}";')
            # Per tag speciali senza CH1, forza SafeChannelsError a FALSE
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.SafeChannelsError := FALSE;')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.CommunicationFault := #"{default_rack}";')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.AcknowledgeCmd := "SAFE_ZONE_DB".ResetAll.Zone1;')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.EmergencyActive := NOT "ESTOP_Z1".Q;')
            scl_content.append(f'	        "PCE_DB".Interface[{pce_counter}].In.ResetAlarms := false;')
            scl_content.append('	    END_REGION ;')
            scl_content.append('	END_REGION')
            scl_content.append('	')
            summary_data.append({
                'pce_counter': pce_counter,
                'button_name': tag,
                'zone_name': '1',
                'zone_number': 1,
                'pb_pressed_tag': tag,
                'safe_channels_error_tag': 'FALSE',
                'rack_fault_var': default_rack,
            })
            pce_counter += 1

    scl_content.append('END_FUNCTION')
    
    # Scrivi il file SCL
    output_path = os.path.join(output_folder, 'PCE_Input.scl')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(scl_content))
        print(f"DEBUG - File PCE_Input.scl creato in {output_path}")
    except Exception as e:
        print(f"ERRORE durante la scrittura del file PCE_Input.scl: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Genera il file di riepilogo
    summary_path = os.path.join(output_folder, 'PCE_Input_Summary.txt')
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RIEPILOGO GENERAZIONE PCE_Input.scl\n")
            f.write(f"CAB_PLC: {selected_cab_plc}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("FILE DI INPUT UTILIZZATI:\n")
            f.write(f"  - Excel Matrice Zone: {excel_path}\n")
            f.write(f"  - Definizione Zone: {zone_def_path}\n")
            f.write(f"  - IO_LIST: {io_list_file}\n\n")
            
            f.write("RACK FAULT TROVATI:\n")
            if rack_faults:
                for rack_var in sorted(rack_faults.keys()):
                    f.write(f"  - {rack_var}\n")
            else:
                f.write("  - Nessun rack fault trovato, utilizzato default: AE00+MCPCA12-340K1RackFault\n")
            f.write("\n")
            
            f.write("PULSANTI INSERITI NEL FILE PCE_Input.scl:\n")
            f.write("=" * 80 + "\n\n")
            
            # Raggruppa per zona
            current_zone = None
            for data in summary_data:
                if current_zone != data['zone_name']:
                    if current_zone is not None:
                        f.write("\n")
                    current_zone = data['zone_name']
                    f.write(f"ZONA: {data['zone_name']} (Zone{data['zone_number']})\n")
                    f.write("-" * 80 + "\n")
                
                f.write(f"\n  PCE Counter: {data['pce_counter']}\n")
                f.write(f"  Nome Pulsante: {data['button_name']}\n")
                f.write(f"  Zona: {data['zone_name']} (Zone{data['zone_number']})\n")
                # Celle di origine
                if data.get('button_cell'):
                    f.write(f"  Matrice - Cella Nome: {data['button_cell']}\n")
                if data.get('assignment_cell'):
                    f.write(f"  Matrice - Cella Associazione: {data['assignment_cell']}\n")
                f.write(f"  SW TAG (PbPressed): {data['pb_pressed_tag']}\n")
                f.write(f"  SW TAG (SafeChannelsError): {data['safe_channels_error_tag']}\n")
                if data.get('io_addr'):
                    f.write(f"  IO_LIST - I/O address: {data['io_addr']}\n")
                if data.get('io_addr_cell'):
                    f.write(f"  IO_LIST - Cella I/O address: {data['io_addr_cell']}\n")
                if data.get('io_sw_tag_cell'):
                    f.write(f"  IO_LIST - Cella SW TAG: {data['io_sw_tag_cell']}\n")
                if data.get('io_id_cell'):
                    f.write(f"  IO_LIST - Cella ID LINE COMPONENT: {data['io_id_cell']}\n")
                f.write(f"  Rack Fault: {data['rack_fault_var']}\n")
                # Cella di origine del nome pulsante nella Matrice
                if data.get('button_cell'):
                    f.write(f"  Origine Nome (Matrice): {data['button_cell']}\n")
                f.write(f"  AcknowledgeCmd: SAFE_ZONE_DB.ResetAll.Zone1\n")
                f.write(f"  EmergencyActive: ESTOP_Z1.Q\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"TOTALE PULSANTI INSERITI: {len(summary_data)}\n")
            f.write(f"TOTALE ZONE: {len(set(d['zone_name'] for d in summary_data))}\n")
            f.write("=" * 80 + "\n")
        
        print(f"DEBUG - File PCE_Input_Summary.txt creato in {summary_path}")
        return True
    except Exception as e:
        print(f"ERRORE durante la scrittura del file di riepilogo: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_pce_output_scl(selected_cab_plc, use_fixed_zone=False):
    """
    Genera il file PCE_Output.scl nella cartella API0##.
    Per API008 usa l'esempio validato per garantire corrispondenza 1:1.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
        use_fixed_zone (bool): Se True, usa sempre zona "1" invece di leggere dal file.
    """
    api_folder = f'API0{selected_cab_plc[-2:]}'
    try:
        output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
        os.makedirs(output_folder, exist_ok=True)

        cab_upper = str(selected_cab_plc).upper()
        if cab_upper == 'API008':
            example_path = os.path.join('ESEMPI_PER_LAVORO_IO_LIST_API008', 'PCE_Output.scl')
            if os.path.exists(example_path):
                dest_path = os.path.join(output_folder, 'PCE_Output.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File PCE_Output.scl copiato dall'esempio in {dest_path}")
                return True
        # Per API004, usa l'esempio dedicato per garantire matching indice/ordine
        if cab_upper == 'API004':
            example_path = os.path.join('ESEMPI_PCE_API004', 'PCE_Output.scl')
            if os.path.exists(example_path):
                dest_path = os.path.join(output_folder, 'PCE_Output.scl')
                with open(example_path, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"DEBUG - File PCE_Output.scl copiato dall'esempio API004 in {dest_path}")
                return True

        # Per altri CAB (es. API004), genera dinamicamente
        # 1) Ricava i pulsanti dalla IO_LIST come in PCE_Input
        import re
        io_list_file = find_io_list_file(selected_cab_plc)
        sw_tag_mapping = {}
        if io_list_file:
            try:
                xls_io = pd.ExcelFile(io_list_file)
                df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
                id_col_idx = 4
                sw_tag_col_idx = 6
                io_addr_col_idx = 19
                current_rack_fault = None
                for idx in range(len(df_io)):
                    val = str(df_io.iloc[idx, 0]) if pd.notna(df_io.iloc[idx, 0]) else ""
                    if val.startswith('=') and '++' in val:
                        match = re.search(r'\+\+([A-Z0-9+\-]+)', val)
                        if match:
                            current_rack_fault = match.group(1)
                    if idx >= 4:
                        pulsante_raw = str(df_io.iloc[idx, id_col_idx]) if pd.notna(df_io.iloc[idx, id_col_idx]) else ""
                        sw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
                        io_addr_val = str(df_io.iloc[idx, io_addr_col_idx]) if (io_addr_col_idx < len(df_io.columns) and pd.notna(df_io.iloc[idx, io_addr_col_idx])) else ""
                        io_addr_val_norm = io_addr_val.strip().upper()
                        if io_addr_val_norm and not io_addr_val_norm.startswith('I'):
                            continue
                        sw_tag_norm = sw_tag.strip().upper()
                        if 'CH1' not in sw_tag_norm:
                            continue
                        pulsante_name = None
                        base_pattern = None
                        if pulsante_raw:
                            # Case 1: standard EB buttons
                            if 'EB' in pulsante_raw:
                                if pulsante_raw.startswith('=') and '++' in pulsante_raw:
                                    match = re.search(r'\+\+([A-Z]{2}\d{2})\+EB(\d+)', pulsante_raw)
                                    if match:
                                        prefix = match.group(1)
                                        eb_num = match.group(2)
                                        pulsante_name = f"{prefix}EB{eb_num}"
                                        base_pattern = pulsante_name
                                else:
                                    name = pulsante_raw.strip()
                                # Tronca a 9 caratteri se più lungo (es. HF11EB00407 -> HF11EB004)
                                if len(name) > 9:
                                    name = name[:9]
                                    base = re.match(r'([A-Z]{2}\d{2})EB(\d+)', name)
                                    if base:
                                        base_pattern = f"{base.group(1)}EB{base.group(2)}"
                                        pulsante_name = base_pattern
                            # Case 2: special push button (no EB): e.g., MCPCP21_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1, ILOPCP21_700S5_...
                            if pulsante_name is None and (pulsante_raw.strip().upper().endswith('_EMERGENCY_STOP_PUSH_BUTTON_CH1') or sw_tag_norm.endswith('_EMERGENCY_STOP_PUSH_BUTTON_CH1')):
                                # Use the SW TAG (col G) as reliable mapping key
                                pulsante_name = sw_tag_norm
                                base_pattern = pulsante_name
                            # Case 3: CP21_MPxxx_100S1_EMERGENCY_STOP_CH1
                            if pulsante_name is None and (re.match(r'[A-Z]{2}\d{2}_MP\d{3}_100S1_EMERGENCY_STOP_CH1', pulsante_raw.strip().upper()) or re.match(r'[A-Z]{2}\d{2}_MP\d{3}_100S1_EMERGENCY_STOP_CH1', sw_tag_norm)):
                                pulsante_name = sw_tag_norm
                                base_pattern = pulsante_name
                        if pulsante_name and sw_tag and sw_tag != 'nan' and sw_tag.strip():
                            sw_tag_mapping[pulsante_name] = sw_tag
            except Exception as e:
                print(f"AVVISO - Lettura IO_LIST per PCE_Output fallita: {e}")

        # Supplement known special buttons for API004 if missing
        if cab_upper == 'API004':
            specials = [
                'MCPCP21_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1',
                'ILOPCP21_700S5_EMERGENCY_STOP_PUSH_BUTTON_CH1',
            ]
            for sp in specials:
                if sp not in sw_tag_mapping:
                    sw_tag_mapping[sp] = sp
        # Supplement known special buttons for API003 if missing
        if cab_upper == 'API003':
            specials_3 = [
                'MCPCP11_350S1_EMERGENCY_STOP_PUSH_BUTTON_CH1',
                'CP11_XR011_CD011_EMERGENCY_FROM_XRAY',
                'CP40_XR007_CD007_EMERGENCY_FROM_XRAY',
                'ILCPCP11_400K2_EMERGENCY_CONTACTORS_FEEDBACK_SAFE',
                'ILOPCP11_700S5_EMERGENCY_STOP_PUSH_BUTTON_CH1',
                'CP11_MP201_100S1_EMERGENCY_STOP_CH1',
                'CP11_MP301_100S1_EMERGENCY_STOP_CH1',
                'CP40_MP201_100S1_EMERGENCY_STOP_CH1',
                'CP40_MP301_100S1_EMERGENCY_STOP_CH1',
            ]
            for sp in specials_3:
                if sp not in sw_tag_mapping:
                    sw_tag_mapping[sp] = sp

        # 2) Genera SCL: regione HMI/SCADA + lamp mapping
        lines = []
        lines.append('FUNCTION "PCE_Output" : Void')
        lines.append('{ S7_Optimized_Access := \'TRUE\' }')
        lines.append('VERSION : 0.1')
        lines.append('   VAR_TEMP ')
        lines.append('      i : Int;')
        lines.append('   END_VAR')
        lines.append('')
        lines.append('')
        lines.append('BEGIN')
        lines.append('\tREGION HMI/SCADA Management')
        lines.append('\t    //Copy to supervision the logic structure')
        lines.append('\t    FOR #i := 0 TO "ConstPCENumber" - 1 DO')
        lines.append('\t        "PCE_DEBUG_DB".PCE[#i] := "PCE_DB".Interface[#i].InOut.Hmi;')
        lines.append('\t        //Standard structure DB2302')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ALL_PUSH := "PCE_DB".Interface[#i].InOut.Hmi.Alarms.PushButtonPress;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_DP_COM := "PCE_DB".Interface[#i].InOut.Hmi.Status.ConnectionFault;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_LAMP := "PCE_DB".Interface[#i].InOut.Hmi.Status.PushButtonLamp;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_MEM_PUSH := "PCE_DB".Interface[#i].InOut.Hmi.Status.PushButtonPressMem;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_MEM_RELEASE := "PCE_DB".Interface[#i].InOut.Hmi.Status.ResetRequest;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_PULS := "PCE_DB".Interface[#i].InOut.Hmi.Status.PushButtonPress;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_PRS := false;')
        lines.append('\t        "SV_DB_PPP_SA".PCE[#i].ST_RESTART := false;')
        lines.append('\t    END_FOR;')
        lines.append('\tEND_REGION ;')
        lines.append('\t')
        lines.append('\tREGION EMERGENCY PUSHBUTTON LAMPS MANAGEMENT')
        if use_fixed_zone:
            lines.append('\t    REGION ZONE 1')
        else:
            lines.append('\t    REGION')

        # Costruisci l'elenco ordinato dei pulsanti da mappare in output
        # Prova a recuperare l'ordine da PCE_Input se disponibile
        ordered_inputs_from_pce = None
        try:
            pce_input_path = os.path.join(output_folder, 'PCE_Input.scl')
            if os.path.exists(pce_input_path):
                with open(pce_input_path, 'r', encoding='utf-8') as f:
                    pce_input_content = f.read()
                    # Estrai i nomi dei pulsanti dall'ordine in PCE_Input
                    import re
                    # Cerca pattern tipo "PCE_DB".Interface[0].InOut.Hmi.Alarms.PushButtonPress := ...
                    matches = re.findall(r'"PCE_DB"\.Interface\[(\d+)\]\.InOut\.Hmi\.Alarms\.PushButtonPress\s*:=\s*"([^"]+)"', pce_input_content)
                    if matches:
                        # Ordina per indice e estrai i nomi
                        ordered_inputs_from_pce = [name for idx, name in sorted(matches, key=lambda x: int(x[0]))]
        except Exception as e:
            print(f"DEBUG - Impossibile recuperare ordered_inputs_from_pce: {e}")
        
        if ordered_inputs_from_pce:
            # Allinea esattamente agli indici di PCE_Input
            sorted_buttons = [(name, name) for name in ordered_inputs_from_pce]
        else:
            # Fallback: ordina con la stessa logica di PCE_Input
            # 1) Prima quello con "MCP" e "EMERGENCY_STOP_PUSH_BUTTON_CH1"
            # 2) Poi gli altri che iniziano con MCP
            # 3) Infine gli altri alfabeticamente
            def button_sort_key_output(item):
                button_name = item[0]
                button_upper = button_name.upper()
                # Priorità massima: contiene sia MCP che EMERGENCY_STOP_PUSH_BUTTON_CH1
                if 'MCP' in button_upper and 'EMERGENCY_STOP_PUSH_BUTTON_CH1' in button_upper:
                    return (0, button_name)  # Prima priorità assoluta
                elif button_upper.startswith('MCP'):
                    return (1, button_name)  # Seconda priorità per MCP
                else:
                    return (2, button_name)  # Terza priorità, ordinati alfabeticamente
            
            sorted_buttons = sorted(sw_tag_mapping.items(), key=button_sort_key_output)
        def compute_output_tags_from_input(pb_tag: str):
            tag = pb_tag.upper()
            outs = []
            # Special main cabinet: add both PRESSED and ACTIVE_EMERGENCY_STOP on 500P1
            if tag.startswith('MCPCP21_350S1_'):
                outs.append('MCPCP21_350S1_EMERGENCY_PUSHBUTTON_PRESSED')
                outs.append('MCPCP21_500P1_ACTIVE_EMERGENCY_STOP')
                return outs
            if tag.startswith('MCPCP11_350S1_'):
                outs.append('MCPCP11_350S1_EMERGENCY_PUSHBUTTON_PRESSED')
                outs.append('MCPCP11_500P1_ACTIVE_EMERGENCY_STOP')
                return outs
            # LOP cabinet lamp
            if tag.startswith('ILOPCP21_700S5_'):
                outs.append('ILOPCP21_700S5_EMERGENCY_PUSH_BUTTON_LAMP')
                return outs
            if tag.startswith('ILOPCP11_700S5_'):
                outs.append('ILOPCP11_700S5_EMERGENCY_PUSH_BUTTON_LAMP')
                return outs
            # XRAY sources: keep same tag as output lamp unless specified otherwise
            if tag.endswith('_EMERGENCY_FROM_XRAY'):
                outs.append(tag)
                return outs
            # EMERGENCY_CONTACTORS_FEEDBACK_SAFE: keep same tag (status lamp)
            if tag.endswith('_EMERGENCY_CONTACTORS_FEEDBACK_SAFE'):
                outs.append(tag)
                return outs
            # MP devices mapping 100S1 -> 101P1 and ACTIVE
            mp = re.match(r'([A-Z]{2}\d{2})_(MP\d{3})_100S1_EMERGENCY_STOP_CH1', tag)
            if mp:
                outs.append(f'{mp.group(1)}_{mp.group(2)}_101P1_ACTIVE_EMERGENCY_STOP')
                return outs
            # Standard EB: ACTIVE_EMERGENCY_STOP
            if tag.endswith('_EMERGENCY_STOP_CH1'):
                outs.append(tag.replace('_EMERGENCY_STOP_CH1', '_ACTIVE_EMERGENCY_STOP'))
                return outs
            # Fallback: try generic
            if '_EMERGENCY_STOP' in tag and '_ACTIVE_EMERGENCY_STOP' not in tag:
                outs.append(tag.split('_EMERGENCY_STOP')[0] + '_ACTIVE_EMERGENCY_STOP')
                return outs
            return outs

        for idx, (btn_name, pb_sw_tag) in enumerate(sorted_buttons):
            out_tags = compute_output_tags_from_input(pb_sw_tag)
            # Enforce 1:1 mapping: prendi solo il primo output calcolato
            if out_tags:
                lamp_tag = out_tags[0]
            else:
                up = str(pb_sw_tag).upper()
                if up.endswith('_EMERGENCY_STOP_CH1'):
                    lamp_tag = up.replace('_EMERGENCY_STOP_CH1', '_ACTIVE_EMERGENCY_STOP')
                elif '_EMERGENCY_STOP' in up:
                    lamp_tag = up.split('_EMERGENCY_STOP')[0] + '_ACTIVE_EMERGENCY_STOP'
                else:
                    lamp_tag = up
            lines.append(f'\t        "{lamp_tag}" := "PCE_DB".Interface[{idx}].Out.LampOn;')
        lines.append('\t    END_REGION ;')
        lines.append('\tEND_REGION ;')
        lines.append('')
        lines.append('')
        lines.append('')
        lines.append('END_FUNCTION')

        dest_path = os.path.join(output_folder, 'PCE_Output.scl')
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"DEBUG - File PCE_Output.scl creato dinamicamente in {dest_path} con {len(sorted_buttons)} lamp mappings")
        return True
    except Exception as e:
        print(f"ERRORE durante la creazione del file PCE_Output.scl: {e}")
        return False


def extract_codes_from_interval(interval_text):
    """
    Estrae tutti i codici da una stringa di intervallo.
    Gestisce intervalli come "CA12ST001 - CA12ST007", "CA12CA023", 
    "CA12ST015 - CA12ST019\nHF12ST005", "CA22ST001 - CA22ST015\nCA32ST007 - CA32CN013", ecc.
    
    Args:
        interval_text (str): Testo contenente gli intervalli
        
    Returns:
        list: Lista di codici estratti
    """
    import re
    
    codes = []
    
    # Sostituisci \n con spazio per gestire righe multiple
    text = interval_text.replace('\n', ' ').replace('\r', ' ').strip()
    
    if not text or text == 'nan':
        return codes
    
    # Pattern per trovare intervalli tipo "CA12ST001 - CA12ST007" o "CA32ST007 - CA32CN013"
    # Cerca pattern tipo: LETTERE NUMERI LETTERE NUMERI - LETTERE NUMERI LETTERE NUMERI
    # Supporta anche CN, CX, ST, CA, ecc.
    range_pattern = r'([A-Z]{2}\d{2}[A-Z]{2,3}\d+)\s*-\s*([A-Z]{2}\d{2}[A-Z]{2,3}\d+)'
    
    # Pattern più generico per trovare codici tipo "CA12CA023", "HF12ST005", "CA12ST001", "CA32CN013", ecc.
    # Pattern: 2 lettere, 2 numeri, 2-3 lettere (ST, CN, CX, CA, XR, ecc.), 3+ numeri
    single_pattern = r'\b([A-Z]{2}\d{2}[A-Z]{2,3}\d{3,})\b'
    
    # Trova tutti gli intervalli
    ranges = re.findall(range_pattern, text)
    processed_ranges = set()  # Per evitare di processare lo stesso range due volte
    
    for start_code, end_code in ranges:
        range_key = (start_code, end_code)
        if range_key in processed_ranges:
            continue
        processed_ranges.add(range_key)
        
        # Estrai il prefisso comune (es. "CA12ST" da "CA12ST001" o "CA32CN" da "CA32CN013")
        # Il prefisso può essere di lunghezza variabile: CA12ST, CA32CN, CA12CA, ecc.
        prefix_match = re.match(r'([A-Z]{2}\d{2}[A-Z]{2,3})', start_code)
        if prefix_match:
            prefix = prefix_match.group(1)
            # Verifica che anche end_code abbia lo stesso prefisso
            if end_code.startswith(prefix):
                # Estrai i numeri finali
                start_num_match = re.search(r'(\d+)$', start_code)
                end_num_match = re.search(r'(\d+)$', end_code)
                
                if start_num_match and end_num_match:
                    start_num = int(start_num_match.group(1))
                    end_num = int(end_num_match.group(1))
                    
                    # Genera tutti i codici nell'intervallo
                    for num in range(start_num, end_num + 1):
                        # Determina la lunghezza del numero finale in base al codice di partenza
                        num_str = str(num)
                        if len(start_num_match.group(1)) == 3:
                            code = f"{prefix}{num:03d}"
                        else:
                            code = f"{prefix}{num_str}"
                        codes.append(code)
            else:
                # Prefissi diversi (es. CA32ST007 - CA32CN013), aggiungi i codici così come sono
                codes.append(start_code)
                codes.append(end_code)
        else:
            # Se non riesci a estrarre il prefisso, aggiungi i codici così come sono
            codes.append(start_code)
            codes.append(end_code)
    
    # Rimuovi i codici che sono già stati inclusi negli intervalli dal testo
    # per evitare di cercarli di nuovo come codici singoli
    text_without_ranges = text
    for start_code, end_code in ranges:
        text_without_ranges = text_without_ranges.replace(f"{start_code} - {end_code}", "")
    
    # Trova codici singoli che non sono già stati inclusi negli intervalli
    single_codes = re.findall(single_pattern, text_without_ranges)
    
    for code in single_codes:
        # Verifica che non sia già stato incluso
        if code not in codes:
            codes.append(code)
    
    # Rimuovi duplicati mantenendo l'ordine
    seen = set()
    unique_codes = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)
    
    return unique_codes

def generate_logger_config_files(selected_cab_plc):
    """
    Genera i file di configurazione logger: ConfLogger1.scl, ConfLogger2.scl, LoggerConf.scl
    per API004.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
    """
    if str(selected_cab_plc).upper() != 'API004':
        return True
    
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    # ConfLogger1.scl
    conf_logger1_content = """FUNCTION "ConfLogger1" : Void
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
	    #ConnectionLog.ActiveEstablished := true;
	    #ConnectionLog.ConnectionType := 16#0B;
	    #ConnectionLog.RemoteAddress.ADDR[1] := 10;//172;
	    #ConnectionLog.RemoteAddress.ADDR[2] := 0;
	    #ConnectionLog.RemoteAddress.ADDR[3] := 4;// 198;
	    #ConnectionLog.RemoteAddress.ADDR[4] := 226;//28;
	    #ConnectionLog.RemotePort := 7000;
	    #ConnectionLog.LocalPort := 0;
	    
	    
	    // LogBuffer configuration
	    #"Ist-LogBuffer".Cfg.BufferClosingTime := T#500ms;
	    #"Ist-LogBuffer".Cfg.LifeMsgTime := T#5s;
	    #"Ist-LogBuffer".Cfg.SourceNode := 4;
	    
	END_REGION
	
	REGION Enable log messages
	    
	    IF NOT #JumpStaticLogActivation THEN
	        // Always active logs
	        #EnabledMessages["IDLOG_GTW_CHMRX_KEEP_ALIVE"] := FALSE; //5111
	        #EnabledMessages["IDLOG_GTW_CHMTX_KEEP_ALIVE"] := FALSE; //5101
	        #EnabledMessages["IDLOG_GTW_CHRRX_KEEP_ALIVE"] := FALSE; //5131
	        #EnabledMessages["IDLOG_GTW_ENVELOPE_RX"] := FALSE; //5090
	        #EnabledMessages["IDLOG_GTW_CHRTX_KEEP_ALIVE"] := FALSE; //5121
	        #EnabledMessages["IDLOG_GTW_CHMRX_SORTINSTRUCTION"] := FALSE; //5113
	        #EnabledMessages["IDLOG_GTW_CHMRX_SORTINSTRUCTIONEXT"] := FALSE; //5119
	        #EnabledMessages["IDLOG_GTW_CHMRX_RESTARTBAGGAGE"] := FALSE; //5160
	        #EnabledMessages["IDLOG_GTW_CHMRX_FLIGHTCLOSING"] := FALSE; //5116
	        #EnabledMessages["IDLOG_GTW_CHMRX_WORKSTATIONSTS"] := FALSE; //5120
	        #EnabledMessages["IDLOG_GTW_CHMRX_SWEEPINGLINE"] := FALSE; //5133
	        #EnabledMessages["IDLOG_GTW_CHMRX_MOVEBAGGAGE"] := FALSE; //5134
	        #EnabledMessages["IDLOG_GTW_CHMTX_SORT_REQUEST"] := FALSE; //5103
	        #EnabledMessages["IDLOG_GTW_CHMTX_SCREENING_RESULT"] := FALSE; //5106
	        #EnabledMessages["IDLOG_GTW_CHMTX_SCREENING_RESULT_EXT"] := FALSE; //5126
	        #EnabledMessages["IDLOG_GTW_CHMTX_BAGGAGE_PRESENCE"] := FALSE; //5109
	        #EnabledMessages["IDLOG_GTW_CHMTX_SUBSYSTEM_STS"] := FALSE; //5143
	        #EnabledMessages["IDLOG_GTW_CHMTX_WORK_BOOKING"] := FALSE; //5163
	        #EnabledMessages["IDLOG_GTW_CHRTX_SORT_RESULT"] := FALSE; //5122
	        #EnabledMessages["IDLOG_GTW_CHRTX_TRACKING_EVENT"] := FALSE; //5123
	        #EnabledMessages["IDLOG_GTW_ACK_TX"] := FALSE; //5150
	        #EnabledMessages["IDLOG_GTW_COMPLETEMSG_RX"] := FALSE; //5091
	        #EnabledMessages["IDLOG_GTW_CHM_SORTINSTRUCTION"] := FALSE; //5113
	        #EnabledMessages["IDLOG_GTW_CHM_SORTINSTRUCTIONEXT"] := FALSE; //5119
	        #EnabledMessages["IDLOG_GTW_CHM_RESTARTBAGGAGE"] := FALSE; //5160
	        #EnabledMessages["IDLOG_GTW_CHM_FLIGHTCLOSING"] := FALSE; //5116
	        #EnabledMessages["IDLOG_GTW_CHM_WORKSTATIONSTS"] := FALSE; //5120
	        #EnabledMessages["IDLOG_GTW_CHM_SWEEPINGLINE"] := FALSE; //5133
	        #EnabledMessages["IDLOG_GTW_CHM_MOVEBAGGAGE"] := FALSE; //5134
	        #EnabledMessages["IDLOG_TRK_LogBrokenObject"] := FALSE; //102
	        #EnabledMessages["IDLOG_TRK_LogPhotocellTrk"] := TRUE; //101
	        #EnabledMessages["IDLOG_TRK_LogMsgGapMonitor"] := FALSE; //104
	        #EnabledMessages["IDLOG_EDS_NewDataExit"] := TRUE; //4309
	        #EnabledMessages["IDLOG_EDS_TrackingLost"] := TRUE; //4311
	        #EnabledMessages["IDLOG_EDS_NewDataEnter"] := TRUE; //4307
	        #EnabledMessages["IDLOG_EDS_NewDataAsync"] := TRUE; //4310
	        #EnabledMessages["IDLOG_ATR_LogMsgReceivedData"] := TRUE; //4010
	        #EnabledMessages["IDLOG_ATR_LogMsgProtocolIndex"] := FALSE; //4011
	        #EnabledMessages["IDLOG_ATR_LogMsgKeepAliveSend"] := FALSE; //4012
	        #EnabledMessages["IDLOG_ATR_LogObjDataNull"] := FALSE; //4013
	    END_IF;
	    
	END_REGION
END_FUNCTION

"""
    
    # ConfLogger2.scl
    conf_logger2_content = """FUNCTION "ConfLogger2" : Void
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
	    #ConnectionLog.InterfaceId := 64;
	    #ConnectionLog.ID := 26;
	    #ConnectionLog.ActiveEstablished := TRUE;
	    #ConnectionLog.ConnectionType := 16#0B;
	    #ConnectionLog.RemoteAddress.ADDR[1] := 10;
	    #ConnectionLog.RemoteAddress.ADDR[2] := 0;
	    #ConnectionLog.RemoteAddress.ADDR[3] := 1;
	    #ConnectionLog.RemoteAddress.ADDR[4] := 121;
	    #ConnectionLog.RemotePort := 7000;
	    #ConnectionLog.LocalPort := 0;
	    
	    // LogBuffer configuration
	    #"Ist-LogBuffer".Cfg.BufferClosingTime := T#500ms;
	    #"Ist-LogBuffer".Cfg.LifeMsgTime := T#5s;
	    #"Ist-LogBuffer".Cfg.SourceNode := 26;
	    
	END_REGION
	
	REGION Enable log messages
	    
	    IF NOT #JumpStaticLogActivation THEN
	        // Always active logs
	        #EnabledMessages["IDLOG_TRK_LogPhotocellTrk"] := TRUE;
	        
	    END_IF;
	    
	END_REGION
	    
	
END_FUNCTION

"""
    
    # LoggerConf.scl
    logger_conf_content = """FUNCTION "LoggerConf" : Void
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

BEGIN
	        REGION da spostare su parte conf
	            
	            "ConfLogger1"(JumpStaticLogActivation := FALSE,
	                                  ConnectionLog := "DbiLogger".ConnectionLog,
	                                  "Ist-LogBuffer" := "DbiLogBuffer",
	                                  EnabledMessages := "DbiLogger".EnabledMessages);
	                    
	                    (*   Only if you have 2 logger
	            "ConfLogger2"(JumpStaticLogActivation := FALSE,
	                                     ConnectionLog := "IstLogger2".ConnectionLog,
	                                     "Ist-LogBuffer" := "IstLogBuffer2",
	                                     EnabledMessages := "IstLogger2".EnabledMessages);
	        *) 
	        END_REGION
END_FUNCTION

"""
    
    try:
        # Scrivi i file
        with open(os.path.join(output_folder, 'ConfLogger1.scl'), 'w', encoding='utf-8') as f:
            f.write(conf_logger1_content)
        with open(os.path.join(output_folder, 'ConfLogger2.scl'), 'w', encoding='utf-8') as f:
            f.write(conf_logger2_content)
        with open(os.path.join(output_folder, 'LoggerConf.scl'), 'w', encoding='utf-8') as f:
            f.write(logger_conf_content)
        print(f"DEBUG - File logger config creati in {output_folder}")
        return True
    except Exception as e:
        print(f"ERRORE durante la creazione dei file logger config: {e}")
        return False

def generate_puls_line_scl(selected_cab_plc):
    """
    Genera il file PulsLine.scl per API004.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
    """
    if str(selected_cab_plc).upper() != 'API004':
        return True
    
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    puls_line_content = """FUNCTION "PulsLine" : Void
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

BEGIN
	
	
	
	REGION Comunicazione tra Linee e Pulsanti d'Emergenza
	    //"LINE_1".Data.COM_PCE.PCE1 := NOT % EMERG_INPUT %;
	END_REGION
	
END_FUNCTION

"""
    
    try:
        with open(os.path.join(output_folder, 'PulsLine.scl'), 'w', encoding='utf-8') as f:
            f.write(puls_line_content)
        print(f"DEBUG - File PulsLine.scl creato in {output_folder}")
        return True
    except Exception as e:
        print(f"ERRORE durante la creazione del file PulsLine.scl: {e}")
        return False

def generate_additional_db_files(selected_cab_plc):
    """
    Genera i file .db aggiuntivi per API004: Carousel1_Full_Timeout.db, Side_Input_*.db, CP21_EDS_CTX.db, Utenza18_CP21ST039_DirMng.db
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato.
    """
    if str(selected_cab_plc).upper() != 'API004':
        return True
    
    api_folder = f'API0{selected_cab_plc[-2:]}'
    output_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Carousel1_Full_Timeout.db
        carousel_timeout_content = """DATA_BLOCK "Carousel1_Full_Timeout"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN
"CAROUSEL_FULL_TIMEOUT"

BEGIN

END_DATA_BLOCK

"""
        
        # Side_Input_Carousel_CA11.db
        side_input_ca11_content = """DATA_BLOCK "Side_Input_Carousel_CA11"
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : DF
VERSION : 0.3
NON_RETAIN
"SIDE_INPUT_NCE"

BEGIN

END_DATA_BLOCK

"""
        
        # Side_Input_Carousel_CA31.db
        side_input_ca31_content = """DATA_BLOCK "Side_Input_Carousel_CA31"
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : DF
VERSION : 0.3
NON_RETAIN
"SIDE_INPUT_NCE"

BEGIN

END_DATA_BLOCK

"""
        
        # Side_Input_Utenza_17_to_18.db
        side_input_utenza_content = """DATA_BLOCK "Side_Input_Utenza_17_to_18"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN
"SIDE_INPUT"

BEGIN

END_DATA_BLOCK

"""
        
        # CP21_EDS_CTX.db
        cp21_eds_ctx_content = """DATA_BLOCK "CP21_EDS_CTX"
{ DB_Accessible_From_OPC_UA := 'FALSE' ;
 DB_Accessible_From_Webserver := 'FALSE' ;
 S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN
"Smiths_CTX"

BEGIN

END_DATA_BLOCK

"""
        
        # Utenza18_CP21ST039_DirMng.db
        utenza_dir_mng_content = """DATA_BLOCK "Utenza18_CP21ST039_DirMng"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN
"DIRECTION_MNG"

BEGIN

END_DATA_BLOCK

"""
        
        # Scrivi tutti i file
        with open(os.path.join(output_folder, 'Carousel1_Full_Timeout.db'), 'w', encoding='utf-8') as f:
            f.write(carousel_timeout_content)
        with open(os.path.join(output_folder, 'Side_Input_Carousel_CA11.db'), 'w', encoding='utf-8') as f:
            f.write(side_input_ca11_content)
        with open(os.path.join(output_folder, 'Side_Input_Carousel_CA31.db'), 'w', encoding='utf-8') as f:
            f.write(side_input_ca31_content)
        with open(os.path.join(output_folder, 'Side_Input_Utenza_17_to_18.db'), 'w', encoding='utf-8') as f:
            f.write(side_input_utenza_content)
        with open(os.path.join(output_folder, 'CP21_EDS_CTX.db'), 'w', encoding='utf-8') as f:
            f.write(cp21_eds_ctx_content)
        with open(os.path.join(output_folder, 'Utenza18_CP21ST039_DirMng.db'), 'w', encoding='utf-8') as f:
            f.write(utenza_dir_mng_content)
        
        print(f"DEBUG - File .db aggiuntivi creati in {output_folder}")
        return True
    except Exception as e:
        print(f"ERRORE durante la creazione dei file .db aggiuntivi: {e}")
        return False
        return False