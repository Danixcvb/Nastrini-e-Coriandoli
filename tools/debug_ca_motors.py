"""Script per verificare perché i motori CA non vengono trovati"""

import os
import sys

# Aggiungi la directory root al path per gli import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from funzioni_elaborazione import count_ca_occurrences

# Carica il file Excel
df = pd.read_excel('Input/Matrice_Zone_di_Emergenza_Nizza.xlsx')

# Filtra per API004
cab_data = df[df['CAB_PLC'] == 'API004'].copy()

# Filtra elementi CA11
ca11_data = cab_data[cab_data['ITEM_ID_CUSTOM'].str.startswith('CA11', na=False)].copy()

print("=" * 80)
print("ELEMENTI CA11 TROVATI PER API004")
print("=" * 80)

carousel_main = None
motors = []

for idx, row in ca11_data.iterrows():
    item = str(row['ITEM_ID_CUSTOM']).upper()
    ca_count = count_ca_occurrences(item)
    trunk = row['ITEM_TRUNK']
    prefix = item[:4] if len(item) >= 4 else ""
    
    print(f"{row['ITEM_ID_CUSTOM']}: CA count={ca_count}, Trunk={trunk}, Prefix={prefix}")
    
    # Identifica il carousel principale (quello con 2 occorrenze di CA che viene riconosciuto come Carousel)
    if ca_count == 2:
        # Verifica se questo è il carousel principale (es. CA11CA023)
        # Il carousel principale è quello che viene riconosciuto come "Carousel" nel codice
        if carousel_main is None:
            carousel_main = {
                'item_id': row['ITEM_ID_CUSTOM'],
                'item_id_upper': item,
                'trunk': trunk,
                'prefix': prefix
            }
            print(f"  -> CAROUSEL PRINCIPALE: {row['ITEM_ID_CUSTOM']}")
        else:
            # Altri elementi con 2 occorrenze di CA sono potenziali motori
            if item != carousel_main['item_id_upper']:
                motors.append({
                    'item_id': row['ITEM_ID_CUSTOM'],
                    'item_id_upper': item,
                    'trunk': trunk,
                    'prefix': prefix,
                    'ca_count': ca_count
                })
                print(f"  -> POTENZIALE MOTORE: {row['ITEM_ID_CUSTOM']}")

print("\n" + "=" * 80)
print("RIEPILOGO")
print("=" * 80)
if carousel_main:
    print(f"Carousel principale: {carousel_main['item_id']} (Trunk: {carousel_main['trunk']})")
    print(f"Motori trovati: {len(motors)}")
    for i, motor in enumerate(motors[:5], 1):  # Mostra solo i primi 5
        print(f"  {i}. {motor['item_id']} (Trunk: {motor['trunk']}, CA count: {motor['ca_count']})")
else:
    print("Nessun carousel principale trovato!")

