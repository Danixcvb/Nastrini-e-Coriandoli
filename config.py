"""
Questo modulo gestisce il salvataggio e il caricamento delle configurazioni dell'applicazione,
come l'ultimo percorso del file Excel selezionato.
"""

import os
import json

# Nome del file di configurazione
CONFIG_FILE = "app_config.json"

def save_last_excel_path(file_path):
    """
    Salva l'ultimo percorso del file Excel selezionato.
    
    Args:
        file_path (str): Percorso del file Excel da salvare
    """
    config = {}
    
    # Carica la configurazione esistente se presente
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Se il file è corrotto o non può essere letto, inizia con un dizionario vuoto
            pass
    
    # Aggiorna il percorso del file Excel
    config['last_excel_path'] = file_path
    
    # Salva la configurazione aggiornata
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except IOError:
        # Ignora gli errori di scrittura
        pass

def get_last_excel_path():
    """
    Recupera l'ultimo percorso del file Excel salvato.
    
    Returns:
        str: Percorso dell'ultimo file Excel selezionato, None se non presente o non valido
    """
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Verifica se il percorso esiste
        file_path = config.get('last_excel_path')
        if file_path and os.path.exists(file_path):
            return file_path
        return None
    except (json.JSONDecodeError, IOError):
        # Se il file è corrotto o non può essere letto, restituisci None
        return None 