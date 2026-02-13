"""
Modulo per la generazione dei file CheckIn (Desk, Damper, Collector).
Genera file separati nella cartella Output/CheckIn.
"""

import os
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional

# Mappatura fissa collettore -> numero utenza
COLLECTOR_TO_UTENZA_MAP = {
    'AC11ST001': 1, 'AC11ST003': 2, 'AC11ST005': 3, 'AC11ST007': 4, 'AC11ST009': 5,
    'AC11ST011': 6, 'AC11ST013': 7, 'AC11ST017': 8, 'AC11ST019': 9, 'AC11ST021': 10,
    'AC11ST027': 11, 'AC11ST029': 12, 'AC11ST031': 13, 'AC11ST033': 14, 'AC11ST035': 15,
    'AC11CN037': 16, 'AC11ST039': 17, 'AC11ST041': 18, 'AC11CN043': 19, 'AC11ST045': 20,
    'AC11ST047': 21, 'AC11ST049': 22, 'AC11CN051': 23, 'AC11DV053': 0,  # Diverter
    'AC11ST055': 25, 'AC11ST057': 26, 'AC11CN059': 27, 'AC11ST061': 28,
    'AC21ST001': 29, 'AC21ST003': 30, 'AC21ST005': 31, 'AC21ST007': 32, 'AC21ST009': 33,
    'AC21ST011': 34, 'AC21ST013': 35, 'AC21ST017': 36, 'AC21ST019': 37, 'AC21ST021': 38,
    'AC21ST027': 39, 'AC21ST029': 40, 'AC21ST031': 41, 'AC21ST033': 42, 'AC21ST035': 43,
    'AC21ST037': 44, 'AC21ST039': 45, 'AC21ST041': 46, 'AC21ST043': 47, 'AC21ST045': 48,
    'AC21ST047': 49, 'AC21ST049': 50, 'AC21ST051': 51, 'AC21ST053': 52, 'AC21ST055': 53,
    'AC21CN057': 54, 'AC21ST059': 55, 'AC21ST061': 56, 'AC21ST063': 57,
    'AC31ST001': 58, 'AC31ST003': 59, 'AC31ST005': 60, 'AC31ST007': 61, 'AC31ST009': 62,
    'AC31ST011': 63, 'AC31ST015': 64, 'AC31ST017': 65, 'AC31ST019': 66, 'AC31ST025': 67,
    'AC31ST027': 68, 'AC31ST029': 69, 'AC31ST031': 70,
    'AC41ST001': 71, 'CP23ST003': 72, 'CP23ST005': 73,
}

def get_utenza_number(collector_name: str) -> int:
    """
    Restituisce il numero di utenza per un collettore basandosi sulla mappatura fissa.
    
    Args:
        collector_name: Nome del collettore (es. 'AC11ST001')
        
    Returns:
        Numero di utenza (default: 1 se non trovato)
    """
    collector_upper = collector_name.strip().upper()
    return COLLECTOR_TO_UTENZA_MAP.get(collector_upper, 1)


def read_checkin_excel(excel_path: str) -> pd.DataFrame:
    """
    Legge il file Excel CHECK_IN_MISURATOR ignorando le prime due righe.
    
    Args:
        excel_path: Percorso del file Excel
        
    Returns:
        DataFrame con i dati delle Desk e Collector
    """
    try:
        # Leggi il file Excel saltando le prime 2 righe (header)
        df = pd.read_excel(excel_path, header=None, skiprows=2)
        
        # Assegna nomi alle colonne
        # Colonne A-F: Desk (A=collettore, B=indice desk, C=lunghezza, D=BknAreaPosition_Left, E=BknAreaPosition_Right, F=ignorare)
        # Colonne G-L: Collector (G=ignorare, H=lunghezza, I=PhtTracking01 right, J=PhtTracking02 right, K=PhtTracking01 left, L=PhtTracking02 left)
        df.columns = [
            'Collector_Name',      # A
            'Desk_Index',          # B
            'Collector_Length',    # C
            'BknAreaPosition_Left',   # D (corretto: D è Left, non Right)
            'BknAreaPosition_Right',  # E (corretto: E è Right, non Left)
            'Ignore_F',            # F
            'Ignore_G',            # G
            'Collector_Length_Col', # H (ignorare, presente in machine table)
            'PhtTracking01_Right', # I
            'PhtTracking02_Right', # J
            'PhtTracking01_Left',  # K
            'PhtTracking02_Left'   # L
        ]
        
        # Rimuovi righe completamente vuote
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        print(f"Errore nella lettura del file Excel CheckIn: {e}")
        raise


def find_collector_info(collector_name: str, machine_table_path: str, cab_plc: str = 'APR001') -> Optional[Dict]:
    """
    Trova informazioni sul collettore dalla machine table.
    Confronta il nome del collector con ITEM_ID_CUSTOM per trovare ITEM_TRUNK.
    
    Args:
        collector_name: Nome del collettore (es. 'AC11ST005')
        machine_table_path: Percorso del file machine table
        cab_plc: CAB_PLC (default APR001)
        
    Returns:
        Dict con: trunk_number, utenza_number, length, oppure None se non trovato
    """
    try:
        df = pd.read_excel(machine_table_path)
        
        # Verifica che le colonne necessarie esistano
        required_columns = ['ITEM_ID_CUSTOM', 'CAB_PLC', 'ITEM_TRUNK']
        if not all(col in df.columns for col in required_columns):
            print(f"ERRORE: Colonne mancanti nella machine table: {required_columns}")
            return None
        
        # Filtra per CAB_PLC
        df = df[df['CAB_PLC'] == cab_plc]
        if df.empty:
            print(f"ATTENZIONE: Nessun dato trovato per CAB_PLC {cab_plc}")
            return None
        
        # Filtra righe con ITEM_TRUNK != 0
        df = df[df['ITEM_TRUNK'].astype(float) != 0]
        if df.empty:
            print(f"ATTENZIONE: Nessun dato con ITEM_TRUNK != 0 per CAB_PLC {cab_plc}")
            return None
        
        # Normalizza il nome del collector per il confronto
        collector_name_upper = str(collector_name).strip().upper()
        
        # Cerca il collettore confrontando ITEM_ID_CUSTOM con il nome del collector
        # Usa match esatto case-insensitive
        collector_row = df[df['ITEM_ID_CUSTOM'].astype(str).str.upper().str.strip() == collector_name_upper]
        
        if collector_row.empty:
            # Prova a vedere se ci sono collettori simili per debug
            similar_collectors = df[df['ITEM_ID_CUSTOM'].astype(str).str.upper().str.contains(collector_name_upper[:4], na=False)]
            print(f"ATTENZIONE: Collettore '{collector_name}' non trovato nella machine table")
            if not similar_collectors.empty:
                print(f"  Collettori simili trovati (primi 5):")
                for idx, row in similar_collectors.head(5).iterrows():
                    print(f"    - {row['ITEM_ID_CUSTOM']} (Trunk: {row['ITEM_TRUNK']})")
            return None
        
        # Se ci sono più match, prendi il primo
        if len(collector_row) > 1:
            print(f"ATTENZIONE: Trovati {len(collector_row)} match per '{collector_name}', uso il primo")
        
        row = collector_row.iloc[0]
        
        # Calcola l'utenza number: conta tutti i collettori (ST/CN/CX) prima di questo nello stesso CAB_PLC
        # Ordina per prefisso e ultime 3 cifre
        df['Prefix'] = df['ITEM_ID_CUSTOM'].str[:4].str.lower()
        df['LastThreeDigits'] = df['ITEM_ID_CUSTOM'].str[-3:].str.extract(r'(\d+)')[0].astype(float)
        
        # Filtra solo collettori (ST, CN, CX) escludendo SC (Datalogic) e doppio CA (Carousel)
        collectors_only = df[
            (df['ITEM_ID_CUSTOM'].str.contains('ST|CN|CX', case=False, na=False)) &
            (~df['ITEM_ID_CUSTOM'].str.contains('SC', case=False, na=False)) &
            (df['ITEM_ID_CUSTOM'].str.upper().str.count('CA') != 2)
        ].copy()
        
        # Ordina per prefisso e ultime 3 cifre
        collectors_only = collectors_only.sort_values(['Prefix', 'LastThreeDigits']).reset_index(drop=True)
        
        # Trova la posizione del collettore corrente nella lista ordinata
        current_item_id = row['ITEM_ID_CUSTOM']
        matching_idx = collectors_only[collectors_only['ITEM_ID_CUSTOM'] == current_item_id].index
        if len(matching_idx) > 0:
            utenza_number = matching_idx[0] + 1  # Utenza parte da 1
        else:
            # Fallback: conta tutti i collettori prima di questo (basato su ordinamento)
            utenza_number = len(collectors_only[collectors_only['ITEM_ID_CUSTOM'] < current_item_id]) + 1
        
        return {
            'trunk_number': int(row['ITEM_TRUNK']),
            'utenza_number': utenza_number,
            'length': float(row.get('ITEM_L', 0)) if pd.notna(row.get('ITEM_L')) else 0,
            'item_id': row['ITEM_ID_CUSTOM']
        }
    except Exception as e:
        print(f"Errore nella ricerca del collettore {collector_name}: {e}")
        return None


def get_damper_number(desk_index: int) -> int:
    """
    Calcola il numero della Damper associata a una Desk.
    Ogni coppia di Desk ha una sola Damper: numero dispari.
    Se Desk è pari, usa il precedente dispari.
    
    Args:
        desk_index: Indice della Desk
        
    Returns:
        Numero della Damper
    """
    if desk_index % 2 == 0:
        # Pari: usa il precedente dispari
        return desk_index - 1
    else:
        # Dispari: usa quello stesso
        return desk_index


def generate_desk_conf(desk_data: Dict, collector_info: Dict) -> str:
    """
    Genera la sezione CONF per una Desk.
    
    Args:
        desk_data: Dict con i dati della Desk dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        
    Returns:
        Stringa SCL con la configurazione della Desk
    """
    collector_name = desk_data['Collector_Name']
    desk_index = int(desk_data['Desk_Index'])
    
    # Estrai prefisso (primi 4 caratteri) e costruisci nome Desk
    # Formato: CC + prima cifra statica (1) + ultime due cifre dell'indice
    prefix = collector_name[:4].upper()
    desk_name = f"Desk_{prefix}CC1{desk_index%100:02d}"
    
    # Valori dal file Excel (sono in millimetri, convertiamo in metri)
    bkn_right_raw = desk_data.get('BknAreaPosition_Right', 0)
    bkn_left_raw = desk_data.get('BknAreaPosition_Left', 0)
    # Converti da mm a m (dividi per 1000)
    bkn_right = float(bkn_right_raw) / 1000.0 if pd.notna(bkn_right_raw) and bkn_right_raw != 0 else 0.0
    bkn_left = float(bkn_left_raw) / 1000.0 if pd.notna(bkn_left_raw) and bkn_left_raw != 0 else 0.0
    
    # Determina il tronco dal collettore
    trunk_number = collector_info.get('trunk_number', 1)
    
    # Trova il nome dell'utenza per il collettore usando la mappatura fissa
    utenza_num = get_utenza_number(collector_name)
    utenza_name = f"Utenza{utenza_num}_{collector_name}"
    
    conf_lines = [
        f'REGION Config Desk ({desk_name})',
        '    REGION Data',
        '        ',
        f'        "{desk_name}".Data.CNF.Belt_Number := 2;',
        f'        "{desk_name}".Data.CNF.Id := {desk_index};',
        f'        "{desk_name}".Data.CNF.ScaleEn := TRUE;',
        f'        "{desk_name}".Data.CNF.Pht1_1_En := TRUE;',
        f'        "{desk_name}".Data.CNF.Pht1_1_Timeout := T#1s; //How long oversize back command enabled',
        f'        "{desk_name}".Data.CNF.Pht1_2_En := TRUE;',
        f'        "{desk_name}".Data.CNF.Pht1_2_Timeout := T#250ms;',
        f'        "{desk_name}".Data.CNF.Pht3_1_En := TRUE;',
        f'        "{desk_name}".Data.CNF.Pht3_1_Timeout := T#250ms;',
        f'        "{desk_name}".Data.CNF.Pht1_1_JamTime := T#5s;',
        f'        "{desk_name}".Data.CNF.Pht1_2_JamTime := T#5s;',
        f'        "{desk_name}".Data.CNF.PhtOverHeight_JamTime := T#5s;',
        f'        "{desk_name}".Data.CNF.Pht3_1_JamTime := T#8s;',
        f'        "{desk_name}".Data.CNF.InjFailed_Delay := T#7s;',
        f'        "{desk_name}".Data.CNF.BookingReqTimeoutH := T#1s;',
        f'        IF "{utenza_name}".Collector.Direction THEN',
        f'            "{desk_name}".Data.CNF.BookingReqTimeoutHH := T#30s;',
        '        ELSE',
        f'            "{desk_name}".Data.CNF.BookingReqTimeoutHH := T#50s;',
        '        END_IF;',
        f'        "{desk_name}".Data.CNF.PhtOverHeight_En := TRUE;',
        f'        "{desk_name}".Data.CNF.PhtOverHeight_Timeout := T#250ms;',
        f'        "{desk_name}".Data.CNF.PhtRiseFilterThr := T#0ms;',
        f'        "{desk_name}".Data.CNF.PhtFallFilterThr := T#0ms;',
        f'        "{desk_name}".Data.CNF.LongResetPT := T#5s;',
        f'        "{desk_name}".Data.CNF.BknSlotLenght := 1.75;',
        f'        "{desk_name}".Data.CNF.BknAreaPosition_Left := {bkn_left};',
        f'        "{desk_name}".Data.CNF.BknAreaPosition_Right := {bkn_right};',
        '        ',
        '    END_REGION',
        '    REGION Conveyor1.Data',
        f'        "{desk_name}".Conveyor1.Data.CNF.FB_TIMER := T#500ms;',
        '    END_REGION',
    ]
    
    # Aggiungi Conveyor2 se necessario (basato sugli esempi, alcune Desk hanno Conveyor2)
    # Per ora aggiungiamo solo Conveyor3, ma potremmo dover aggiungere Conveyor2 per alcune Desk
    if desk_index >= 34:  # Basato sugli esempi, Desk 34+ hanno Conveyor2
        conf_lines.extend([
            '    REGION Conveyor2.Data',
            f'        "{desk_name}".Conveyor2.Data.CNF.FB_TIMER := T#500ms;',
            '    END_REGION',
        ])
    
    conf_lines.extend([
        '    REGION Conveyor3.Data',
        f'        "{desk_name}".Conveyor3.Data.CNF.FB_TIMER := T#500ms;',
        '    END_REGION',
        '    REGION Damper.Data',
        f'        "{desk_name}".Damper.Data.CNF.AutomaticCloseDelay_PT := T#4m;',
        f'        "{desk_name}".Damper.Data.CNF.NotClosed_PT := t#15s;',
        f'        "{desk_name}".Damper.Data.CNF.NotOpened_PT := t#15s;',
        '    END_REGION',
        'END_REGION',
        ''
    ])
    
    return '\n'.join(conf_lines)


def generate_damper_conf(damper_number: int, collector_name: str) -> str:
    """
    Genera la sezione CONF per una Damper.
    
    Args:
        damper_number: Numero della Damper
        collector_name: Nome del collettore (per estrarre prefisso)
        
    Returns:
        Stringa SCL con la configurazione della Damper
    """
    prefix = collector_name[:4].upper()
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    
    conf_lines = [
        f'REGION Config Damper ({damper_name})',
        '    ',
        f'    "{damper_name}".Data.Cnf.Time_Off_Before_Retry := T#2s;',
        f'    "{damper_name}".Data.Cnf.Time_Out_Cmd_On := T#15s;',
        f'    "{damper_name}".Data.Cnf.RetryCnt := 3;',
        '    ',
        'END_REGION',
        ''
    ]
    
    return '\n'.join(conf_lines)


def generate_collector_conf(collector_data: Dict, collector_info: Dict, desk_count: int = 4) -> str:
    """
    Genera la sezione CONF per un Collector.
    
    Args:
        collector_data: Dict con i dati del Collector dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        desk_count: Numero di Desk associate al Collector (default: 4)
        
    Returns:
        Stringa SCL con la configurazione del Collector
    """
    collector_name = collector_data.get('Collector_Name', '')
    # Usa la mappatura fissa invece di quella dalla machine table
    utenza_num = get_utenza_number(collector_name)
    utenza_name = f"Utenza{utenza_num}_{collector_name}"
    
    # Valori dal file Excel (sono in mm, convertiamo in metri dividendo per 1000)
    pht01_right_raw = collector_data.get('PhtTracking01_Right', 0)
    pht02_right_raw = collector_data.get('PhtTracking02_Right', 0)
    pht01_left_raw = collector_data.get('PhtTracking01_Left', 0)
    pht02_left_raw = collector_data.get('PhtTracking02_Left', 0)
    
    # Converti da mm a m (dividi per 1000)
    pht01_right = float(pht01_right_raw) / 1000.0 if pd.notna(pht01_right_raw) and pht01_right_raw != 0 else 0.0
    pht02_right = float(pht02_right_raw) / 1000.0 if pd.notna(pht02_right_raw) and pht02_right_raw != 0 else 0.0
    pht01_left = float(pht01_left_raw) / 1000.0 if pd.notna(pht01_left_raw) and pht01_left_raw != 0 else 0.0
    pht02_left = float(pht02_left_raw) / 1000.0 if pd.notna(pht02_left_raw) and pht02_left_raw != 0 else 0.0
    
    # Lunghezza dalla colonna H dell'Excel (Collector_Length_Col) - è in mm, convertiamo in metri
    # Se non presente nella colonna H, usa la lunghezza dalla machine table come fallback
    length_raw = collector_data.get('Collector_Length_Col', 0)
    if pd.notna(length_raw) and length_raw != 0:
        length = float(length_raw) / 1000.0
    else:
        # Fallback: usa la lunghezza dalla machine table (già in mm, convertiamo in metri)
        length_mt = collector_info.get('length', 0)
        length = float(length_mt) / 1000.0 if length_mt != 0 else 0.0
    
    # Determina il tronco
    trunk_number = collector_info.get('trunk_number', 1)
    
    conf_lines = [
        f'REGION Config Collector_SEW_MOVIGEAR ({collector_name})',
        f'    IF "{utenza_name}".Collector.Direction THEN',
        '        //Direction right',
        '        REGION Conveyor.BookingData',
        f'            "{utenza_name}".Collector.BookingData.CNF.DeskNumber := {desk_count};',
        f'            "{utenza_name}".Collector.BookingData.CNF.SpeedOkThr := 1;',
        f'            "{utenza_name}".Collector.BookingData.CNF.BookingNoreq := T#30s;',
        '        END_REGION',
        '        ',
        '        REGION Collector.Data.CNF',
        f'            "{utenza_name}".Collector.Data.CNF.Pht01En := TRUE;      // [default=TRUE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht02En := TRUE;       // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht03En := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht04En := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht01TrkEn := TRUE;      // [default=TRUE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht02TrkEn := TRUE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht03TrkEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht04TrkEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.SlowdownOnAsrEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.LinkedToNext := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.AdjToSpeedNext := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.ExtDeltaEncoderEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.HmiControlEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.AntiShadowingEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.StrictGapEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.JamStopReqEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.EnableContaminationCheck := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.EnableSecurityStopCheck := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.DbObjectsNumber := 1;       // [default=1]',
        f'            "{utenza_name}".Collector.Data.CNF.Conveyor_ID := {utenza_num:04d};       // [default=0000]',
        f'            "{utenza_name}".Collector.Data.CNF.UseTrunkNumber := {trunk_number};          // [default=1]',
        f'            "{utenza_name}".Collector.Data.CNF.TimeEnergySaving := T#120s;      // [default=T#30S]',
        f'            "{utenza_name}".Collector.Data.CNF.TimeEnergySavingAutotest := T#10S;      // [default=T#30S]',
        f'            "{utenza_name}".Collector.Data.CNF.Speed1 := "DB_TEST_HMI".BONUS_SPEED + 0.8; // [default=1.5] (m/s)',
        f'            "{utenza_name}".Collector.Data.CNF.Speed2 := 0.8;        // [default=0.0]',
        f'            "{utenza_name}".Collector.Data.CNF.SpeedLow := 0.0;        // [default=0.0]',
        f'            "{utenza_name}".Collector.Data.CNF.DriveMaxSpeed := 1.14;        // [default=1.15]',
        f'            "{utenza_name}".Collector.Data.CNF.Acceleration := 2.5;        // [default=2.5]',
        f'            "{utenza_name}".Collector.Data.CNF.Length := {length};       // [default=1600]',
        f'            "{utenza_name}".Collector.Data.CNF.Gap := 0.4;        // [default=0.4]',
        f'            "{utenza_name}".Collector.Data.CNF.Step := 0.0;        // [default=0.4]',
        f'            "{utenza_name}".Collector.Data.CNF.TrackingSlotLength := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Data.CNF.StopDistance := 0.6;        // [default=0.6]',
        f'            "{utenza_name}".Collector.Data.CNF.EndZone := 0.6;        // [default=0.6]',
        f'            "{utenza_name}".Collector.Data.CNF.ContaminationAreaLength := 0.15;        // [default=0.15]',
        '            ',
        '        END_REGION',
        '        ',
        '        REGION Collector.Pht01.Data.CNF',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.FlickeringMaxFp := 5;          // [default=5]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.JamLengthThr := 3;          // [default=3]',
        '        END_REGION',
        '        ',
        '        REGION Collector.Pht02.Data.CNF',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.FlickeringMaxFp := 5;          // [default=5]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.JamLengthThr := 3;          // [default=3]',
        '        END_REGION',
        '        ',
        '        ',
        '        REGION Collector.PhtTracking01.Data.CNF',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId;          // [default=1]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DecisionPointId := 0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.Position := {pht01_right};        // [default=400]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.TrkCtrlTolerance := 0.40;       // [default=0.35] ',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]',
        '            ',
        '        END_REGION',
        '        ',
        '        REGION Collector.PhtTracking02.Data.CNF',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId;          // [default=1]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DecisionPointId := 0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.Position := {pht02_right};         // [default=400]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.TrkCtrlTolerance := 0.35;       // [default=0.35]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]',
        '        END_REGION',
        '        ',
        '        ',
        '        REGION Encoder.Data.CNF',
        f'            "{utenza_name}".Encoder.Data.CNF.K_pulse := 0.0;        // [default=0.0]',
        f'            "{utenza_name}".Encoder.Data.CNF.SpeedTolerance := 0.0;        // [default=0.0]',
        '        END_REGION',
        '        ',
        '        REGION Drive.Par',
        f'            "{utenza_name}".Drive.Data.Par.Direction := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Drive.Data.Par.UseDriveSpeedYs := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Drive.Data.Par.HwAddr := 0;          // [default=0]',
        f'            "{utenza_name}".Drive.Data.Par.MaxSpeed := 1.14;        // [default=1.15]',
        f'            "{utenza_name}".Drive.Data.Par.FeedbackTime := T#500MS;    // [default=T#500MS]',
        '        END_REGION',
        '    ELSE',
        '        //Direction left',
        '        REGION Conveyor.BookingData',
        f'            "{utenza_name}".Collector.BookingData.CNF.DeskNumber := {desk_count};',
        f'            "{utenza_name}".Collector.BookingData.CNF.SpeedOkThr := 1;',
        f'            "{utenza_name}".Collector.BookingData.CNF.BookingNoreq := T#30s;',
        '        END_REGION',
        '        ',
        '        REGION Collector.Data.CNF',
        f'            "{utenza_name}".Collector.Data.CNF.Pht01En := TRUE;      // [default=TRUE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht02En := TRUE;       // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht03En := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht04En := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht01TrkEn := TRUE;      // [default=TRUE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht02TrkEn := TRUE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht03TrkEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.Pht04TrkEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.SlowdownOnAsrEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.LinkedToNext := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.AdjToSpeedNext := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.ExtDeltaEncoderEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.HmiControlEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.AntiShadowingEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.StrictGapEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.JamStopReqEn := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.EnableContaminationCheck := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.EnableSecurityStopCheck := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.Data.CNF.DbObjectsNumber := 1;       // [default=1]',
        f'            "{utenza_name}".Collector.Data.CNF.Conveyor_ID := {utenza_num:04d};       // [default=0000]',
        f'            "{utenza_name}".Collector.Data.CNF.UseTrunkNumber := {trunk_number};          // [default=1]',
        f'            "{utenza_name}".Collector.Data.CNF.TimeEnergySaving := T#120s;      // [default=T#30S]',
        f'            "{utenza_name}".Collector.Data.CNF.TimeEnergySavingAutotest := T#10S;      // [default=T#30S]',
        f'            "{utenza_name}".Collector.Data.CNF.Speed1 := "DB_TEST_HMI".BONUS_SPEED + 0.8; // [default=1.5] (m/s)',
        f'            "{utenza_name}".Collector.Data.CNF.Speed2 := 0.8;        // [default=0.0]',
        f'            "{utenza_name}".Collector.Data.CNF.SpeedLow := 0.0;        // [default=0.0]',
        f'            "{utenza_name}".Collector.Data.CNF.DriveMaxSpeed := 1.14;        // [default=1.15]',
        f'            "{utenza_name}".Collector.Data.CNF.Acceleration := 2.5;        // [default=2.5]',
        f'            "{utenza_name}".Collector.Data.CNF.Length := {length};       // [default=1600]',
        f'            "{utenza_name}".Collector.Data.CNF.Gap := 0.4;        // [default=0.4]',
        f'            "{utenza_name}".Collector.Data.CNF.Step := 0.0;        // [default=0.4]',
        f'            "{utenza_name}".Collector.Data.CNF.TrackingSlotLength := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Data.CNF.StopDistance := 0.6;        // [default=0.6]',
        f'            "{utenza_name}".Collector.Data.CNF.EndZone := 0.6;        // [default=0.6]',
        f'            "{utenza_name}".Collector.Data.CNF.ContaminationAreaLength := 0.15;        // [default=0.15]',
        '            ',
        '        END_REGION',
        '        ',
        '        REGION Collector.Pht01.Data.CNF',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.FlickeringMaxFp := 5;          // [default=5]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht01.Data.CNF.JamLengthThr := 3;          // [default=3]',
        '        END_REGION',
        '        ',
        '        REGION Collector.Pht02.Data.CNF',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.FlickeringMaxFp := 5;          // [default=5]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.FlickeringTime := T#500MS;    // [default=T#500MS]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.PhtRiseFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.PhtFallFilterThr := 0.04;       // [default=0.04]',
        f'            "{utenza_name}".Collector.Pht02.Data.CNF.JamLengthThr := 3;          // [default=3]',
        '        END_REGION',
        '        ',
        '        ',
        '        REGION Collector.PhtTracking01.Data.CNF',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId;          // [default=1]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.DecisionPointId := 0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.Position := {pht01_left};        // [default=400]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.TrkCtrlTolerance := 0.40;       // [default=0.35] ',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking01.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]',
        '            ',
        '        END_REGION',
        '        ',
        '        REGION Collector.PhtTracking02.Data.CNF',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.VidGenerationEn := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ObjLengthUpdateDis := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableUnexpected := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisablePieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationSlipForward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationSlipBackward := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationPieceAppeared := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationPieceLost := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DisableContaminationLengthMismatch := FALSE;      // [default=FALSE]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.MachineId := "DbGlobale".GlobalData.MachineId;          // [default=1]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.DecisionPointId := 0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.MaxLostPiecesForJam := 3;          // [default=3]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.Position := {pht02_left};         // [default=400]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.TrkCtrlTolerance := 0.35;       // [default=0.35]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ObjLengthTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.SlipForwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.SlipBackwardTolerance := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ContaminatioForwardThr := 0.0;          // [default=0]',
        f'            "{utenza_name}".Collector.PhtTracking02.Data.CNF.ContaminatioBackwardThr := 0.0;          // [default=0]',
        '        END_REGION',
        '        ',
        '        ',
        '        REGION Encoder.Data.CNF',
        f'            "{utenza_name}".Encoder.Data.CNF.K_pulse := 0.0;        // [default=0.0]',
        f'            "{utenza_name}".Encoder.Data.CNF.SpeedTolerance := 0.0;        // [default=0.0]',
        '        END_REGION',
        '        ',
        '        REGION Drive.Par',
        f'            "{utenza_name}".Drive.Data.Par.Direction := TRUE;      // [default=FALSE]',
        f'            "{utenza_name}".Drive.Data.Par.UseDriveSpeedYs := TRUE;       // [default=TRUE]',
        f'            "{utenza_name}".Drive.Data.Par.HwAddr := 0;          // [default=0]',
        f'            "{utenza_name}".Drive.Data.Par.MaxSpeed := 1.14;        // [default=1.15]',
        f'            "{utenza_name}".Drive.Data.Par.FeedbackTime := T#500MS;    // [default=T#500MS]',
        '        END_REGION',
        '    END_IF;',
        'END_REGION',
        ''
    ]
    
    return '\n'.join(conf_lines)


def generate_desk_dbin(desk_data: Dict, collector_info: Dict) -> str:
    """
    Genera la sezione DigIn per una Desk.
    Basata sugli esempi forniti.
    
    Args:
        desk_data: Dict con i dati della Desk dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        
    Returns:
        Stringa SCL con la sezione DigIn della Desk
    """
    collector_name = desk_data['Collector_Name']
    desk_index = int(desk_data['Desk_Index'])
    
    prefix = collector_name[:4].upper()
    desk_name = f"Desk_{prefix}CC1{desk_index%100:02d}"
    
    # CDE è legato alla Damper (numero dispari), non alla Desk singola
    damper_number = get_damper_number(desk_index)
    
    # Determina se la desk è pari (indice % 2 == 0) per usare valori diversi
    is_even_desk = (desk_index % 2 == 0)
    motor_suffix = "_2" if is_even_desk else "_1"
    f1_suffix = "125F1" if is_even_desk else "120F1"
    f1_socket_suffix = "126F1" if is_even_desk else "121F1"
    q1_suffix = "125Q1" if is_even_desk else "120Q1"
    q2_suffix = "125Q2" if is_even_desk else "120Q2"
    
    digin_lines = [
        f'    REGION Input Desk {desk_index} ({desk_name})',
        '        ',
        f'        //From ACA - check in enabling signal',
        f'        "CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}" := TRUE;',
        '        ',
        f'        "{desk_name}".Data.IN.Maintenance := FALSE;//NOT "{prefix}_OP81{desk_index%100:02d}_100S1_CLOSED"; //Da verificare',
        f'        "{desk_name}".Data.IN.KeyActive_Ouvert := "CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}" AND "{prefix}_OP81{desk_index%100:02d}_100S1_OPEN";',
        f'        "{desk_name}".Data.IN.KeyActive_DBA := "CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}" AND "{prefix}_OP81{desk_index%100:02d}_100S1_DBA";',
        f'        "{desk_name}".Data.IN.PB_Check := "{prefix}_OP82{desk_index%100:02d}_100S1_FORWARD";',
        f'        "{desk_name}".Data.IN.PB_Move_3 := "{prefix}_OP82{desk_index%100:02d}_100S2_SEND";',
        f'        "{desk_name}".Data.IN.PB_Recul := "{prefix}_OP82{desk_index%100:02d}_100S1_BACKWARD";',
        f'        "{desk_name}".Data.IN.PB_Reset := "DB_TEST_HMI".RESET; //Da modificare',
        f'        "{desk_name}".Data.IN.Pht1_1 := NOT "{prefix}_CC1{desk_index%100:02d}_B1101_STOP_HEAD_PHOTOCELL";',
        f'        "{desk_name}".Data.IN.Pht1_2 := NOT "{prefix}_CC1{desk_index%100:02d}_B1201_STOP_TAIL_PHOTOCELL";',
        f'        "{desk_name}".Data.IN.Pht3_1 := NOT "{prefix}_CC2{desk_index%100:02d}_B1101_STOP_HEAD_PHOTOCELL";',
        f'        "{desk_name}".Data.IN.PhtOverHeight := NOT "{prefix}_CC1{desk_index%100:02d}_B7701_SIZE_CONTROL";',
        f'        "{desk_name}".Data.IN.EMG := FALSE; // NOT "ESTOP_Z1".Q;',
        f'        "{desk_name}".Data.IN.BusFault := "SV_DB_PROFINET_SA".FaultProfinet1[28];',
        '        ',
        f'        "{desk_name}".Data.IN.ExternalFault := FALSE;',
        f'        "{desk_name}".Data.IN.ExternalFault := "{desk_name}".Data.IN.ExternalFault OR NOT "{prefix}_CC1{desk_index%100:02d}_M0001_WEIGHING_BELT_MOTOR{motor_suffix}_OVERTEMPERATURE";',
        f'        "{desk_name}".Data.IN.ExternalFault := "{desk_name}".Data.IN.ExternalFault OR NOT "{prefix}_CC2{desk_index%100:02d}_M0001_LAUNCH_BELT_MOTOR{motor_suffix}_OVERTEMPERATURE";',
        f'        "{desk_name}".Data.IN.ExternalFault := "{desk_name}".Data.IN.ExternalFault OR NOT "{prefix}_CDE{damper_number:02d}_210F1_ELECTRONIC_FUSES_STATUS";',
        f'        //"{desk_name}".Data.IN.ExternalFault := "{desk_name}".Data.IN.ExternalFault OR NOT "{prefix}_CDE{damper_number:02d}_450B1_OVERTEMPERATURE";',
        '        ',
        f'        "{desk_name}".Data.IN.SafetyBreaker := "{prefix}_CDE{damper_number:02d}_100Q1_MAIN_SWITCH_CLOSED" AND NOT "{prefix}_CDE{damper_number:02d}_100Q1_MAIN_SWITCH_TRIPPED";',
        f'        "{desk_name}".Data.IN.EOK400VAC := "{prefix}_CDE{damper_number:02d}_{f1_suffix}_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_BENCH_MOTORS_{desk_index}";',
        f'        "{desk_name}".Data.IN.EOK230VAC := "{prefix}_CDE{damper_number:02d}_102Q1_230VAC_UPS_MAIN_SWITCH_CLOSED" AND "{prefix}_CDE{damper_number:02d}_{f1_socket_suffix}_230VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_BENCH_SOCKET_{desk_index}";',
        f'        "{desk_name}".Data.IN.EOK24VDCConveyors := "{prefix}_CDE{damper_number:02d}_200F1_230VAC_UPS_CIRCUIT_BREAKER_STATUS_POWER_SUPPLY_24VDC";',
        f'        "{desk_name}".Data.IN.EOK24VDCShutter := "{prefix}_CDE{damper_number:02d}_200F1_230VAC_UPS_CIRCUIT_BREAKER_STATUS_POWER_SUPPLY_24VDC";',
        '        //Conveyor 1',
        f'        "{desk_name}".Conveyor1.Data.IN.FAULT := NOT "{prefix}_CDE{damper_number:02d}_{q1_suffix}_FAULT_WEIGHING_BELT_MOTOR{motor_suffix}";',
        f'        "{desk_name}".Conveyor1.Data.IN.RESET := "DB_TEST_HMI".RESET;',
        f'        "{desk_name}".Conveyor1.Data.IN.Maintenance_FW := "{prefix}_OP82{desk_index%100:02d}_100S1_FORWARD";',
        f'        "{desk_name}".Conveyor1.Data.IN.Maintenance_RW := "{prefix}_OP82{desk_index%100:02d}_100S1_BACKWARD";',
        '        //Conveyor 3',
        f'        "{desk_name}".Conveyor3.Data.IN.FAULT := NOT "{prefix}_CDE{damper_number:02d}_{q2_suffix}_FAULT_LAUNCH_BELT_MOTOR{motor_suffix}";',
        f'        "{desk_name}".Conveyor3.Data.IN.RESET := "DB_TEST_HMI".RESET;',
        f'        "{desk_name}".Conveyor3.Data.IN.Maintenance_FW := "{prefix}_OP82{desk_index%100:02d}_100S1_FORWARD";',
        f'        "{desk_name}".Conveyor3.Data.IN.Maintenance_RW := "{prefix}_OP82{desk_index%100:02d}_100S1_BACKWARD";',
        '        ',
        '        //Damper',
        f'        "{desk_name}".Damper.Data.IN.Fault := FALSE; ',
    ]
    
    # Aggiungi riferimenti Damper (ogni Desk usa la sua Damper, anche se condivisa)
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    digin_lines.extend([
        f'        "{desk_name}".Damper.Data.IN.Opened := "{prefix}_SD1{damper_number%100:02d}_B7001_POSITION_UP";',
        f'        "{desk_name}".Damper.Data.IN.Closed := "{prefix}_SD1{damper_number%100:02d}_B7101_POSITION_DOWN";',
        '        ',
        '    END_REGION',
        ''
    ])
    
    return '\n'.join(digin_lines)


def generate_damper_dbin(damper_number: int, collector_name: str, desk_indices: List[int]) -> str:
    """
    Genera la sezione DigIn per una Damper.
    Una Damper gestisce due Desk.
    
    Args:
        damper_number: Numero della Damper
        collector_name: Nome del collettore (per estrarre prefisso)
        desk_indices: Lista degli indici delle Desk associate (sempre 2)
        
    Returns:
        Stringa SCL con la sezione DigIn della Damper
    """
    prefix = collector_name[:4].upper()
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    # Le desk hanno +100 sull'indice nella nomenclatura
    desk1_name = f"Desk_{prefix}CC1{(desk_indices[0] + 100) % 100:02d}"
    desk2_name = f"Desk_{prefix}CC1{(desk_indices[1] + 100) % 100:02d}"
    
    digin_lines = [
        f'    REGION Input Damper Interface ({damper_name}) - Desk {desk_indices[0]}/{desk_indices[1]}',
        '        ',
        f'        "{damper_name}".Data.In.Damper1Data := "{desk1_name}".Damper.Data;',
        f'        "{damper_name}".Data.In.Damper2Data := "{desk2_name}".Damper.Data;',
        '        ',
        '    END_REGION',
        ''
    ]
    
    return '\n'.join(digin_lines)


def generate_collector_dbin(collector_data: Dict, collector_info: Dict) -> str:
    """
    Genera la sezione DigIn per un Collector.
    
    Args:
        collector_data: Dict con i dati del Collector dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        
    Returns:
        Stringa SCL con la sezione DigIn del Collector
    """
    collector_name = collector_data.get('Collector_Name', '')
    # Usa la mappatura fissa invece di quella dalla machine table
    utenza_num = get_utenza_number(collector_name)
    utenza_name = f"Utenza{utenza_num}_{collector_name}"
    
    # Determina il tronco
    trunk_number = collector_info.get('trunk_number', 1)
    
    digin_lines = [
        f'    REGION Input Collector {utenza_name} ({collector_name})',
        '        ///',
        '        //    Profinet',
        '        //   ---------------------------------------------------------------------------------',
        '        ',
        f'        IF "SV_DB_PROFINET_SA".FaultProfinet1[11] THEN',
        f'            "{utenza_name}".Drive.Data.In.DataOk := FALSE;',
        f'            "{utenza_name}".Collector.Data.IN.BusFault := TRUE;',
        f'            "{utenza_name}".Collector.Pht01.Data.IN.BusFault := TRUE;',
        f'            "{utenza_name}".Encoder.Data.IN.BusFault := TRUE;',
        '        ELSE',
        f'            "{utenza_name}".Drive.Data.In.DataOk := TRUE;',
        f'            "{utenza_name}".Collector.Data.IN.BusFault := FALSE;',
        f'            "{utenza_name}".Collector.Pht01.Data.IN.BusFault := FALSE;',
        f'            "{utenza_name}".Encoder.Data.IN.BusFault := FALSE;',
        '        END_IF;',
        '        ',
        '        ',
        '        //    Conveyor Input',
        '        //   ---------------------------------------------------------------------------------',
        f'        "{utenza_name}".Collector.Data.IN.PRS := NOT "DbiTrunkLN{trunk_number:02d}".Data.SA.ST_AUTOMATIC;',
        f'        "{utenza_name}".Collector.Data.IN.Dir := TRUE;',
        f'        "{utenza_name}".Collector.Data.IN.ExternalFault := FALSE;',
        f'        "{utenza_name}".Collector.Data.IN.PFL := FALSE;',
        f'        "{utenza_name}".Collector.Data.IN.ASR := FALSE;',
        f'        "{utenza_name}".Collector.Data.IN.EnableBuffering := FALSE;',
        f'        "{utenza_name}".Collector.Data.IN.SafetyBreaker := FALSE; // NOT "ENR55CV0100_SBR";',
        f'        "{utenza_name}".Collector.Data.IN.EMG := FALSE; // For Emulation := NOT "ENR55_EMG_ZONE1";',
        '        ///',
        '        //    Photocell Input',
        '        //   ---------------------------------------------------------------------------------',
        '        ',
        f'        "{utenza_name}".Collector.Pht01.Data.IN.Photocell := NOT "{collector_name[:4].upper()}_ST{collector_name[-3:].upper()}_B1201_STOP_TAIL_PHOTOCELL";',
        f'        "{utenza_name}".Collector.Pht02.Data.IN.Photocell := NOT "{collector_name[:4].upper()}_ST{collector_name[-3:].upper()}_B1101_STOP_HEAD_PHOTOCELL";',
        '        ',
        '        //    Drive Input',
        '        //   ---------------------------------------------------------------------------------',
        '        ',
        f'        "{utenza_name}".Drive.Data.In.EOk := TRUE; // for emu TRUE;',
        f'        "{utenza_name}".Drive.Data.In.Telegram := "{collector_name.upper()}_IN";',
        '        ',
        '        ',
        '        ',
        '    END_REGION ;',
        ''
    ]
    
    return '\n'.join(digin_lines)


def generate_desk_digout(desk_data: Dict) -> str:
    """
    Genera la sezione DigOut per una Desk.
    
    Args:
        desk_data: Dict con i dati della Desk dal file Excel
        
    Returns:
        Stringa SCL con la sezione DigOut della Desk
    """
    collector_name = desk_data['Collector_Name']
    desk_index = int(desk_data['Desk_Index'])
    
    prefix = collector_name[:4].upper()
    desk_name = f"Desk_{prefix}CC1{desk_index%100:02d}"
    
    # CDE è legato alla Damper (numero dispari), non alla Desk singola
    damper_number = get_damper_number(desk_index)
    
    digout_lines = [
        f'    REGION Output Check-in Desk {desk_index} ({desk_name})',
        '        ',
        '        //Service lamp must be flashing if DBA/OPEN are TRUE and CUSTOMER ENABLED is FALSE (or VICE-VERSA)',
        '        //Service lamp must be ON if DBA/OPEN are TRUE and CUSTOMER ENABLED is TRUE',
        '        #TempServiceLamp := FALSE;',
        f'        #TempServiceLamp := #TempServiceLamp OR ("CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}" AND "DbGlobale".TimeData.ClkLampeggioLento);',
        f'        #TempServiceLamp := #TempServiceLamp OR ("{prefix}_OP81{desk_index%100:02d}_100S1_OPEN" AND "DbGlobale".TimeData.ClkLampeggioLento);',
        f'        #TempServiceLamp := #TempServiceLamp OR ("{prefix}_OP81{desk_index%100:02d}_100S1_DBA" AND "DbGlobale".TimeData.ClkLampeggioLento);',
        f'        #TempServiceLamp := #TempServiceLamp OR ("{prefix}_OP81{desk_index%100:02d}_100S1_OPEN" AND "CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}");',
        f'        #TempServiceLamp := #TempServiceLamp OR ("{prefix}_OP81{desk_index%100:02d}_100S1_DBA" AND "CUSTOMER_VARIOUS_CHECKIN_JB_ENABLED_CHECK_IN_BENCH_{desk_index}");',
        f'        "{prefix}_OP81{desk_index%100:02d}_100P1_IN_SERVICE" := #TempServiceLamp;',
        '        ',
        f'        "{prefix}_OP81{desk_index%100:02d}_100P2_MAINTENANCE_ONGOING" := "{desk_name}".Data.SV.Desk.Maintenance;',
        '        ',
        f'        "{prefix}_OP81{desk_index%100:02d}_100P3_TECHNICAL_FAULT" := "{desk_name}".AVR;',
        f'        "{prefix}_OP82{desk_index%100:02d}_100P1_OVERSIZE" := "{desk_name}".Data.OUT.Led_OverLenght OR "{desk_name}".Data.SV.Conveyor1.AlmPhotocell3;',
        '        ',
        f'        "{prefix}_OP82{desk_index%100:02d}_100S2_SEND_PB_LIGHT" := "{desk_name}".Data.OUT.Led_Move_3;',
        '        ',
        '        //Conveyor 1',
        f'        "{prefix}_CDE{damper_number:02d}_120Q1_START_FORWARD_WEIGHING_BELT_MOTOR_1" := "{desk_name}".Conveyor1.Data.CMD.CMD_FW;',
        f'        "{prefix}_CDE{damper_number:02d}_120Q1_START_BACKWARD_WEIGHING_BELT_MOTOR_1" := "{desk_name}".Conveyor1.Data.CMD.CMD_RW;',
        '        //Conveyor 3',
        f'        "{prefix}_CDE{damper_number:02d}_120Q2_START_FORWARD_LAUNCH_BELT_MOTOR_1" := "{desk_name}".Conveyor3.Data.CMD.CMD_FW;',
        '        ',
        '        ',
        '    END_REGION',
        ''
    ]
    
    return '\n'.join(digout_lines)


def generate_damper_digout(damper_number: int, collector_name: str, desk_indices: List[int]) -> str:
    """
    Genera la sezione DigOut per una Damper.
    
    Args:
        damper_number: Numero della Damper
        collector_name: Nome del collettore (per estrarre prefisso)
        desk_indices: Lista degli indici delle Desk associate
        
    Returns:
        Stringa SCL con la sezione DigOut della Damper
    """
    prefix = collector_name[:4].upper()
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    
    # Determina il prefisso CDE in base alla Damper (CDE è legato alla Damper, non alla Desk)
    cde_prefix = f"{prefix}_CDE{damper_number:02d}"
    
    digout_lines = [
        f'    REGION Output Check-in Dampers {desk_indices[0]} & {desk_indices[1]} ({prefix}SD1{damper_number%100:02d})',
        '        ',
        f'        "{cde_prefix}_501K1_UP_STOP_DOWN_STOP_ANTI_INTRUSION_DAMPER" := "{damper_name}".Data.Out.Signal;',
        f'        "{cde_prefix}_501K5_ANOMALY_ANTI_INTRUSION_DAMPER" := "{damper_name}".Data.Out.Fault;',
        '        ',
        '    END_REGION',
        ''
    ]
    
    return '\n'.join(digout_lines)


def generate_desk_main(desk_data: Dict, collector_info: Dict, desks_comm_index: int) -> str:
    """
    Genera la sezione MAIN per una Desk.
    
    Args:
        desk_data: Dict con i dati della Desk dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        desks_comm_index: Indice per DesksComm (parte da 1)
        
    Returns:
        Stringa SCL con la sezione MAIN della Desk
    """
    collector_name = desk_data['Collector_Name']
    desk_index = int(desk_data['Desk_Index'])
    
    prefix = collector_name[:4].upper()
    desk_name = f"Desk_{prefix}CC1{desk_index%100:02d}"
    
    # Usa la mappatura fissa invece di quella dalla machine table
    utenza_num = get_utenza_number(collector_name)
    utenza_name = f"Utenza{utenza_num}_{collector_name}"
    
    main_lines = [
        f'REGION {desk_name} - DESK',
        '    ',
        f'    "{desk_name}"(TimeData := #TimeData,',
        f'                 Com_Collector := "{utenza_name}".Collector.DesksComm[{desks_comm_index}].COM_COLLECTOR,',
        f'                 Com_Desk => "{utenza_name}".Collector.DesksComm[{desks_comm_index}].COM_DESK,',
        f'                 PANYTO_SV := "SV_DB_CHECKIN".DESK[{desk_index}],',
        '                 InterfaceTrunkUse := #TrunkInterface,',
        '                 InterfaceLineTrunk := "DbiLine1".ComLineTrunk);',
        'END_REGION',
        ''
    ]
    
    return '\n'.join(main_lines)


def generate_damper_main(damper_number: int, collector_name: str) -> str:
    """
    Genera la sezione MAIN per una Damper.
    
    Args:
        damper_number: Numero della Damper
        collector_name: Nome del collettore (per estrarre prefisso)
        
    Returns:
        Stringa SCL con la sezione MAIN della Damper
    """
    prefix = collector_name[:4].upper()
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    
    main_lines = [
        f'REGION Call SingleImpulsiveDamper ({damper_name})',
        '    ',
        f'    "{damper_name}"(#TrunkInterface);',
        '    ',
        'END_REGION',
        ''
    ]
    
    return '\n'.join(main_lines)


def generate_collector_main(collector_data: Dict, collector_info: Dict, prev_collector: Optional[str] = None, next_collector: Optional[str] = None) -> str:
    """
    Genera la sezione MAIN per un Collector.
    
    Args:
        collector_data: Dict con i dati del Collector dal file Excel
        collector_info: Dict con info del collettore dalla machine table
        prev_collector: Nome del Collector precedente (opzionale)
        next_collector: Nome del Collector successivo (opzionale)
        
    Returns:
        Stringa SCL con la sezione MAIN del Collector
    """
    collector_name = collector_data.get('Collector_Name', '')
    # Usa la mappatura fissa invece di quella dalla machine table
    utenza_num = get_utenza_number(collector_name)
    utenza_name = f"Utenza{utenza_num}_{collector_name}"
    
    # Determina il tronco
    trunk_number = collector_info.get('trunk_number', 1)
    
    # Costruisci riferimenti PREV e NEXT
    prev_ref = f'"{prev_collector}".Collector.Data.OUT' if prev_collector else '"NULL"'
    next_ref = f'"{next_collector}".Collector.Data.OUT' if next_collector else '"NULL"'
    
    main_lines = [
        f'REGION Call Collector_SEW_MOVIGEAR ({collector_name})',
        '    ',
        f'    "{utenza_name}"(START := #StartTronco,',
        f'                    PREV := {prev_ref},',
        f'                    NEXT := {next_ref},',
        '                    TimeData := #TimeData,',
        '                    Constants := #Constants,',
        f'                    TrunkInterface := #TrunkInterface,',
        f'                    SupervisionSa := "SV_DB_COLLECTOR_SA".COLLECTOR[{utenza_num}],',
        f'                    SupervisionCmd := "SV_DB_COLLECTOR_CMD".COLLECTOR[{utenza_num}],',
        '                    DB_OBJ := "DbsObject".DbObj[1]);',
        '    ',
        'END_REGION',
        ''
    ]
    
    return '\n'.join(main_lines)


def generate_desk_db(desk_data: Dict) -> str:
    """
    Genera il file .db per una Desk.
    
    Args:
        desk_data: Dict con i dati della Desk dal file Excel
        
    Returns:
        Stringa con il contenuto del file .db
    """
    collector_name = desk_data['Collector_Name']
    desk_index = int(desk_data['Desk_Index'])
    
    prefix = collector_name[:4].upper()
    desk_name = f"Desk_{prefix}CC1{desk_index%100:02d}"
    
    db_content = f'''DATA_BLOCK "{desk_name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.2
NON_RETAIN
"DESK"

BEGIN

END_DATA_BLOCK

'''
    return db_content


def generate_damper_db(damper_number: int, collector_name: str) -> str:
    """
    Genera il file .db per una Damper.
    
    Args:
        damper_number: Numero della Damper
        collector_name: Nome del collettore (per estrarre prefisso)
        
    Returns:
        Stringa con il contenuto del file .db
    """
    prefix = collector_name[:4].upper()
    damper_name = f"Damper_{prefix}SD1{damper_number%100:02d}"
    
    db_content = f'''DATA_BLOCK "{damper_name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
NON_RETAIN
"SingleImpulsiveDamperInterface"

BEGIN

END_DATA_BLOCK

'''
    return db_content


def generate_checkin_files(checkin_excel_path: str, machine_table_path: str, output_folder: str = 'Output/CheckIn', cab_plc: str = 'APR001'):
    """
    Funzione principale per generare tutti i file CheckIn.
    
    Args:
        checkin_excel_path: Percorso del file Excel CHECK_IN_MISURATOR
        machine_table_path: Percorso del file machine table
        output_folder: Cartella di output (default: Output/CheckIn)
        cab_plc: CAB_PLC (default: APR001)
        
    Returns:
        bool: True se la generazione è completata con successo, False altrimenti
    """
    try:
        # Crea la cartella di output se non esiste
        os.makedirs(output_folder, exist_ok=True)
        
        # Leggi il file Excel CheckIn
        print(f"Lettura file Excel CheckIn: {checkin_excel_path}")
        df_checkin = read_checkin_excel(checkin_excel_path)
        
        if df_checkin.empty:
            print("ERRORE: Nessun dato trovato nel file Excel CheckIn")
            return False, "Nessun dato trovato nel file Excel CheckIn"
        
        # Raccoglie tutti i dati senza separazione per tronco
        all_desks = []
        all_collectors = []
        all_dampers_set = set()
        
        # Processa ogni riga del DataFrame
        for idx, row in df_checkin.iterrows():
            collector_name = str(row['Collector_Name']).strip()
            
            if pd.isna(collector_name) or collector_name == '':
                continue
            
            # Trova informazioni sul collettore dalla machine table
            collector_info = find_collector_info(collector_name, machine_table_path, cab_plc)
            
            if collector_info is None:
                print(f"ATTENZIONE: Collettore {collector_name} non trovato nella machine table, saltato")
                continue
            
            # Aggiungi Desk se presente
            if pd.notna(row['Desk_Index']):
                desk_index = int(row['Desk_Index'])
                desk_data = {
                    'Collector_Name': collector_name,
                    'Desk_Index': desk_index,
                    'BknAreaPosition_Right': row.get('BknAreaPosition_Right', 0),
                    'BknAreaPosition_Left': row.get('BknAreaPosition_Left', 0),
                }
                all_desks.append({
                    'data': desk_data,
                    'collector_info': collector_info
                })
                
                # Aggiungi Damper associata
                damper_number = get_damper_number(desk_index)
                all_dampers_set.add((damper_number, collector_name))
            
            # Aggiungi Collector se presente (controlla se ci sono valori nelle colonne I-L)
            # Se ci sono valori PhtTracking, usali; altrimenti aggiungi comunque il Collector se non è già presente
            has_pht_tracking = pd.notna(row.get('PhtTracking01_Right')) or pd.notna(row.get('PhtTracking01_Left'))
            
            # Verifica se il Collector è già stato aggiunto (evita duplicati)
            collector_already_added = any(
                c['data']['Collector_Name'] == collector_name 
                for c in all_collectors
            )
            
            # Aggiungi solo se non è già presente (evita duplicati)
            if not collector_already_added:
                # Prendi Collector_Length_Col dalla colonna H (se presente, altrimenti usa 0)
                collector_length_col = row.get('Collector_Length_Col', 0) if pd.notna(row.get('Collector_Length_Col')) else 0
                
                collector_data = {
                    'Collector_Name': collector_name,
                    'Collector_Length_Col': collector_length_col,  # Colonna H - lunghezza in mm
                    'PhtTracking01_Right': row.get('PhtTracking01_Right', 0) if pd.notna(row.get('PhtTracking01_Right')) else 0,
                    'PhtTracking02_Right': row.get('PhtTracking02_Right', 0) if pd.notna(row.get('PhtTracking02_Right')) else 0,
                    'PhtTracking01_Left': row.get('PhtTracking01_Left', 0) if pd.notna(row.get('PhtTracking01_Left')) else 0,
                    'PhtTracking02_Left': row.get('PhtTracking02_Left', 0) if pd.notna(row.get('PhtTracking02_Left')) else 0,
                }
                all_collectors.append({
                    'data': collector_data,
                    'collector_info': collector_info
                })
        
        # Genera CONF.scl (unico file)
        print("\nGenerazione file CheckIn...")
        conf_content = []
        
        # Aggiungi Desk
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            conf_content.append(generate_desk_conf(desk_item['data'], desk_item['collector_info']))
        
        # Aggiungi Damper (una sola volta per ogni Damper unica)
        dampers_sorted = sorted(all_dampers_set, key=lambda x: x[0])
        for damper_number, collector_name in dampers_sorted:
            conf_content.append(generate_damper_conf(damper_number, collector_name))
        
        # Aggiungi Collector
        # Raggruppa Desk per Collector per calcolare DeskNumber
        collector_desk_count = {}  # {collector_name: count}
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            collector_name = desk_item['data']['Collector_Name']
            collector_desk_count[collector_name] = collector_desk_count.get(collector_name, 0) + 1
        
        for collector_item in all_collectors:
            collector_name = collector_item['data']['Collector_Name']
            desk_count = collector_desk_count.get(collector_name, 4)  # Default 4 se non trovato
            conf_content.append(generate_collector_conf(collector_item['data'], collector_item['collector_info'], desk_count))
        
        conf_file_path = os.path.join(output_folder, 'CONF.scl')
        with open(conf_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(conf_content))
        print(f"  Creato: {conf_file_path}")
        
        # Genera DigIn.scl (unico file)
        all_digin_content = []
        
        # Aggiungi Desk DigIn
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            all_digin_content.append(generate_desk_dbin(desk_item['data'], desk_item['collector_info']))
        
        # Aggiungi Damper DigIn (raggruppa per Damper)
        damper_desks = {}  # {damper_number: [desk_indices]}
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            desk_index = desk_item['data']['Desk_Index']
            damper_number = get_damper_number(desk_index)
            if damper_number not in damper_desks:
                damper_desks[damper_number] = []
            damper_desks[damper_number].append(desk_index)
        
        for damper_number, desk_indices in sorted(damper_desks.items()):
            if len(desk_indices) == 2:
                # Trova il collector_name corretto basandosi sulle desk_indices della damper
                collector_name = None
                for desk_item in all_desks:
                    if desk_item['data']['Desk_Index'] in desk_indices:
                        collector_name = desk_item['data']['Collector_Name']
                        break
                if collector_name is None:
                    collector_name = all_desks[0]['data']['Collector_Name']  # Fallback al primo se non trovato
                all_digin_content.append(generate_damper_dbin(damper_number, collector_name, desk_indices))
        
        # Aggiungi Collector DigIn (evita duplicati usando un set)
        seen_collectors = set()
        for collector_item in all_collectors:
            collector_name = collector_item['data']['Collector_Name']
            if collector_name not in seen_collectors:
                seen_collectors.add(collector_name)
                all_digin_content.append(generate_collector_dbin(collector_item['data'], collector_item['collector_info']))
        
        # Genera DigOut.scl (unico file)
        all_digout_content = []
        
        # Prima aggiungi Damper DigOut (come nell'esempio)
        for damper_number, desk_indices in sorted(damper_desks.items()):
            if len(desk_indices) == 2:
                # Trova il collector_name corretto basandosi sulle desk_indices della damper
                collector_name = None
                for desk_item in all_desks:
                    if desk_item['data']['Desk_Index'] in desk_indices:
                        collector_name = desk_item['data']['Collector_Name']
                        break
                if collector_name is None:
                    collector_name = all_desks[0]['data']['Collector_Name']  # Fallback al primo se non trovato
                all_digout_content.append(generate_damper_digout(damper_number, collector_name, desk_indices))
        
        # Poi aggiungi Desk DigOut
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            all_digout_content.append(generate_desk_digout(desk_item['data']))
        
        # Genera MAIN.scl (unico file)
        main_content = [
            '',
            ''
        ]
        
        # Raggruppa Desk per Collector per determinare DesksComm index
        collector_desks = {}  # {collector_name: [desk_items]}
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            collector_name = desk_item['data']['Collector_Name']
            if collector_name not in collector_desks:
                collector_desks[collector_name] = []
            collector_desks[collector_name].append(desk_item)
        
        # Aggiungi Desk MAIN
        for collector_name, desk_items in sorted(collector_desks.items()):
            for idx, desk_item in enumerate(desk_items, start=1):
                main_content.append(generate_desk_main(desk_item['data'], desk_item['collector_info'], idx))
        
        # Aggiungi Damper MAIN
        for damper_number, collector_name in dampers_sorted:
            main_content.append(generate_damper_main(damper_number, collector_name))
        
        # Aggiungi Collector MAIN
        for idx, collector_item in enumerate(all_collectors):
            prev_collector = None
            next_collector = None
            if idx > 0:
                prev_collector_name = all_collectors[idx-1]['data']['Collector_Name']
                prev_collector = f"Utenza{get_utenza_number(prev_collector_name)}_{prev_collector_name}"
            if idx < len(all_collectors) - 1:
                next_collector_name = all_collectors[idx+1]['data']['Collector_Name']
                next_collector = f"Utenza{get_utenza_number(next_collector_name)}_{next_collector_name}"
            main_content.append(generate_collector_main(collector_item['data'], collector_item['collector_info'], prev_collector, next_collector))
        
        main_file_path = os.path.join(output_folder, 'MAIN.scl')
        with open(main_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(main_content))
        print(f"  Creato: {main_file_path}")
        
        # Genera file .db per Desk e Damper
        for desk_item in sorted(all_desks, key=lambda x: x['data']['Desk_Index']):
            db_content = generate_desk_db(desk_item['data'])
            desk_index = desk_item['data']['Desk_Index']
            collector_name = desk_item['data']['Collector_Name']
            prefix = collector_name[:4].upper()
            db_file_path = os.path.join(output_folder, f'Desk_{prefix}CC1{desk_index%100:02d}.db')
            with open(db_file_path, 'w', encoding='utf-8') as f:
                f.write(db_content)
            print(f"  Creato: {db_file_path}")
        
        for damper_number, collector_name in dampers_sorted:
            db_content = generate_damper_db(damper_number, collector_name)
            prefix = collector_name[:4].upper()
            db_file_path = os.path.join(output_folder, f'Damper_{prefix}SD1{damper_number%100:02d}.db')
            with open(db_file_path, 'w', encoding='utf-8') as f:
                f.write(db_content)
            print(f"  Creato: {db_file_path}")
        
        # Genera file DigIn.scl unico
        if all_digin_content:
            digin_file_path = os.path.join(output_folder, 'DigIn.scl')
            with open(digin_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_digin_content))
            print(f"  Creato: {digin_file_path}")
        
        # Genera file DigOut.scl unico
        if all_digout_content:
            digout_file_path = os.path.join(output_folder, 'DigOut.scl')
            with open(digout_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_digout_content))
            print(f"  Creato: {digout_file_path}")
        
        print(f"\nGenerazione CheckIn completata! File salvati in: {output_folder}")
        return True, f"Generazione completata. File salvati in: {output_folder}"
        
    except Exception as e:
        print(f"ERRORE durante la generazione CheckIn: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)
