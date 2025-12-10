"""
Script di test per verificare la generazione automatica dei file SCL per API004
con le linee CP21, DC11, CA11, CA31 in ordine.

Questo script simula la chiamata a process_excel senza utilizzare l'interfaccia grafica.
"""

import os
import sys

# Aggiungi la directory root al path per gli import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elaborazione_principale import process_excel
from PyQt6.QtCore import QThread

# Configurazione di test
TEST_CAB_PLC = "API004"
TEST_ORDER = ["CP21", "DC11", "CA11", "CA31"]
TEST_EXCEL_FILE = "Input/Machine_Table_per_tool_AI.xlsx"  # File Excel corretto con tutte le colonne

# Classe dummy per simulare status_var
class DummyStatusVar:
    def __init__(self):
        self.value = ""
    
    def set(self, value):
        self.value = value
        print(f"STATUS: {value}")

# Classe dummy per simulare root
class DummyRoot:
    pass

def test_generazione_api004():
    """
    Testa la generazione dei file per API004 con le linee specificate.
    """
    print("=" * 80)
    print("TEST GENERAZIONE API004")
    print("=" * 80)
    print(f"CAB_PLC: {TEST_CAB_PLC}")
    print(f"Ordine linee: {TEST_ORDER}")
    print(f"File Excel: {TEST_EXCEL_FILE}")
    print("=" * 80)
    
    # Verifica che il file Excel esista
    if not os.path.exists(TEST_EXCEL_FILE):
        print(f"ERRORE: File Excel non trovato: {TEST_EXCEL_FILE}")
        print("Assicurati che il file esista nella cartella Input/")
        return False
    
    # Crea gli oggetti dummy necessari
    status_var = DummyStatusVar()
    root = DummyRoot()
    
    # Elimina la cartella di output esistente per test pulito
    api_folder = f'API0{TEST_CAB_PLC[-2:]}'
    output_folder = os.path.join('Configurazioni', TEST_CAB_PLC, api_folder)
    if os.path.exists(output_folder):
        import shutil
        print(f"\nEliminazione cartella esistente per test pulito: {output_folder}")
        try:
            shutil.rmtree(output_folder)
            print("Cartella eliminata con successo")
        except Exception as e:
            print(f"Errore durante eliminazione cartella: {e}")
    
    try:
        # Chiama process_excel con i parametri di test
        print("\nAvvio generazione...")
        success, message = process_excel(
            selected_cab_plc=TEST_CAB_PLC,
            status_var=status_var,
            root=root,
            order=TEST_ORDER,
            excel_file_path=TEST_EXCEL_FILE
        )
        
        print(f"\nRisultato: {'SUCCESSO' if success else 'ERRORE'}")
        print(f"Messaggio: {message}")
        
        # Verifica i file generati
        api_folder = f'API0{TEST_CAB_PLC[-2:]}'
        output_folder = os.path.join('Configurazioni', TEST_CAB_PLC, api_folder)
        
        print(f"\n{'=' * 80}")
        print("VERIFICA FILE GENERATI")
        print(f"{'=' * 80}")
        print(f"Cartella di output: {output_folder}")
        
        if os.path.exists(output_folder):
            files_generated = []
            for root_dir, dirs, files in os.walk(output_folder):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root_dir, file), output_folder)
                    files_generated.append(rel_path)
            
            files_generated.sort()
            print(f"\nFile trovati ({len(files_generated)}):")
            for file in files_generated:
                print(f"  - {file}")
            
            # Verifica file chiave
            key_files = [
                'DigIn.scl',
                'GenLine.scl',
                'Main.scl',
                'PCE_Input.scl',
                'PCE_Output.scl'
            ]
            
            print(f"\n{'=' * 80}")
            print("VERIFICA FILE CHIAVE")
            print(f"{'=' * 80}")
            for key_file in key_files:
                file_path = os.path.join(output_folder, key_file)
                exists = os.path.exists(file_path)
                status = "[OK]" if exists else "[MISSING]"
                print(f"{status} {key_file}")
            
            # Verifica file CONF_T e MAIN
            conf_files = [f for f in files_generated if f.startswith('CONF_T') and f.endswith('.scl')]
            main_files = [f for f in files_generated if f.startswith('MAIN') and f.endswith('.scl')]
            
            print(f"\n{'=' * 80}")
            print("RIEPILOGO FILE GENERATI")
            print(f"{'=' * 80}")
            print(f"File CONF_T: {len(conf_files)}")
            for conf_file in sorted(conf_files):
                print(f"  - {conf_file}")
            
            print(f"\nFile MAIN: {len(main_files)}")
            for main_file in sorted(main_files):
                print(f"  - {main_file}")
            
            # Verifica presenza Carousel
            carousel_files = [f for f in files_generated if 'Carousel' in f]
            if carousel_files:
                print(f"\nFile Carousel trovati: {len(carousel_files)}")
                for carousel_file in sorted(carousel_files):
                    print(f"  - {carousel_file}")
            
            # Verifica DigIn.scl contiene Carousel
            digin_path = os.path.join(output_folder, 'DigIn.scl')
            if os.path.exists(digin_path):
                with open(digin_path, 'r', encoding='utf-8') as f:
                    digin_content = f.read()
                    if 'REGION Input CAROUSEL' in digin_content:
                        print("\n[OK] DigIn.scl contiene sezione CAROUSEL")
                        # Conta quante sezioni CAROUSEL ci sono
                        carousel_count = digin_content.count('REGION Input CAROUSEL')
                        print(f"     Trovate {carousel_count} sezione/i CAROUSEL")
                    else:
                        print("\n[ERRORE] DigIn.scl NON contiene sezione CAROUSEL")
                    
                    if 'REGION Input LINE' in digin_content:
                        line_count = digin_content.count('REGION Input LINE')
                        print(f"[OK] DigIn.scl contiene {line_count} sezione/i LINE")
                    else:
                        print("[ERRORE] DigIn.scl NON contiene sezione LINE")
                    
                    if 'REGION Input Badge Reader' in digin_content:
                        print("[OK] DigIn.scl contiene sezione Badge Reader")
                    else:
                        print("[INFO] DigIn.scl NON contiene sezione Badge Reader (normale se non CA12/CA22/CA32)")
                    
                    if 'REGION Input SIDEINPUT Carousel' in digin_content:
                        print("[OK] DigIn.scl contiene sezione SIDEINPUT Carousel")
                    else:
                        print("[ERRORE] DigIn.scl NON contiene sezione SIDEINPUT Carousel")
                    
                    if 'REGION Input CONVEYOR' in digin_content:
                        conveyor_count = digin_content.count('REGION Input CONVEYOR')
                        print(f"[OK] DigIn.scl contiene {conveyor_count} sezione/i CONVEYOR")
                    else:
                        print("[ERRORE] DigIn.scl NON contiene sezione CONVEYOR")
            
        else:
            print(f"ERRORE: Cartella di output non trovata: {output_folder}")
            return False
        
        print(f"\n{'=' * 80}")
        print("TEST COMPLETATO")
        print(f"{'=' * 80}")
        return success
        
    except Exception as e:
        print(f"\nERRORE durante il test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Script di test per generazione API004")
    print("Questo script testerà la generazione automatica dei file SCL\n")
    
    result = test_generazione_api004()
    
    if result:
        print("\n[SUCCESSO] Test completato con successo!")
        sys.exit(0)
    else:
        print("\n[ERRORE] Test fallito!")
        sys.exit(1)

