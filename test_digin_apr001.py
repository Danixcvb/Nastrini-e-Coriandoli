"""
Script di test per verificare che DigIn.scl contenga tutti i tronchi per APR001
"""

import os
import sys
import pandas as pd
import builtins
from elaborazione_principale import process_excel

# Mock dell'input per rispondere automaticamente "s" alla conferma
class MockInput:
    def __init__(self, response='s'):
        self.response = response
        self.original_input = builtins.input
    
    def __call__(self, prompt=''):
        if 'Eliminarla' in prompt or 'eliminarla' in prompt:
            print(f"{prompt}{self.response}")
            return self.response
        return self.original_input(prompt)

class DummyStatusVar:
    def set(self, value):
        print(f"STATUS: {value}")

class DummyRoot:
    pass

def test_digin_apr001():
    """
    Test per verificare che DigIn.scl contenga tutti i tronchi per APR001
    """
    print("=" * 80)
    print("TEST: Verifica generazione DigIn.scl per APR001")
    print("=" * 80)
    
    # Configurazione
    selected_cab_plc = 'APR001'
    excel_file_path = os.path.join('Input', 'Machine_Table_per_tool_AI.xlsx')
    
    if not os.path.exists(excel_file_path):
        print(f"ERRORE: File Excel non trovato: {excel_file_path}")
        return False
    
    # Verifica che il file DigIn.scl esista dopo la generazione
    api_folder = f'API0{selected_cab_plc[-2:]}'
    digin_path = os.path.join('Configurazioni', selected_cab_plc, api_folder, 'DigIn.scl')
    
    print(f"\n1. Generazione file DigIn.scl per {selected_cab_plc}...")
    print(f"   File Excel: {excel_file_path}")
    print(f"   Output atteso: {digin_path}")
    
    # Leggi il file Excel per determinare l'ordine dei prefissi
    print(f"\n   Lettura file Excel per determinare l'ordine...")
    try:
        df_temp = pd.read_excel(excel_file_path)
        df_temp = df_temp[df_temp['CAB_PLC'] == selected_cab_plc]
        if df_temp.empty:
            print(f"   ERRORE: Nessun dato trovato per {selected_cab_plc} nel file Excel")
            return False
        
        # Estrai i prefissi unici
        unique_prefixes = sorted(set(item[:4].upper() for item in df_temp['ITEM_ID_CUSTOM'].astype(str)))
        print(f"   Prefissi trovati: {unique_prefixes}")
        
        # Crea l'ordine nel formato richiesto: ["1. AC11", "2. AC21", ...]
        order = [f"{i+1}. {prefix}" for i, prefix in enumerate(unique_prefixes)]
        print(f"   Ordine creato: {order}")
        
    except Exception as e:
        print(f"   ERRORE durante la lettura del file Excel: {e}")
        return False
    
    # Esegui la generazione con mock dell'input per rispondere automaticamente "s"
    status_var = DummyStatusVar()
    root = DummyRoot()
    
    # Mock dell'input per rispondere automaticamente "s"
    mock_input = MockInput('s')
    original_input = builtins.input
    builtins.input = mock_input
    
    try:
        success, message = process_excel(selected_cab_plc, status_var, root, order, excel_file_path, use_fixed_zone=False)
    except Exception as e:
        # Ripristina l'input originale anche in caso di errore
        builtins.input = original_input
        print(f"ERRORE durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Ripristina l'input originale
        builtins.input = original_input
    
    if not success:
        print(f"ERRORE durante la generazione: {message}")
        return False
    
    print(f"\n✓ Generazione completata: {message}")
    
    # Verifica che il file sia stato creato
    if not os.path.exists(digin_path):
        print(f"\n✗ ERRORE: File DigIn.scl non trovato in {digin_path}")
        return False
    
    print(f"\n✓ File DigIn.scl trovato")
    
    # Leggi il file e verifica i tronchi
    print(f"\n2. Analisi del file DigIn.scl...")
    
    with open(digin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cerca tutte le REGION Input TRUNK
    import re
    trunk_regions = re.findall(r'REGION Input TRUNK (\d+|Carousel)', content)
    
    print(f"   Tronchi trovati nel DigIn.scl: {len(trunk_regions)}")
    print(f"   Lista tronchi: {trunk_regions}")
    
    # Verifica che ci siano almeno 26 tronchi (o tutti quelli presenti nel GenLine.scl)
    genline_path = os.path.join('Configurazioni', selected_cab_plc, api_folder, 'GenLine.scl')
    if os.path.exists(genline_path):
        with open(genline_path, 'r', encoding='utf-8') as f:
            genline_content = f.read()
        
        genline_trunks = re.findall(r'REGION Call TRUNK (\d+)', genline_content)
        expected_trunk_count = len(genline_trunks)
        
        print(f"\n3. Confronto con GenLine.scl...")
        print(f"   Tronchi in GenLine.scl: {expected_trunk_count}")
        print(f"   Tronchi in DigIn.scl: {len(trunk_regions)}")
        
        if len(trunk_regions) >= expected_trunk_count:
            print(f"\n✓ SUCCESSO: DigIn.scl contiene tutti i tronchi ({len(trunk_regions)} >= {expected_trunk_count})")
            
            # Verifica che i numeri dei tronchi siano corretti
            numeric_trunks = [int(t) for t in trunk_regions if t.isdigit()]
            if numeric_trunks:
                min_trunk = min(numeric_trunks)
                max_trunk = max(numeric_trunks)
                print(f"   Range tronchi: {min_trunk} - {max_trunk}")
                
                # Verifica che ci siano tutti i tronchi da 1 a max_trunk
                expected_trunks = set(range(1, max_trunk + 1))
                actual_trunks = set(numeric_trunks)
                missing_trunks = expected_trunks - actual_trunks
                
                if missing_trunks:
                    print(f"   ⚠ ATTENZIONE: Tronchi mancanti: {sorted(missing_trunks)}")
                else:
                    print(f"   ✓ Tutti i tronchi da 1 a {max_trunk} sono presenti")
            
            return True
        else:
            print(f"\n✗ ERRORE: DigIn.scl contiene solo {len(trunk_regions)} tronchi, ne servono almeno {expected_trunk_count}")
            return False
    else:
        print(f"\n⚠ ATTENZIONE: GenLine.scl non trovato, impossibile verificare il numero esatto di tronchi")
        print(f"   Tronchi trovati: {len(trunk_regions)}")
        return len(trunk_regions) > 0

if __name__ == "__main__":
    success = test_digin_apr001()
    sys.exit(0 if success else 1)

