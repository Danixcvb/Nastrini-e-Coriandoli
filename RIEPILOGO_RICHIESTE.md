# Riepilogo Richieste e Modifiche - Aggiornamento API004

## Richiesta Originale

Aggiornare il sistema di generazione per creare configurazioni API004 che corrispondano esattamente alla struttura di `API004_NEW` (cartella di riferimento).

### Requisiti Chiave

1. **NO backward compatibility** - Aggiornare completamente alla nuova struttura
2. **Generazione automatica** di file CONF_T# e MAIN# mancanti basandosi su dati Excel
3. **Test automatico** dopo ogni generazione per confrontare API004 vs API004_NEW
4. **Struttura API004_NEW** è la fonte di verità

## Modifiche Strutturali Richieste

### Nomenclatura e Riferimenti
- `"DbGlobale"` invece di `"UpstreamDB-Globale"`
- `LINE_1`, `TRUNK1`, `PCT1` invece di `LINE[1]`, `TRUNK[1]`, `PCT[1]`
- `CONVEYOR_1` invece di `CONVEYOR[1]`
- `GenLine.scl` invece di `GEN_LINE.scl`
- `Main.scl` (Organization Block) invece di `MAIN [OB1].scl`
- `"Config PANEL1 ()"` invece di `"Config DbiPanel1 ()"`

### Struttura CONF_T# (Conveyor)
- Aggiunte regioni: `Pht03`, `Pht04`, `PhtTracking03`, `PhtTracking04`
- Nuovi campi: `Pht01TrkEn`, `Pht02TrkEn`, `Pht03TrkEn`, `Pht04TrkEn`, `JamStopReqEn`, `EnableContaminationCheck`, `EnableSecurityStopCheck`, `Conveyor_ID`, `TimeEnergySavingAutotest`, `ContaminationAreaLength`
- `DriveInterface.Par` → `Drive.Par`
- `DriveMaxSpeed` sempre `1.15` (non dalla machine table)
- Valori: `DbObjectsNumber := 1`, `TimeEnergySaving := T#120s`, `Step := 0.0`
- `TrkCtrlTolerance` invece di `TrkCtrlTollerance`
- `SpeedTolerance` invece di `SpeedTolerance`

### Struttura MAIN#
- `VAR_INPUT` con `GlobalData`, `TimeData`, `Constants`
- `VAR_IN_OUT` con `TrunkInterface`
- Uso `#GlobalData`, `#TimeData`, `#Constants`, `#TrunkInterface` invece di riferimenti diretti
- Parametri Conveyor: `SupervisionSa`, `SupervisionCmd`, `ObjectsTable` invece di `PANYTOCNV_SA`, etc.
- `PREV := #GlobalData.EmptyUser` invece di `NULL`
- Formato NEXT: `"Utenza2_CP21ST003" ."Conveyor".Data.OUT` (con spazio prima del punto)

### Main.scl (OB)
- `ORGANIZATION_BLOCK "Main"` invece di `FUNCTION`
- File rinominato da `MAIN [OB1].scl` a `Main.scl`
- Commento copyright presente

### GenLine.scl
- Funzione rinominata da `"GEN_LINE"` a `"GenLine"`
- File rinominato da `GEN_LINE.scl` a `GenLine.scl`
- `LINE_1`, `TRUNK1`, `PCT1` invece di array

### CONF.scl
- `MachineId := 4` invece di `101`
- Rimossi `PROFINET_NODE_BY_SIGNALS` (non presenti nel riferimento)

### Indentazione
- Tutti i file devono usare **tabs** invece di spazi per corrispondere a API004_NEW

## Valori dalla Machine Table

**CORRETTO** (possono differire dagli esempi):
- `Speed1`, `Speed2`, `Acceleration`, `Length` → dalla machine table

**FISSO** (non dalla machine table):
- `DriveMaxSpeed` → sempre `1.15`
- `TimeEnergySaving` → sempre `T#120s`
- `TimeEnergySavingAutotest` → sempre `T#10S`
- `ContaminationAreaLength` → sempre `0.15`

## Test Automatico

- Confronto file-by-file dopo ogni generazione
- Confronta `Configurazioni/API004` vs `Configurazioni/API004_NEW`
- Esegue automaticamente dopo generazione API004
- Nessun report dettagliato, solo esecuzione automatica

## File da Generare Automaticamente

- CONF_T3.scl - CONF_T16.scl (basandosi su CONF_T1.scl e CONF_T2.scl)
- MAIN2.scl - MAIN16.scl (basandosi su MAIN1.scl)
- Tutti i file basati su dati Excel

## File Solo in API004_NEW (da verificare)

- ConfLogger1.scl, ConfLogger2.scl, LoggerConf.scl
- PCE_Output.scl
- PulsLine.scl

## Correzioni Implementate

✅ DriveMaxSpeed sempre 1.15
✅ Main.scl - indentazione corretta
✅ CONF.scl - MachineId=4, indentazione, rimossi PROFINET_NODE_BY_SIGNALS
✅ CONF_T# - indentazione e struttura corretta
✅ MAIN# - formato NEXT corretto, VAR_INPUT/IN_OUT
✅ GenLine.scl - formato corretto
✅ DigOut.scl - formato corretto
✅ DigIn.scl - riga vuota dopo BEGIN corretta
✅ PCE_Input.scl - indentazione e struttura corretta, DbSvProfinetSa
✅ Zones_Input.scl - header FUNCTION aggiunto, indentazione corretta

## Note Finali

- Il codice è stato testato e compila correttamente
- Tutti i moduli si importano senza errori
- La funzione di confronto funziona correttamente
- Le modifiche principali sono state implementate
- Il sistema è pronto per una generazione di test completa

