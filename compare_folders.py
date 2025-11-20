"""
Script completo per confrontare le cartelle API004 e API004_NEW
e generare un report dettagliato delle differenze.
"""

import os
import difflib
from pathlib import Path
from collections import defaultdict

def normalize_line(line):
    """Normalizza una riga per il confronto: rimuove trailing whitespace e normalizza spazi."""
    return line.rstrip()

def compare_file_content(file1_path, file2_path):
    """
    Confronta il contenuto di due file riga per riga.
    
    Returns:
        dict: {
            'identical': bool,
            'total_lines': int,
            'differences': list of dict con 'line_num', 'type' ('added', 'removed', 'modified'), 'content'
        }
    """
    try:
        with open(file1_path, 'r', encoding='utf-8-sig') as f1:
            lines1 = [normalize_line(line) for line in f1.readlines()]
        with open(file2_path, 'r', encoding='utf-8-sig') as f2:
            lines2 = [normalize_line(line) for line in f2.readlines()]
    except FileNotFoundError as e:
        return {'identical': False, 'error': str(e), 'total_lines': 0, 'differences': []}
    except Exception as e:
        return {'identical': False, 'error': str(e), 'total_lines': max(len(lines1) if 'lines1' in locals() else 0, len(lines2) if 'lines2' in locals() else 0), 'differences': []}
    
    if lines1 == lines2:
        return {'identical': True, 'total_lines': len(lines1), 'differences': []}
    
    # Usa difflib per trovare le differenze
    diff = list(difflib.unified_diff(lines1, lines2, 
                                     fromfile=str(file1_path), 
                                     tofile=str(file2_path),
                                     lineterm='',
                                     n=0))
    
    differences = []
    for line in diff:
        if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
            continue
        if line.startswith('+'):
            differences.append({'type': 'added', 'content': line[1:], 'line_num': None})
        elif line.startswith('-'):
            differences.append({'type': 'removed', 'content': line[1:], 'line_num': None})
    
    return {
        'identical': False,
        'total_lines': max(len(lines1), len(lines2)),
        'differences': differences[:50]  # Limita a 50 differenze per file
    }

def compare_folders(folder1, folder2):
    """
    Confronta due cartelle e tutti i loro file.
    
    Returns:
        dict: Risultati del confronto
    """
    results = {
        'identical_files': [],
        'different_files': [],
        'only_in_folder1': [],
        'only_in_folder2': [],
        'errors': []
    }
    
    if not os.path.exists(folder1):
        results['errors'].append(f"Cartella non trovata: {folder1}")
        return results
    
    if not os.path.exists(folder2):
        results['errors'].append(f"Cartella non trovata: {folder2}")
        return results
    
    # Trova tutti i file .scl in entrambe le cartelle
    files1 = set()
    files2 = set()
    
    for root, dirs, files in os.walk(folder1):
        for file in files:
            if file.endswith('.scl'):
                rel_path = os.path.relpath(os.path.join(root, file), folder1)
                files1.add(rel_path)
    
    for root, dirs, files in os.walk(folder2):
        for file in files:
            if file.endswith('.scl'):
                rel_path = os.path.relpath(os.path.join(root, file), folder2)
                files2.add(rel_path)
    
    # File solo in folder1
    results['only_in_folder1'] = sorted(files1 - files2)
    
    # File solo in folder2
    results['only_in_folder2'] = sorted(files2 - files1)
    
    # File comuni
    common_files = files1 & files2
    
    # Confronta i file comuni
    for rel_path in sorted(common_files):
        file1_path = os.path.join(folder1, rel_path)
        file2_path = os.path.join(folder2, rel_path)
        
        comparison = compare_file_content(file1_path, file2_path)
        
        if 'error' in comparison:
            results['errors'].append(f"{rel_path}: {comparison['error']}")
        elif comparison['identical']:
            results['identical_files'].append(rel_path)
        else:
            results['different_files'].append({
                'file': rel_path,
                'total_lines': comparison['total_lines'],
                'num_differences': len(comparison['differences']),
                'differences': comparison['differences']
            })
    
    return results

def print_comparison_report(results, folder1_name, folder2_name):
    """Stampa un report dettagliato del confronto."""
    print("=" * 80)
    print(f"REPORT CONFRONTO: {folder1_name} vs {folder2_name}")
    print("=" * 80)
    print()
    
    print(f"File identici: {len(results['identical_files'])}")
    print(f"File diversi: {len(results['different_files'])}")
    print(f"File solo in {folder1_name}: {len(results['only_in_folder1'])}")
    print(f"File solo in {folder2_name}: {len(results['only_in_folder2'])}")
    print(f"Errori: {len(results['errors'])}")
    print()
    
    if results['only_in_folder1']:
        print(f"\nFile presenti solo in {folder1_name}:")
        for file in results['only_in_folder1'][:20]:
            print(f"  - {file}")
        if len(results['only_in_folder1']) > 20:
            print(f"  ... e altri {len(results['only_in_folder1']) - 20} file")
    
    if results['only_in_folder2']:
        print(f"\nFile presenti solo in {folder2_name}:")
        for file in results['only_in_folder2'][:20]:
            print(f"  - {file}")
        if len(results['only_in_folder2']) > 20:
            print(f"  ... e altri {len(results['only_in_folder2']) - 20} file")
    
    if results['different_files']:
        print(f"\nFile con differenze ({len(results['different_files'])}):")
        for item in results['different_files'][:30]:
            print(f"\n  {item['file']}:")
            print(f"    Righe totali: {item['total_lines']}")
            print(f"    Differenze trovate: {item['num_differences']}")
            if item['differences']:
                print(f"    Prime differenze:")
                for diff in item['differences'][:5]:
                    type_symbol = '+' if diff['type'] == 'added' else '-'
                    content_preview = diff['content'][:60] + '...' if len(diff['content']) > 60 else diff['content']
                    try:
                        print(f"      {type_symbol} {content_preview}")
                    except UnicodeEncodeError:
                        print(f"      {type_symbol} [contenuto non stampabile]")
        
        if len(results['different_files']) > 30:
            print(f"\n  ... e altri {len(results['different_files']) - 30} file con differenze")
    
    if results['errors']:
        print(f"\nErrori durante il confronto:")
        for error in results['errors'][:10]:
            print(f"  - {error}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Percorsi delle cartelle
    api004_folder = os.path.join('Configurazioni', 'API004')
    api004_new_folder = os.path.join('Configurazioni', 'API004_NEW')
    
    print("Confronto in corso...")
    print(f"Cartella 1: {api004_folder}")
    print(f"Cartella 2: {api004_new_folder}")
    print()
    
    results = compare_folders(api004_folder, api004_new_folder)
    print_comparison_report(results, 'API004', 'API004_NEW')
    
    # Salva risultati in un file
    output_file = 'comparison_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("REPORT CONFRONTO API004 vs API004_NEW\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"File identici: {len(results['identical_files'])}\n")
        f.write(f"File diversi: {len(results['different_files'])}\n")
        f.write(f"File solo in API004: {len(results['only_in_folder1'])}\n")
        f.write(f"File solo in API004_NEW: {len(results['only_in_folder2'])}\n")
        f.write(f"Errori: {len(results['errors'])}\n\n")
        
        if results['different_files']:
            f.write("\nFILE CON DIFFERENZE:\n")
            f.write("-" * 80 + "\n")
            for item in results['different_files']:
                f.write(f"\n{item['file']}:\n")
                f.write(f"  Righe totali: {item['total_lines']}\n")
                f.write(f"  Differenze: {item['num_differences']}\n")
        
        if results['only_in_folder1']:
            f.write("\n\nFILE SOLO IN API004:\n")
            f.write("-" * 80 + "\n")
            for file in results['only_in_folder1']:
                f.write(f"  - {file}\n")
        
        if results['only_in_folder2']:
            f.write("\n\nFILE SOLO IN API004_NEW:\n")
            f.write("-" * 80 + "\n")
            for file in results['only_in_folder2']:
                f.write(f"  - {file}\n")
    
    print(f"\nReport salvato in: {output_file}")

