import os
import pandas as pd
from typing import Dict, List, Tuple


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
    io_list_folder = os.path.join('Input', 'IO_LIST')
    if not os.path.exists(io_list_folder):
        return [], []

    cab_upper = str(selected_cab_plc).upper()
    io_path = None
    for fn in os.listdir(io_list_folder):
        if fn.endswith('.xlsx') and cab_upper in fn.upper():
            io_path = os.path.join(io_list_folder, fn)
            break
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


