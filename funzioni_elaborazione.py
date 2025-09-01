"""
Questo modulo contiene le funzioni di utilità per l'elaborazione dei dati.
Include funzioni per l'estrazione di numeri, conteggio di occorrenze e gestione dei valori predefiniti.
"""

import re
import pandas as pd
import math # Added import for math module

def get_last_three_digits(s):
    """
    Estrae le ultime tre cifre da una stringa.
    
    Args:
        s (str): Stringa da cui estrarre le cifre
        
    Returns:
        int: Le ultime tre cifre come numero intero, o 0 se non ci sono abbastanza cifre
    """
    digits = ''.join(filter(str.isdigit, s))
    return int(digits[-3:]) if len(digits) >= 3 else 0

def count_ca_occurrences(s):
    """
    Conta le occorrenze di "CA" in una stringa (case insensitive).
    
    Args:
        s (str): Stringa in cui cercare
        
    Returns:
        int: Numero di occorrenze di "CA"
    """
    return s.upper().count('CA')

def extract_ca_numbers(s):
    """
    Estrae i numeri che seguono "CA" in una stringa.
    
    Args:
        s (str): Stringa da cui estrarre i numeri
        
    Returns:
        list: Lista di numeri trovati dopo "CA"
    """
    return [int(num) for num in re.findall(r'CA(\d+)', s.upper())]

def get_value_or_default(value, default):
    """
    Restituisce il valore se non è vuoto, altrimenti restituisce il valore predefinito.
    
    Args:
        value: Valore da controllare
        default: Valore predefinito da restituire se value è vuoto
        
    Returns:
        Il valore originale o il valore predefinito
    """
    return value if not pd.isna(value) else default

def extract_numeric_part(s):
    """
    Estrae la parte numerica da una stringa.
    
    Args:
        s (str): Stringa da cui estrarre i numeri
        
    Returns:
        int: Numero estratto o 0 se non ci sono numeri
    """
    numbers = re.findall(r'\d+', s)
    if numbers:
        return int(''.join(numbers))
    return 0 

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

def format_datalogic_hwid(item_id_custom):
    """
    Formatta l'item_id_custom per gli HWID dei Datalogic.
    Es. "ca32sc009" -> "CA32+SC009"
    """
    # Estrae le parti alfabetiche e numeriche
    matches = re.findall(r'([A-Za-z]+)(\d+)([A-Za-z]+)(\d+)', item_id_custom)
    if matches:
        p1_alpha, p1_num, p2_alpha, p2_num = matches[0]
        return f"{p1_alpha.upper()}{p1_num}+{p2_alpha.upper()}{p2_num}"
    return item_id_custom.upper() # Fallback se il formato non corrisponde

# def generate_power_supply_breaker_status_ref(cab_plc, item_id_custom):
#     """
#     Genera la stringa per DriveInterface.In.EOk basata sul CAB_PLC e ITEM_ID_CUSTOM.
#     Es. CAB_PLC='API004', ITEM_ID_CUSTOM='CA11ST001' -> 'MCPCA11_130F1_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_INVERTER_ST001_ST007'
#     """
#     # Estrai il prefisso dalla CAB_PLC (es. API004 -> CA)
#     # prefix_cab = ""
#     # if cab_plc.startswith("API"):
#     #     prefix_cab = cab_plc[3:] # Prende solo il numero (es. "004")
#     # elif cab_plc.startswith("APR"):
#     #     prefix_cab = cab_plc[3:] # Prende solo il numero (es. "001")
    
#     # # Estrai il prefisso della linea da item_id_custom (es. CA11ST001 -> CA11)
#     # line_prefix_match = re.match(r'([A-Z]{2}\d{2})', item_id_custom.upper())
#     # line_prefix = line_prefix_match.group(1) if line_prefix_match else ""

#     # # Estrai l'ultima parte di item_id_custom (es. CA11ST001 -> ST001)
#     # last_part_match = re.search(r'([A-Z]{2}\d{3})', item_id_custom.upper())
#     # last_part = last_part_match.group(1) if last_part_match else ""
    
#     # # Costruisci la stringa finale
#     # # La parte 130F1 e ST007 sono assunte come fisse per ora in base all'esempio
#     # # TODO: questi valori potrebbero dover essere derivati dinamicamente se cambiano
#     # return f"MCP{line_prefix}_130F1_400VAC_POWER_SUPPLY_CIRCUIT_BREAKER_STATUS_INVERTER_{last_part}_ST007"


def calculate_tracking_slot_length(component_type, item_l_float):
    """
    Calcola la lunghezza dello slot di tracciamento in base al tipo di componente e alla lunghezza dell'elemento.
    
    Args:
        component_type (str): Tipo di componente (es. "Carousel", "Conveyor")
        item_l_float (float): Lunghezza dell'elemento in metri
        
    Returns:
        float: La lunghezza dello slot di tracciamento calcolata
    """
    if component_type == "Carousel":
        # Logica specifica per i caroselli: item_l / 400, arrotondato al multiplo più vicino di 0.02
        calculated_value = item_l_float / 400.0
        # Arrotonda per eccesso al multiplo successivo di 0.02
        return round(math.ceil(calculated_value / 0.02) * 0.02, 4) # Arrotonda a 4 decimali per precisione
    else:
        return 0.04 # Valore di default per tutti gli altri componenti 