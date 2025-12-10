"""
Modulo per il confronto automatico tra API004 generato e API004_NEW di riferimento.
Esegue confronto file-by-file dopo ogni generazione.
"""

import os
import difflib
from pathlib import Path


def compare_files(file1_path, file2_path):
    """
    Confronta due file SCL ignorando differenze di whitespace e commenti.
    
    Args:
        file1_path (str): Percorso del primo file
        file2_path (str): Percorso del secondo file
        
    Returns:
        tuple: (bool, list) - (True se identici, lista delle differenze)
    """
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        with open(file2_path, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
    except FileNotFoundError as e:
        return False, [f"File non trovato: {e}"]
    except Exception as e:
        return False, [f"Errore lettura file: {e}"]
    
    # Normalizza le righe: rimuovi trailing whitespace e normalizza spazi multipli
    def normalize_line(line):
        # Rimuovi commenti inline (mantieni commenti standalone)
        if '//' in line:
            parts = line.split('//', 1)
            code_part = parts[0].rstrip()
            comment_part = '//' + parts[1] if len(parts) > 1 else ''
            return code_part + (' ' + comment_part if comment_part else '')
        return line.rstrip()
    
    normalized1 = [normalize_line(line) for line in lines1]
    normalized2 = [normalize_line(line) for line in lines2]
    
    # Confronta le righe normalizzate
    diff = list(difflib.unified_diff(normalized1, normalized2, 
                                     fromfile=file1_path, 
                                     tofile=file2_path,
                                     lineterm=''))
    
    return len(diff) == 0, diff


def compare_api004_folders(generated_folder, reference_folder):
    """
    Confronta tutti i file .scl tra la cartella generata e quella di riferimento.
    
    Args:
        generated_folder (str): Cartella con i file generati (API004)
        reference_folder (str): Cartella con i file di riferimento (API004_NEW)
        
    Returns:
        dict: Risultati del confronto con chiavi:
            - 'identical': lista file identici
            - 'different': lista file diversi
            - 'missing_in_generated': file presenti solo in riferimento
            - 'missing_in_reference': file presenti solo in generato
            - 'errors': errori durante il confronto
    """
    results = {
        'identical': [],
        'different': [],
        'missing_in_generated': [],
        'missing_in_reference': [],
        'errors': []
    }
    
    gen_path = Path(generated_folder)
    ref_path = Path(reference_folder)
    
    if not gen_path.exists():
        results['errors'].append(f"Cartella generata non trovata: {generated_folder}")
        return results
    
    if not ref_path.exists():
        results['errors'].append(f"Cartella riferimento non trovata: {reference_folder}")
        return results
    
    # Trova tutti i file .scl in entrambe le cartelle
    gen_scl_files = {f.name: f for f in gen_path.glob('*.scl')}
    ref_scl_files = {f.name: f for f in ref_path.glob('*.scl')}
    
    # Confronta file presenti in entrambe
    common_files = set(gen_scl_files.keys()) & set(ref_scl_files.keys())
    for filename in common_files:
        gen_file = gen_scl_files[filename]
        ref_file = ref_scl_files[filename]
        
        is_identical, diff = compare_files(str(gen_file), str(ref_file))
        if is_identical:
            results['identical'].append(filename)
        else:
            results['different'].append({
                'filename': filename,
                'diff': diff[:50]  # Limita a prime 50 righe di diff
            })
    
    # File presenti solo in riferimento
    results['missing_in_generated'] = list(set(ref_scl_files.keys()) - set(gen_scl_files.keys()))
    
    # File presenti solo in generato
    results['missing_in_reference'] = list(set(gen_scl_files.keys()) - set(ref_scl_files.keys()))
    
    return results


def run_comparison_test(selected_cab_plc='API004'):
    """
    Esegue il test di confronto automatico dopo la generazione.
    
    Args:
        selected_cab_plc (str): CAB_PLC selezionato (default: API004)
        
    Returns:
        dict: Risultati del confronto
    """
    # Per API004, la cartella è API004, non API004
    if selected_cab_plc == 'API004':
        api_folder = 'API004'
    else:
        api_folder = f'API0{selected_cab_plc[-2:]}'
    generated_folder = os.path.join('Configurazioni', selected_cab_plc, api_folder)
    reference_folder = os.path.join('Configurazioni', f'{selected_cab_plc}_NEW')
    
    # Verifica che la cartella di riferimento esista
    if not os.path.exists(reference_folder):
        print(f"ATTENZIONE: Cartella di riferimento non trovata: {reference_folder}")
        print("Il test di confronto verrà saltato.")
        return {
            'identical': [],
            'different': [],
            'missing_in_generated': [],
            'missing_in_reference': [],
            'errors': [f"Cartella riferimento non trovata: {reference_folder}"]
        }
    
    print(f"\n{'='*60}")
    print(f"TEST DI CONFRONTO: {selected_cab_plc} vs {selected_cab_plc}_NEW")
    print(f"{'='*60}")
    
    results = compare_api004_folders(generated_folder, reference_folder)
    
    # Stampa risultati
    print(f"\nFile identici: {len(results['identical'])}")
    if results['identical']:
        for f in results['identical'][:10]:  # Mostra primi 10
            print(f"  ✓ {f}")
        if len(results['identical']) > 10:
            print(f"  ... e altri {len(results['identical']) - 10} file")
    
    print(f"\nFile diversi: {len(results['different'])}")
    if results['different']:
        for item in results['different'][:5]:  # Mostra primi 5
            print(f"  ✗ {item['filename']}")
        if len(results['different']) > 5:
            print(f"  ... e altri {len(results['different']) - 5} file")
    
    print(f"\nFile mancanti in generato: {len(results['missing_in_generated'])}")
    if results['missing_in_generated']:
        for f in results['missing_in_generated'][:10]:
            print(f"  - {f}")
        if len(results['missing_in_generated']) > 10:
            print(f"  ... e altri {len(results['missing_in_generated']) - 10} file")
    
    print(f"\nFile extra in generato: {len(results['missing_in_reference'])}")
    if results['missing_in_reference']:
        for f in results['missing_in_reference'][:10]:
            print(f"  + {f}")
        if len(results['missing_in_reference']) > 10:
            print(f"  ... e altri {len(results['missing_in_reference']) - 10} file")
    
    if results['errors']:
        print(f"\nErrori: {len(results['errors'])}")
        for e in results['errors']:
            print(f"  ! {e}")
    
    print(f"\n{'='*60}\n")
    
    return results

