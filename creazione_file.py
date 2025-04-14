"""
Questo modulo contiene le funzioni per la creazione dei file di configurazione.
Gestisce la generazione dei file .txt e .scl per le configurazioni dei nastri trasportatori.
"""

import os
from funzioni_elaborazione import count_ca_occurrences, get_last_three_digits

def create_txt_files(df, selected_cab_plc, order):
    """
    Crea i file .txt per le configurazioni delle linee.
    
    Args:
        df: DataFrame con i dati
        selected_cab_plc: CAB_PLC selezionato
        order: Ordine selezionato per la generazione dei file
    """
    # Crea una directory per LINEE all'interno della cartella CAB_PLC selezionata
    linee_folder = f'Configurazioni/{selected_cab_plc}/LINEE'
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

def create_data_block_file(item_id_custom, component_type, output_folder):
    """
    Crea un file DATA_BLOCK per un componente specifico.
    
    Args:
        item_id_custom (str): ID del componente
        component_type (str): Tipo di componente (Carousel/Conveyor)
        output_folder (str): Cartella di destinazione
    """
    data_block_content = f"""DATA_BLOCK "{item_id_custom}"

{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"{component_type}_SEW_MOVIGEAR"

BEGIN

END_DATA_BLOCK
"""
    
    data_block_filename = f"{item_id_custom}.scl"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(os.path.join(output_folder, data_block_filename), 'w') as db_file:
        db_file.write(data_block_content)

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
    linee_folder = f'Configurazioni/{selected_cab_plc}/LINEE'
    if not os.path.exists(linee_folder):
        os.makedirs(linee_folder)
    
    # Estrai i prefissi unici da ITEM_ID_CUSTOM
    unique_prefixes = sorted(set(item[:4].lower() for item in df['ITEM_ID_CUSTOM']))
    
    # Crea un file LINEA per ogni prefisso
    for index, prefix in enumerate(unique_prefixes):
        filename = f"LINEA{index + 1}.scl"
        with open(os.path.join(linee_folder, filename), 'w') as f:
            f.write(f"""DATA_BLOCK "LINE_{index + 1}"
{{ S7_Optimized_Access := 'TRUE' }}
AUTHOR : RP
VERSION : 0.1
NON_RETAIN
"LINE"

BEGIN

END_DATA_BLOCK
""")

def _get_item_details(item_data, index_fallback):
    """Helper function to get formatted name and integer number for an item."""
    if not item_data:
        return "NULL", None # Handle case where item_data is None (e.g., no prev/next)

    item_id = item_data.get('ITEM_ID_CUSTOM', f'MISSING_ID_{index_fallback}')
    formatted_name = item_id # Default a ID originale
    number_int = None

    if "FD" in item_id.upper() or "FIRESHUTTER" in item_id.upper():
        # Per FIRESHUTTER, usa l'ID originale come nome formattato
        formatted_name = item_id
        number_int = index_fallback
    elif "ST" in item_id.upper():
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
    """Helper function to determine if a component should be included in the chain (PREV/NEXT references)."""
    if not item_data:
        return False
        
    item_id = item_data.get('ITEM_ID_CUSTOM', '')
    return ("ST" in item_id.upper() or count_ca_occurrences(item_id) == 2)

def create_main_file(trunk_number, valid_items, output_folder, last_valid_prev_item_data=None, first_valid_next_item_data=None):
    """
    Crea il file MAINx per un tronco specifico.
    
    Args:
        trunk_number (int): Numero del tronco
        valid_items (list): Lista di elementi VALIDI (no 'SC') nel tronco (dizionari)
        output_folder (str): Cartella di output
        last_valid_prev_item_data (dict, optional): Dati dell'ultimo item valido del tronco precedente.
        first_valid_next_item_data (dict, optional): Dati del primo item valido del tronco successivo.
    """
    content = []
    
    # Aggiungi la sezione di inizializzazione
    content.append("REGION Initializing Temp Section")
    content.append("    #TempEncoderNotUsed.Count := 16#0;")
    content.append("END_REGION")
    content.append("")
    
    # Aggiungi la sezione di gestione richiesta start tronco
    content.append("REGION Gestione Richiesta Start Tronco")
    # Assicurati che trunk_number sia intero qui
    try:
        safe_trunk_number = int(trunk_number)
    except (ValueError, TypeError):
        print(f"Attenzione create_main_file: trunk_number '{trunk_number}' non è un intero valido. Uso 0.")
        safe_trunk_number = 0
        
    content.append(f'    IF "UpstreamDB-Globale".Global_Data.Start_All OR "UpstreamDB-Globale".Global_Data.StartTronco{safe_trunk_number} OR "TRUNK{safe_trunk_number}".StartReqAutoFp')
    content.append("    THEN")
    content.append("        #StartTronco := TRUE;")
    content.append("    END_IF;")
    content.append("END_REGION")
    content.append("")
    
    # Aggiungi le chiamate ai blocchi funzionali
    for i, item in enumerate(valid_items):
        
        # --- Ottieni dettagli per item corrente, precedente e successivo EFFETTIVI ---
        current_name, current_number = _get_item_details(item, i + 1) 
        item_id_original = item.get('ITEM_ID_CUSTOM', f'MISSING_ID_{i+1}') 
        
        # Determina il tipo di componente
        item_id_upper = item_id_original.upper()
        if count_ca_occurrences(item_id_original) == 2:
            component_type = "Carousel"
        else:
            component_type = "Conveyor"
        
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
                    
        prev_name_formatted, prev_number = _get_item_details(prev_item_data_to_use, i) 
        prev_component_type = "Carousel" if prev_item_data_to_use and count_ca_occurrences(prev_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2 else "Conveyor"
        prev_name_ref = f'"{prev_name_formatted}".{prev_component_type}.Data.OUT' if prev_item_data_to_use else "NULL"

        # Gestione del riferimento all'item successivo
        next_item_data_to_use = None
        if i == len(valid_items) - 1: 
            # Cerca il primo componente valido nel tronco successivo
            if first_valid_next_item_data and _is_valid_component_for_chain(first_valid_next_item_data):
                next_item_data_to_use = first_valid_next_item_data
        elif i < len(valid_items) - 1:
            # Cerca il prossimo componente valido nel tronco corrente
            for j in range(i+1, len(valid_items)):
                if _is_valid_component_for_chain(valid_items[j]):
                    next_item_data_to_use = valid_items[j]
                    break
                    
        next_name_formatted, next_number = _get_item_details(next_item_data_to_use, i+2)
        next_component_type = "Carousel" if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2 else "Conveyor"
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

            # NEXT: riferimento a item successivo effettivo (gestito sotto)
            if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
                 # Se anche il successivo è Carousel, usa il suo SIDE_INPUT
                 next_carousel_num_for_side = next_number if next_number is not None else 0
                 next_name_ref = f'"SIDE_INPUT_CAROUSEL{next_carousel_num_for_side}".DATA.OUT'
            else:
                 # Altrimenti usa il nome formattato e tipo del successivo
                 next_name_ref = f'"{next_name_formatted}".{next_component_type}.Data.OUT' if next_item_data_to_use else "NULL"
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

            # NEXT: riferimento a item successivo effettivo (gestito sotto)
            if next_item_data_to_use and count_ca_occurrences(next_item_data_to_use.get('ITEM_ID_CUSTOM','')) == 2:
                 # Se il successivo è Carousel, punta al suo SIDE_INPUT
                 next_carousel_num_for_side = next_number if next_number is not None else 0
                 next_name_ref = f'"SIDE_INPUT_CAROUSEL{next_carousel_num_for_side}".DATA.OUT'
            else:
                 # Altrimenti usa il nome formattato e tipo del successivo
                 next_name_ref = f'"{next_name_formatted}".{next_component_type}.Data.OUT' if next_item_data_to_use else "NULL"
            content.append(f'               NEXT := {next_name_ref},')

            content.append('               START := #StartTronco,')
            content.append('               TimeData := "UpstreamDB-Globale".Global_Data.TimeData,')
            content.append('               Constants := "DB_Constants".Constants,')
            content.append(f'               InterfaceTrunkUse := "TRUNK{safe_trunk_number}".ComTrunkUse,') 
            
            panytocnv_num_to_use = current_number if current_number is not None else 0
            content.append(f'               PANYTOCNV_SA := "SV_DB_CONVEYOR_SA".CONVEYOR_{panytocnv_num_to_use},')
            content.append(f'               PANYTOCNV_CMD := "SV_DB_CONVEYOR_CMD".CONVEYOR_{panytocnv_num_to_use},') # CONVEYOR_CMD

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
    
    # Crea il file
    output_path = os.path.join(output_folder, f"MAIN{safe_trunk_number}.scl") # Usa numero tronco sicuro
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("\n".join(content))

def create_conft_t_file(trunk_number, items, output_folder):
    """
    Crea il file CONFT_T per un tronco specifico.
    
    Args:
        trunk_number (int): Numero del tronco
        items (list): Lista di elementi nel tronco
        output_folder (str): Cartella di output
    """
    # Codice per la creazione dei file CONFT_T
    pass


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