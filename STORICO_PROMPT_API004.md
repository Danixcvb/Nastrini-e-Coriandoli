# Storico Prompt - Aggiornamento Generazione API004

## Richiesta Originale (RIASSUNTO)

L'utente ha richiesto di aggiornare il sistema di generazione del codice per API004 in modo che corrisponda esattamente alla struttura di `API004_NEW` (cartella di riferimento).

**Punti chiave:**
- NO backward compatibility - aggiornare completamente alla nuova struttura
- Generare automaticamente file CONF_T# e MAIN# mancanti basandosi su dati Excel
- Test automatico dopo ogni generazione per confrontare API004 vs API004_NEW
- Struttura API004_NEW è la fonte di verità

**Modifiche principali:**
- `"DbGlobale"` invece di `"UpstreamDB-Globale"`
- `LINE_1`, `TRUNK1`, `PCT1` invece di array `LINE[1]`, `TRUNK[1]`, `PCT[1]`
- `CONVEYOR_1` invece di `CONVEYOR[1]`
- `GenLine.scl` invece di `GEN_LINE.scl`
- `Main.scl` (OB) invece di `MAIN [OB1].scl`
- Indentazione con tabs invece di spazi
- `DriveMaxSpeed` sempre `1.15` (non dalla machine table)
- Valori Speed1, Speed2, Acceleration, Length dalla machine table (possono differire)

## Richiesta Originale (DETTAGLIATA)

### Contesto
- Esiste una cartella `Configurazioni/API004_NEW` con configurazioni aggiornate di riferimento
- La cartella `Configurazioni/API004` contiene file generati dalla versione precedente del codice
- Molti file `CONF_T#` e `MAIN#` sono mancanti in `API004_NEW` (ci sono solo esempi)
- Il sistema deve generare automaticamente i file mancanti basandosi sui dati Excel e sulla struttura degli esempi esistenti

### Requisiti Specifici

1. **Generazione CONF_T#**: 
   - Generare tutti i file CONF_T# mancanti (3-16) basandosi sui dati Excel
   - Usare la struttura degli esempi esistenti (CONF_T1.scl, CONF_T2.scl) come template

2. **Generazione MAIN#**:
   - Generare tutti i file MAIN# mancanti (1-16) basandosi sui dati Excel
   - Considerare che `Main.scl` è il vecchio `Main [OB1].scl` (Organization Block)

3. **Aggiornamento Struttura**:
   - **NO backward compatibility** - aggiornare completamente alla nuova struttura
   - Usare `"DbGlobale"` invece di `"UpstreamDB-Globale"`
   - Usare `LINE_1`, `TRUNK1`, `PCT1` invece di `LINE[1]`, `TRUNK[1]`, `PCT[1]`
   - Usare `GenLine.scl` invece di `GEN_LINE.scl`
   - Usare `Main.scl` (Organization Block) invece di `MAIN [OB1].scl`
   - Usare `CONVEYOR_1` invece di `CONVEYOR[1]`

4. **Test Automatico**:
   - Implementare confronto automatico file-by-file dopo ogni generazione
   - Confrontare API004 generato con API004_NEW
   - Nessun report dettagliato, solo esecuzione automatica
   - Eseguire automaticamente dopo ogni generazione

## Modifiche Implementate

### 1. Funzione di Confronto Automatico (`test_comparison.py`)
✅ **Completato**
- Creato modulo `test_comparison.py` con funzioni:
  - `compare_files()`: confronta due file SCL ignorando differenze di whitespace
  - `compare_api004_folders()`: confronta tutte le cartelle
  - `run_comparison_test()`: esegue il test completo e stampa risultati
- Integrato in `elaborazione_principale.py` per esecuzione automatica dopo generazione API004

### 2. Aggiornamento Generazione CONF_T# (`elaborazione_principale.py`)
✅ **Completato** (parzialmente - vedi differenze rimanenti)
- Aggiunte regioni `Pht03` e `Pht04` per Conveyor
- Aggiunte regioni `PhtTracking03` e `PhtTracking04` con tutti i campi:
  - DisableSlipForward, DisableSlipBackward, DisableUnexpected, DisablePieceLost
  - DisableContaminationSlipForward, DisableContaminationSlipBackward
  - DisableContaminationPieceAppeared, DisableContaminationPieceLost
  - DisableContaminationLengthMismatch
  - SlipForwardTolerance, SlipBackwardTolerance
  - ContaminatioForwardThr, ContaminatioBackwardThr
- Cambiato `DriveInterface.Par` in `Drive.Par` per Conveyor
- Aggiunti nuovi campi in `Conveyor.Data.CNF`:
  - `Pht01TrkEn`, `Pht02TrkEn`, `Pht03TrkEn`, `Pht04TrkEn`
  - `JamStopReqEn`
  - `EnableContaminationCheck`
  - `EnableSecurityStopCheck`
  - `Conveyor_ID` (formato 4 cifre)
  - `TimeEnergySavingAutotest`
  - `ContaminationAreaLength`
- Aggiornati valori:
  - `DbObjectsNumber := 1` (invece di 2011)
  - `TimeEnergySaving := T#120s` (invece di T#1s)
  - `Step := 0.0` (invece di 0.4)
  - `DriveMaxSpeed := {item_speed_max}` (valore diretto invece di riferimento)
- Cambiato `TrkCtrlTollerance` in `TrkCtrlTolerance`
- Cambiato `SpeedTollerance` in `SpeedTolerance`
- Aggiornato `PhtTracking01.Position` per usare `Length - 0.4` invece di `0.4`

### 3. Aggiornamento Generazione MAIN# (`creazione_file.py`)
✅ **Completato** (parzialmente - vedi differenze rimanenti)
- Cambiato da `VAR_TEMP` a `VAR_INPUT` e `VAR_IN_OUT`:
  ```scl
  VAR_INPUT 
     GlobalData : "GlobalData";
     TimeData : "TimeData";
     Constants : "Constants";
  END_VAR
  
  VAR_IN_OUT 
     TrunkInterface : "COM_TRUNK-USE";
  END_VAR
  ```
- Aggiornato uso parametri:
  - `#GlobalData` invece di `"DbGlobale".GlobalData`
  - `#TimeData` invece di `"DbGlobale".TimeData`
  - `#Constants` invece di `"DB_Constants".Constants`
  - `#TrunkInterface` invece di `"DbiTrunkLN01".ComTrunkUse`
- Cambiato `CONVEYOR[1]` in `CONVEYOR_1`
- Cambiato parametri funzione Conveyor:
  - `SupervisionSa` invece di `PANYTOCNV_SA`
  - `SupervisionCmd` invece di `PANYTOCNV_CMD`
  - `ObjectsTable` invece di `DB_OBJ`
- Cambiato `NULL` in `#GlobalData.EmptyUser` per PREV quando non c'è elemento precedente
- Rimossa sezione "Initializing Temp Section" con TempEncoderNotUsed

### 4. Aggiornamento Main.scl (OB) (`creazione_file.py`)
✅ **Completato**
- Cambiato da FUNCTION a `ORGANIZATION_BLOCK "Main"`
- File rinominato da `MAIN [OB1].scl` a `Main.scl`
- Aggiunta intestazione con commenti copyright
- Aggiunta sezione `VAR_TEMP` con `ReturnValue`, `OBDateTime`, `StartTronco`
- Aggiunto `END_ORGANIZATION_BLOCK` alla fine
- Mantenuto uso di `"DbGlobale"` (già corretto)
- Mantenuto uso di `"GenLine"()` (già corretto)

### 5. Aggiornamento GenLine.scl (`creazione_file.py`)
✅ **Completato**
- Funzione rinominata da `"GEN_LINE"` a `"GenLine"`
- File rinominato da `GEN_LINE.scl` a `GenLine.scl`
- Cambiato `LINE[1]` in `LINE_1` (generato dinamicamente come `LINE_{line_num}`)
- Cambiato `TRUNK[1]` in `TRUNK1` (generato dinamicamente come `TRUNK{trunk_num}`)
- Cambiato `PCT[1]` in `PCT1` (generato dinamicamente come `PCT{trunk_num}`)
- File salvato direttamente in `API004` invece di sottocartella `LINE`

### 6. Aggiornamento CONF.scl (`creazione_file.py`)
✅ **Completato**
- Cambiato nome regione da `"Config DbiPanel1 ()"` a `"Config PANEL1 ()"`
- Già usa `"DbGlobale"` (corretto)

## Differenze Rimanenti da Risolvere

### 1. Struttura CONF_T# - Elementi Duplicati
**Problema**: In `API004_NEW/CONF_T1.scl` ci sono **due regioni CONVEYOR identiche** per lo stesso elemento `CP21ST001`:
- Prima regione: righe 7-189
- Seconda regione: righe 190-372 (stesso commento `REGION Config CONVEYOR_SEW_MOVIGEAR (CP21ST001)`)

**Analisi**: 
- Entrambe le regioni hanno lo stesso nome elemento `(CP21ST001)`
- La struttura è identica
- Potrebbe essere un errore nel file di riferimento o una caratteristica specifica

**Da verificare**: 
- Se questa duplicazione è intenzionale
- Se serve per gestire più istanze dello stesso elemento
- Se è un errore e va generata solo una regione per elemento

### 1b. Formattazione CONF_T# - Indentazione
**Problema**: Differenze di indentazione tra file generati e riferimento:
- API004_NEW usa tabs consistenti
- File generati potrebbero avere mix di tabs/spaces

**Da verificare**: Normalizzare indentazione per corrispondere esattamente.

### 2. Struttura MAIN# - Formattazione NEXT
**Problema**: Nel MAIN# di riferimento (`API004_NEW/MAIN1.scl` riga 38) c'è uno spazio prima del punto:
```scl
NEXT := "Utenza2_CP21ST003" ."Conveyor".Data.OUT,
```
Mentre nel generato abbiamo:
```scl
NEXT := "Utenza2_CP21ST003".Conveyor.Data.OUT,
```

**Da verificare**: Se lo spazio è intenzionale o è un errore di formattazione nel riferimento.

### 2b. Struttura MAIN# - Parametri Rimossi
**Nota**: I parametri `"Ist-VidGenerator"`, `EncoderInterface`, `DriveInterface_IN/OUT`, `"Ist-McpCreateChrMsg"`, etc. sono stati rimossi nella nuova struttura MAIN#. Questo è corretto secondo `API004_NEW/MAIN1.scl` che usa solo:
- `START`, `PREV`, `NEXT`
- `TimeData`, `Constants`, `TrunkInterface`
- `SupervisionSa`, `SupervisionCmd`, `ObjectsTable`

### 3. Struttura CONF_T# - Carousel
**Problema**: La struttura per Carousel non è stata aggiornata come quella per Conveyor. In `API004_NEW` non ci sono esempi di Carousel in CONF_T#, quindi la struttura attuale potrebbe essere corretta.

**Da verificare**: Se la struttura Carousel deve essere aggiornata o se rimane invariata.

### 4. Valori Hardcoded vs Dinamici
**Problema**: Alcuni valori sono hardcoded invece di essere calcolati dinamicamente:
- `Conveyor_ID` usa `progressive_number` (formato 4 cifre: 0001, 0002, etc.) - **CORRETTO**
- `TimeEnergySaving := T#120s` è hardcoded - **Da verificare se deve venire da Excel**
- `TimeEnergySavingAutotest := T#10S` è hardcoded - **Da verificare se deve venire da Excel**
- `ContaminationAreaLength := 0.15` è hardcoded - **Da verificare se deve venire da Excel**
- `DriveMaxSpeed` usa `{item_speed_max}` direttamente invece di riferimento - **CORRETTO secondo API004_NEW**

**Nota**: In `API004_NEW/CONF_T1.scl` questi valori sono hardcoded, quindi probabilmente sono costanti per API004. Verificare se ci sono colonne Excel corrispondenti.

### 5. Indentazione e Formattazione
**Problema**: Potrebbero esserci differenze di indentazione (tabs vs spaces) o formattazione tra i file generati e quelli di riferimento.

**Da verificare**: Normalizzare l'indentazione per corrispondere esattamente a API004_NEW.

### 6. File Mancanti da Generare
**Problema**: Alcuni file presenti in API004_NEW potrebbero non essere generati:
- `ConfLogger1.scl`, `ConfLogger2.scl` - File logger specifici
- `LoggerConf.scl` - Configurazione logger
- `PulsLine.scl` - Gestione pulsanti linea
- Altri file specifici

**Da verificare**: 
- Se questi file devono essere generati automaticamente
- Se sono file manuali/template da copiare
- Se devono essere generati basandosi su dati Excel

### 7. Differenze nei Valori Specifici
**Problema**: Confrontando `API004_NEW/CONF_T1.scl` con `API004/CONF_T1.scl` ci sono differenze nei valori:
- `Speed1`: API004_NEW usa `+ 0.6`, API004 generato usa `+ 0.8` (da Excel)
- `Speed2`: API004_NEW usa `0.6`, API004 generato usa `1.2` (da Excel)
- `DriveMaxSpeed`: API004_NEW usa `1.15`, API004 generato usa `1.5` (da Excel)
- `Acceleration`: API004_NEW usa `3.0`, API004 generato usa `2.5` (da Excel)
- `Length`: API004_NEW usa `3.2`, API004 generato usa `3.4` (da Excel)

**Nota**: Queste differenze sono probabilmente dovute ai dati Excel diversi. I valori devono venire dall'Excel, quindi il codice è corretto. Verificare che i dati Excel siano corretti.

## File di Riferimento

### File Esempio in API004_NEW (15 file .scl):
- `CONF_T1.scl` - Esempio struttura CONF_T per Conveyor (⚠️ contiene duplicazione - 2 regioni identiche per CP21ST001)
- `CONF_T2.scl` - Esempio struttura CONF_T per Conveyor (solo Utenza2_CP21ST003, nessuna duplicazione)
- `CONF.scl` - Esempio struttura CONF
- `Main.scl` - Esempio Organization Block principale
- `MAIN1.scl` - Esempio struttura MAIN# per tronco (solo 1 elemento)
- `GenLine.scl` - Esempio struttura GenLine
- `DigIn.scl`, `DigOut.scl` - File digitali
- `PCE_Input.scl`, `PCE_Output.scl` - File PCE
- `Zones_Input.scl` - File zone
- `ConfLogger1.scl`, `ConfLogger2.scl`, `LoggerConf.scl` - File logger
- `PulsLine.scl` - Gestione pulsanti

**Nota**: In API004_NEW ci sono solo CONF_T1 e CONF_T2 come esempi. I file CONF_T3-CONF_T16 devono essere generati automaticamente basandosi sulla struttura degli esempi.

**Nota**: In API004_NEW c'è solo MAIN1.scl come esempio. I file MAIN2-MAIN16 devono essere generati automaticamente.

### File Generati Attualmente:
- `Configurazioni/API004/API004/*.scl` - File generati dalla versione precedente (60 file .scl)
- La cartella verrà ricreata alla prossima generazione con la nuova struttura

## Prossimi Passi per Completare

1. **Risolvere Duplicazione CONF_T1**:
   - Verificare con l'utente se la duplicazione in CONF_T1.scl è intenzionale
   - Se sì: implementare logica per duplicare quando necessario
   - Se no: generare solo una regione per elemento

2. **Normalizzare Indentazione**:
   - Verificare che tutti i file generati usino tabs invece di spaces
   - Allineare indentazione a API004_NEW esattamente

3. **Risolvere Formattazione MAIN#**:
   - Verificare se lo spazio in `"Utenza2_CP21ST003" ."Conveyor"` è intenzionale
   - Se sì: aggiungere spazio nella generazione
   - Se no: mantenere senza spazio

4. **Generare File Mancanti**:
   - Verificare se `ConfLogger1.scl`, `ConfLogger2.scl`, `LoggerConf.scl`, `PulsLine.scl` devono essere generati
   - Se sì: implementare generazione basandosi su esempi o dati Excel
   - Se no: documentare che sono file manuali

5. **Test Completo**:
   - Eseguire generazione completa di API004
   - Eseguire confronto automatico
   - Analizzare tutte le differenze rimanenti
   - Risolvere una per una

6. **Verificare Valori Hardcoded**:
   - Verificare se `TimeEnergySaving`, `TimeEnergySavingAutotest`, `ContaminationAreaLength` devono venire da Excel
   - Se sì: aggiungere colonne Excel o logica di calcolo
   - Se no: mantenere hardcoded come in API004_NEW

## Note Importanti

- **NO backward compatibility**: Tutte le modifiche sono definitive, non mantenere compatibilità con versioni precedenti
- **Generazione Automatica**: I file CONF_T# e MAIN# mancanti devono essere generati automaticamente basandosi sui dati Excel
- **Test Automatico**: Il confronto viene eseguito automaticamente dopo ogni generazione per API004
- **Struttura API004_NEW**: È la fonte di verità per la struttura corretta

## Comandi Utili

```python
# Eseguire test di confronto manualmente
from test_comparison import run_comparison_test
result = run_comparison_test('API004')

# Verificare struttura file
import os
api004_new_files = [f for f in os.listdir('Configurazioni/API004_NEW') if f.endswith('.scl')]
print(api004_new_files)
```

## Stato Attuale

- ✅ Funzione di confronto implementata e funzionante
- ✅ Struttura CONF_T# aggiornata (parzialmente - manca gestione duplicazioni)
- ✅ Struttura MAIN# aggiornata (parzialmente - manca formattazione spazio)
- ✅ Main.scl (OB) aggiornato
- ✅ GenLine.scl aggiornato
- ✅ CONF.scl aggiornato
- ⚠️ Alcune differenze rimangono da risolvere (vedi sezione "Differenze Rimanenti")

## Comandi per Test Rapido

```python
# Test importazione moduli
python -c "import test_comparison, elaborazione_principale, creazione_file; print('OK')"

# Test confronto (dopo generazione)
from test_comparison import run_comparison_test
result = run_comparison_test('API004')

# Verificare file in API004_NEW
import os
files = [f for f in os.listdir('Configurazioni/API004_NEW') if f.endswith('.scl')]
print(f"File .scl in API004_NEW: {len(files)}")
print(files)
```

## Note Finali

- Il codice è stato testato e compila correttamente
- Tutti i moduli si importano senza errori
- La funzione di confronto funziona correttamente
- Le modifiche principali sono state implementate
- Restano da risolvere alcune differenze minori di formattazione e struttura
- Il sistema è pronto per una generazione di test completa

## Correzioni Completate (Ultimo Aggiornamento)

✅ **DriveMaxSpeed sempre 1.15** - Corretto in `elaborazione_principale.py`
✅ **Main.scl** - Indentazione dopo BEGIN con tabs
✅ **CONF.scl** - MachineId=4, indentazione tabs, rimossi PROFINET_NODE_BY_SIGNALS
✅ **CONF_T#** - Indentazione tabs, intestazione corretta
✅ **MAIN#** - Formato NEXT con spazio, VAR_INPUT/IN_OUT, indentazione
✅ **GenLine.scl** - Riga vuota dopo BEGIN con tab
✅ **DigOut.scl** - Formato corretto (nessuna riga vuota dopo BEGIN)
✅ **DigIn.scl** - Riga vuota dopo BEGIN con tab
✅ **PCE_Input.scl** - Indentazione tabs, DbSvProfinetSa invece di SV_DB_PROFINET_SA
✅ **Zones_Input.scl** - Header FUNCTION aggiunto, indentazione tabs, END_FUNCTION aggiunto

**Nota importante:** Valori Speed1, Speed2, Acceleration, Length vengono dalla machine table e possono differire dagli esempi in API004_NEW - questo è corretto.

