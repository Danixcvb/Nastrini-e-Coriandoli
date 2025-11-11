import pandas as pd
import os

# Trova il file IO_LIST per API008
io_list_folder = 'Input/IO_LIST'
io_list_file = None

for filename in os.listdir(io_list_folder):
    if filename.endswith('.xlsx') and 'API008' in filename.upper():
        io_list_file = os.path.join(io_list_folder, filename)
        print(f"Trovato file: {filename}")
        break

if not io_list_file:
    print("File IO_LIST per API008 non trovato")
else:
    # Leggi il file
    xls_io = pd.ExcelFile(io_list_file)
    df_io = pd.read_excel(xls_io, sheet_name='IO List', header=None)
    
    print(f"\nFile letto: {io_list_file}")
    print(f"Dimensioni: {len(df_io)} righe\n")
    
    # Colonne: ID LINE COMPONENT è colonna 4, SW TAG è colonna 6
    id_col_idx = 4
    sw_tag_col_idx = 6
    
    print("=" * 100)
    print("RICERCA PULSANTI EB (Emergency Buttons) nel file IO_LIST")
    print("=" * 100)
    print(f"{'Riga':<6} {'ID LINE COMPONENT':<40} {'SW TAG':<60}")
    print("-" * 100)
    
    count = 0
    for idx in range(4, min(300, len(df_io))):  # Dati iniziano dalla riga 4
        pulsante_raw = str(df_io.iloc[idx, id_col_idx]) if pd.notna(df_io.iloc[idx, id_col_idx]) else ""
        sw_tag = str(df_io.iloc[idx, sw_tag_col_idx]) if pd.notna(df_io.iloc[idx, sw_tag_col_idx]) else ""
        
        if pulsante_raw and 'EB' in pulsante_raw and sw_tag and sw_tag != 'nan' and sw_tag.strip():
            # Mostra solo i primi caratteri se troppo lungo
            pulsante_display = pulsante_raw[:38] + ".." if len(pulsante_raw) > 40 else pulsante_raw
            sw_tag_display = sw_tag[:58] + ".." if len(sw_tag) > 60 else sw_tag
            print(f"{idx:<6} {pulsante_display:<40} {sw_tag_display:<60}")
            count += 1
            if count >= 20:  # Mostra i primi 20
                print("\n... (mostrati solo i primi 20)")
                break
    
    print("\n" + "=" * 100)
    print(f"Totale pulsanti trovati: {count}")
    print("=" * 100)

