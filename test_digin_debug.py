"""
Script di debug per verificare cosa contiene trunk_to_line_mapping e il DataFrame
"""

import os
import sys
import pandas as pd
from elaborazione_principale import process_excel

class DummyStatusVar:
    def set(self, value):
        print(f"STATUS: {value}")

class DummyRoot:
    pass

def test_debug_trunks():
    """
    Test per verificare cosa contiene trunk_to_line_mapping e il DataFrame
    """
    print("=" * 80)
    print("DEBUG: Verifica trunk_to_line_mapping e DataFrame")
    print("=" * 80)
    
    selected_cab_plc = 'APR001'
    excel_file_path = os.path.join('Input', 'Machine_Table_per_tool_AI.xlsx')
    
    # Leggi il file Excel
    print(f"\n1. Lettura file Excel...")
    df = pd.read_excel(excel_file_path)
    df = df[df['CAB_PLC'] == selected_cab_plc]
    df = df[df['ITEM_TRUNK'].astype(float) != 0]
    
    print(f"   Righe nel DataFrame: {len(df)}")
    
    # Ottieni tutti i tronchi unici
    trunks_from_df = sorted(df['ITEM_TRUNK'].dropna().unique())
    trunks_from_df = [int(t) for t in trunks_from_df if float(t) != 0]
    print(f"   Tronchi unici dal DataFrame: {len(trunks_from_df)}")
    print(f"   Lista tronchi: {trunks_from_df}")
    
    # Verifica il GenLine.scl per vedere quanti tronchi dovrebbero esserci
    genline_path = os.path.join('Configurazioni', selected_cab_plc, 'API001', 'GenLine.scl')
    if os.path.exists(genline_path):
        with open(genline_path, 'r', encoding='utf-8') as f:
            genline_content = f.read()
        
        import re
        genline_trunks = re.findall(r'REGION Call TRUNK (\d+)', genline_content)
        print(f"\n2. Tronchi in GenLine.scl: {len(genline_trunks)}")
        print(f"   Lista: {sorted([int(t) for t in genline_trunks])}")
    
    # Verifica il DigIn.scl attuale
    digin_path = os.path.join('Configurazioni', selected_cab_plc, 'API001', 'DigIn.scl')
    if os.path.exists(digin_path):
        with open(digin_path, 'r', encoding='utf-8') as f:
            digin_content = f.read()
        
        import re
        digin_trunks = re.findall(r'REGION Input TRUNK (\d+|Carousel)', digin_content)
        print(f"\n3. Tronchi in DigIn.scl attuale: {len(digin_trunks)}")
        print(f"   Lista: {sorted([int(t) if t.isdigit() else 0 for t in digin_trunks])}")
    
    print(f"\n4. Confronto:")
    print(f"   Tronchi nel DataFrame: {len(trunks_from_df)}")
    if os.path.exists(genline_path):
        print(f"   Tronchi in GenLine.scl: {len(genline_trunks)}")
    if os.path.exists(digin_path):
        print(f"   Tronchi in DigIn.scl: {len(digin_trunks)}")
        if os.path.exists(genline_path):
            if len(digin_trunks) < len(genline_trunks):
                print(f"\n   ✗ PROBLEMA: DigIn.scl contiene solo {len(digin_trunks)} tronchi invece di {len(genline_trunks)}")
                missing = set([int(t) for t in genline_trunks]) - set([int(t) if t.isdigit() else 0 for t in digin_trunks])
                print(f"   Tronchi mancanti: {sorted(missing)}")
            else:
                print(f"\n   ✓ OK: DigIn.scl contiene tutti i tronchi")

if __name__ == "__main__":
    test_debug_trunks()

