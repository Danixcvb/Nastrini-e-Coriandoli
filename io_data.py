import os
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional


def find_io_list_file(selected_cab_plc: str) -> Optional[str]:
    """
    Trova il file IO_LIST per il CAB_PLC specificato.
    Se il CAB_PLC è APR001 e non trova il file, cerca anche API001 come fallback.
    Cerca solo il file che corrisponde esattamente al CAB_PLC specificato.
    
    Args:
        selected_cab_plc (str): Il CAB_PLC selezionato (es. 'APR001', 'API001')
        
    Returns:
        Optional[str]: Il percorso del file IO_LIST trovato, o None se non trovato
    """
    io_list_folder = os.path.join('Input', 'IO_LIST')
    if not os.path.exists(io_list_folder):
        return None
    
    cab_upper = str(selected_cab_plc).upper()
    
    # Cerca prima con il CAB_PLC originale
    # Cerca file che contengono esattamente il CAB_PLC nel nome (es. API001 in NT23_IO LIST API001_r3.xlsx)
    for fn in os.listdir(io_list_folder):
        if fn.endswith('.xlsx'):
            fn_upper = fn.upper()
            # Verifica che il CAB_PLC sia presente nel nome del file
            # Cerca pattern tipo API001 o APR001 nel nome del file
            if cab_upper in fn_upper:
                # Verifica che non sia un altro CAB_PLC che contiene questo come substring
                # Es. se cerco API001, non vogliamo trovare API0010 o API0011
                # Cerca pattern tipo "API001" seguito da underscore, punto, o fine stringa
                pattern = re.compile(r'\b' + re.escape(cab_upper) + r'(?:_|\.|$)', re.IGNORECASE)
                if pattern.search(fn_upper):
                    return os.path.join(io_list_folder, fn)
    
    # Se non trovato e il CAB_PLC è APR001, cerca API001 come fallback
    if cab_upper == 'APR001':
        fallback_cab = 'API001'
        for fn in os.listdir(io_list_folder):
            if fn.endswith('.xlsx'):
                fn_upper = fn.upper()
                if fallback_cab in fn_upper:
                    # Verifica pattern esatto per API001
                    pattern = re.compile(r'\b' + re.escape(fallback_cab) + r'(?:_|\.|$)', re.IGNORECASE)
                    if pattern.search(fn_upper):
                        print(f"DEBUG - File IO_LIST non trovato per APR001, uso API001 come fallback: {fn}")
                        return os.path.join(io_list_folder, fn)
    
    return None


def load_io_signals(selected_cab_plc: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Carica i segnali dalla IO_LIST del CAB selezionato.
    - Ignora le prime 3 righe di intestazione
    - Prende il nome tag dalla colonna G
    - Determina direzione dalla colonna T (contiene 'I' => input, 'Q' => output)
    - Ignora qualsiasi riga con 'SPARE' in ID o Tag
    - Ignora righe unite senza contenuto
    Ritorna (inputs, outputs), ciascuno come lista di dict {'tag': str, 'id': str, 'dir': 'I'|'Q'}.
    """
    io_path = find_io_list_file(selected_cab_plc)
    if not io_path:
        return [], []

    xls = pd.ExcelFile(io_path)
    df = pd.read_excel(xls, sheet_name='IO List', header=None)

    inputs: List[Dict] = []
    outputs: List[Dict] = []

    id_idx = 4   # colonna E (0-based)
    tag_idx = 6  # colonna G (0-based)
    dir_idx = 19 # colonna T (0-based)

    for i in range(3, len(df)):  # ignora prime 3 righe
        raw_id = str(df.iloc[i, id_idx]) if id_idx < len(df.columns) and pd.notna(df.iloc[i, id_idx]) else ""
        raw_tag = str(df.iloc[i, tag_idx]) if tag_idx < len(df.columns) and pd.notna(df.iloc[i, tag_idx]) else ""
        raw_dir = str(df.iloc[i, dir_idx]) if dir_idx < len(df.columns) and pd.notna(df.iloc[i, dir_idx]) else ""

        if not raw_id and not raw_tag and not raw_dir:
            continue  # riga unita/blank

        if 'SPARE' in raw_id.upper() or 'SPARE' in raw_tag.upper():
            continue

        tag = raw_tag.strip()
        comp_id = raw_id.strip()
        direction = raw_dir.strip().upper()

        if not tag:
            continue

        rec = {'tag': tag, 'id': comp_id, 'dir': 'I' if 'I' in direction else ('Q' if 'Q' in direction else '')}
        if rec['dir'] == 'I':
            inputs.append(rec)
        elif rec['dir'] == 'Q':
            outputs.append(rec)
        else:
            # ignora righe senza direzione definita
            continue

    return inputs, outputs


