"""
Questo modulo gestisce l'installazione dei pacchetti Python necessari per il funzionamento dell'applicazione.
Contiene la funzione install_and_import che verifica e installa i pacchetti richiesti se non sono già presenti.
"""

import subprocess
import sys

def install_and_import(package):
    """
    Installa un pacchetto Python se non è già presente nel sistema.
    
    Args:
        package (str): Nome del pacchetto da installare
        
    Returns:
        bool: True se l'installazione è riuscita o il pacchetto è già presente, False altrimenti
    """
    try:
        __import__(package)
        print(f"Il pacchetto '{package}' è già installato.")
    except ImportError:
        print(f"Il pacchetto '{package}' non è installato. Installazione in corso...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Il pacchetto '{package}' è stato installato con successo.")
        except Exception as e:
            print(f"Errore durante l'installazione del pacchetto '{package}': {e}")
            return False
    return True

# Lista dei pacchetti da installare
packages_to_install = ["pandas", "openpyxl"]
install_success = True

# Installa i pacchetti richiesti
for package in packages_to_install:
    if not install_and_import(package):
        install_success = False

# Importa pandas solo se l'installazione è riuscita
if install_success:
    import pandas as pd 