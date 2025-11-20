# Riassunto Prompt Principali

## Obiettivo Generale
Aggiornare la generazione di codice SCL per creare configurazioni `API004` che corrispondano alla struttura di `API004_NEW`, senza backward compatibility.

## Richieste Principali

### 1. Struttura File e Naming
- **CONF_T#**: Generare file `CONF_T1.scl`, `CONF_T2.scl`, ecc. seguendo la struttura di `API004_NEW`
- **MAIN#**: Generare file `MAIN1.scl`, `MAIN2.scl`, ecc. (non più `MAIN [OB1].scl`)
- **Main.scl**: File principale come `ORGANIZATION_BLOCK "Main"` invece di `FUNCTION`
- **GenLine.scl**: Nome file e riferimenti aggiornati (non più `GEN_LINE.scl`)
- **CONF.scl**: Regione rinominata da `Config DbiPanel1 ()` a `Config PANEL1 ()`

### 2. Caroselli (Carousel)
- **Tronco Carousel**: Quando un tronco contiene un carosello (identificato da "CA CA"), il tronco deve essere chiamato "Carousel" invece di un numero
  - File generati: `MAINCarousel.scl`, `CONF_TCarousel.scl`, `DbiTrunkLNCarousel.scl`
  - Se il tronco Carousel non è l'ultimo, i tronchi successivi devono essere scalati di 1 per mantenere numerazione contigua
- **Linea Carousel**: Per linee contenenti caroselli, usare `DbiLineCarousel` invece di `DbiLine#`
- **Riferimenti**: Tutti i riferimenti devono usare "Carousel" invece di un numero quando applicabile

### 3. Struttura MAIN#
- **VAR_INPUT/VAR_IN_OUT**: Usare `VAR_INPUT` per `GlobalData`, `TimeData`, `Constants` e `VAR_IN_OUT` per `TrunkInterface`
- **Riferimenti GlobalData**: Usare `#GlobalData` invece di `"DbGlobale".GlobalData`
- **PREV/NEXT**: 
  - Rimuovere spazio extra prima del punto (es. `"Utenza39_CA31ST015"."Conveyor"` invece di `"Utenza39_CA31ST015" ."Conveyor"`)
  - Se `PREV` o `NEXT` appartiene a una linea diversa, il valore deve essere `NULL`
  - Se non c'è `PREV`, usare `#GlobalData.EmptyUser` invece di `NULL`
- **PANYTOCNV_SA/CMD**: Usare `CONVEYOR_X` invece di `CONVEYOR[X]`

### 4. Valori da Machine Table
- **Speed1, Speed2, Acceleration, Length**: Leggere dalla machine table (Excel), anche se diversi da `API004_NEW`
- **DriveMaxSpeed**: Sempre `1.15` (hardcoded)

### 5. DigIn.scl
- **IN.PFL**: La riga di default deve essere commentata:
  ```scl
  //"Utenza1_CP21ST001".Conveyor.Data.IN.PFL := "PFL_NCE1".DATA.OUT.PFL_Req;
  ```

### 6. Test Automatico
- Confronto automatico file-by-file tra `API004` generato e `API004_NEW` dopo ogni generazione
- Nessun report dettagliato, solo esecuzione automatica
- Normalizzazione whitespace e commenti per confronto

### 7. Formattazione
- Indentazione con tab
- Righe vuote dopo `BEGIN` dove necessario
- Rimozione righe vuote extra dove non necessarie
- Encoding `utf-8-sig` per gestire BOM

## Note Tecniche
- Nessuna backward compatibility richiesta
- Generazione basata su Excel (`Machine_Table_per_tool_AI.xlsx`)
- Struttura deve corrispondere esattamente a `API004_NEW` dove possibile
- Valori dalla machine table hanno priorità sugli esempi di `API004_NEW` (tranne `DriveMaxSpeed`)

