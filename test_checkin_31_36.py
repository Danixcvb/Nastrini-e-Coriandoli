"""
Script di test per generare solo Desk 31-36 e confrontare con gli esempi.
"""
import os
import sys
import pandas as pd
from generazione_checkin import generate_checkin_files, read_checkin_excel

def test_checkin_generation():
    """Testa la generazione CheckIn per Desk 31-36."""
    
    # Percorsi file
    checkin_excel_path = os.path.join('Input', 'CheckInExample', 'CHECK_IN_MISURATOR (version 1).xlsx')
    machine_table_path = os.path.join('Input', 'Machine_Table_per_tool_AI.xlsx')
    output_folder = 'Output/CheckIn_Test'
    
    # Verifica file esistenza
    if not os.path.exists(checkin_excel_path):
        print(f"ERRORE: File CheckIn non trovato: {checkin_excel_path}")
        return False
    
    if not os.path.exists(machine_table_path):
        print(f"ERRORE: Machine table non trovata: {machine_table_path}")
        return False
    
    # Leggi il file Excel e filtra solo Desk 31-36
    print("Lettura file Excel CheckIn...")
    df_checkin = read_checkin_excel(checkin_excel_path)
    
    # Filtra solo Desk 31-36
    df_filtered = df_checkin[
        (df_checkin['Desk_Index'] >= 31) & 
        (df_checkin['Desk_Index'] <= 36)
    ].copy()
    
    print(f"Trovate {len(df_filtered)} righe per Desk 31-36")
    print(f"Desk indices: {sorted(df_filtered['Desk_Index'].unique().tolist())}")
    
    # Salva un file temporaneo con solo Desk 31-36
    temp_excel_path = os.path.join('Output', 'CheckIn_Test_Temp.xlsx')
    os.makedirs('Output', exist_ok=True)
    
    # Crea un nuovo Excel con solo le righe filtrate
    # Devo mantenere la stessa struttura del file originale (prime 2 righe vuote)
    with pd.ExcelWriter(temp_excel_path, engine='openpyxl') as writer:
        # Crea un DataFrame vuoto con le stesse colonne
        empty_df = pd.DataFrame(columns=df_checkin.columns)
        # Scrivi 2 righe vuote (come nell'originale)
        empty_df.to_excel(writer, index=False, sheet_name='Sheet1', startrow=0)
        # Poi scrivi i dati filtrati
        df_filtered.to_excel(writer, index=False, sheet_name='Sheet1', startrow=2, header=False)
    
    print(f"Creato file temporaneo: {temp_excel_path}")
    
    # Genera i file
    print("\nGenerazione file CheckIn...")
    try:
        success, message = generate_checkin_files(
            temp_excel_path,
            machine_table_path,
            output_folder,
            'APR001'
        )
        
        if success:
            print(f"\nOK Generazione completata: {message}")
            print(f"\nFile generati in: {output_folder}")
            
            # Elenca i file generati
            if os.path.exists(output_folder):
                files = sorted(os.listdir(output_folder))
                print(f"\nFile generati ({len(files)}):")
                for f in files:
                    print(f"  - {f}")
            
            return True
        else:
            print(f"\n✗ Errore durante la generazione: {message}")
            return False
            
    except Exception as e:
        print(f"\nERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Rimuovi file temporaneo
        if os.path.exists(temp_excel_path):
            os.remove(temp_excel_path)
            print(f"\nRimosso file temporaneo: {temp_excel_path}")

if __name__ == '__main__':
    test_checkin_generation()
