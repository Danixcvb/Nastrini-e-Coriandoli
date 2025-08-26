"""
Questo modulo contiene le funzioni di utilità per l'elaborazione dei dati.
Include funzioni per l'estrazione di numeri, conteggio di occorrenze e gestione dei valori predefiniti.
"""

import re
import pandas as pd

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