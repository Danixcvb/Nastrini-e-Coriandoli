"""
Script principale per l'avvio dell'applicazione di configurazione nastri trasportatori.
"""

import os
import sys
from interfaccia_grafica import create_gui
def main():
    """
    Funzione principale che avvia l'applicazione.
    """
    try:
        # Assicurati che il percorso di esecuzione sia corretto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Aggiungi la directory corrente al PYTHONPATH
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        
        # Crea l'interfaccia grafica
        root = create_gui()
        
        # Avvia il loop principale dell'applicazione
        root.mainloop()
    except Exception as e:
        print(f"Errore durante l'avvio dell'applicazione: {e}")
        input("Premi INVIO per chiudere...")  # Mantiene la finestra aperta in caso di errore

if __name__ == "__main__":
    main() 