"""
Script per confrontare i file generati per API004 con quelli in API004_UPDATED_V3
"""

import os
import difflib
from pathlib import Path

def compare_files(file1_path, file2_path):
    """Confronta due file ignorando differenze minori di whitespace"""
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        with open(file2_path, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
    except FileNotFoundError as e:
        return False, [f"File non trovato: {e}"]
    except Exception as e:
        return False, [f"Errore lettura file: {e}"]
    
    # Normalizza le righe
    def normalize_line(line):
        return line.rstrip()
    
    normalized1 = [normalize_line(line) for line in lines1]
    normalized2 = [normalize_line(line) for line in lines2]
    
    diff = list(difflib.unified_diff(normalized1, normalized2, 
                                     fromfile=file1_path, 
                                     tofile=file2_path,
                                     lineterm=''))
    
    return len(diff) == 0, diff

def main():
    generated_folder = Path('Configurazioni/API004/API004')
    reference_folder = Path('Configurazioni/API004_UPDATED_V3')
    
    if not generated_folder.exists():
        print(f"ERRORE: Cartella generata non trovata: {generated_folder}")
        return
    
    if not reference_folder.exists():
        print(f"ERRORE: Cartella riferimento non trovata: {reference_folder}")
        return
    
    # Confronta file .scl e .db
    generated_files = {}
    reference_files = {}
    
    for ext in ['.scl', '.db']:
        for f in generated_folder.glob(f'*{ext}'):
            if f.name not in ['selected_order.txt', 'PCE_Input_Summary.txt', 'Zones_Input_Summary.txt']:
                generated_files[f.name] = f
        
        for f in reference_folder.glob(f'*{ext}'):
            reference_files[f.name] = f
    
    print("=" * 80)
    print("CONFRONTO FILE API004 GENERATO vs API004_UPDATED_V3")
    print("=" * 80)
    
    identical = []
    different = []
    missing_in_generated = []
    missing_in_reference = []
    
    # File comuni
    common_files = set(generated_files.keys()) & set(reference_files.keys())
    for filename in sorted(common_files):
        gen_file = generated_files[filename]
        ref_file = reference_files[filename]
        is_identical, diff = compare_files(str(gen_file), str(ref_file))
        if is_identical:
            identical.append(filename)
        else:
            different.append((filename, diff[:20]))  # Prime 20 righe di diff
    
    # File mancanti
    missing_in_generated = sorted(set(reference_files.keys()) - set(generated_files.keys()))
    missing_in_reference = sorted(set(generated_files.keys()) - set(reference_files.keys()))
    
    print(f"\nFile identici: {len(identical)}")
    if len(identical) > 0:
        for f in identical[:10]:
            print(f"  [OK] {f}")
        if len(identical) > 10:
            print(f"  ... e altri {len(identical) - 10} file")
    
    print(f"\nFile diversi: {len(different)}")
    for filename, diff_lines in different[:10]:
        print(f"  [DIFF] {filename}")
        if diff_lines:
            print(f"    Prime differenze:")
            for line in diff_lines[:5]:
                try:
                    print(f"      {line}")
                except UnicodeEncodeError:
                    print(f"      [linea con caratteri speciali]")
    
    print(f"\nFile mancanti in generato: {len(missing_in_generated)}")
    for f in missing_in_generated[:20]:
        print(f"  - {f}")
    
    print(f"\nFile extra in generato: {len(missing_in_reference)}")
    for f in missing_in_reference[:20]:
        print(f"  + {f}")
    
    # Verifica specifica per file .db vs .scl
    print("\n" + "=" * 80)
    print("VERIFICA ESTENSIONI FILE")
    print("=" * 80)
    
    db_files_gen = [f for f in generated_files.keys() if f.endswith('.db')]
    scl_files_gen = [f for f in generated_files.keys() if f.endswith('.scl')]
    db_files_ref = [f for f in reference_files.keys() if f.endswith('.db')]
    scl_files_ref = [f for f in reference_files.keys() if f.endswith('.scl')]
    
    print(f"\nFile .db generati: {len(db_files_gen)}")
    print(f"File .scl generati: {len(scl_files_gen)}")
    print(f"File .db riferimento: {len(db_files_ref)}")
    print(f"File .scl riferimento: {len(scl_files_ref)}")
    
    # Verifica DbiLine e DbiTrunkLN
    dbi_line_gen = [f for f in generated_files.keys() if f.startswith('DbiLine')]
    dbi_trunk_gen = [f for f in generated_files.keys() if f.startswith('DbiTrunkLN')]
    dbi_line_ref = [f for f in reference_files.keys() if f.startswith('DbiLine')]
    dbi_trunk_ref = [f for f in reference_files.keys() if f.startswith('DbiTrunkLN')]
    
    print(f"\nDbiLine generati: {sorted(dbi_line_gen)}")
    print(f"DbiLine riferimento: {sorted(dbi_line_ref)}")
    print(f"DbiTrunkLN generati: {sorted(dbi_trunk_gen)}")
    print(f"DbiTrunkLN riferimento: {sorted(dbi_trunk_ref)}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

