# Changelog

## Pulizia e Riorganizzazione Progetto

### Struttura
- ✅ Creata struttura cartelle organizzata:
  - `tests/` - Test automatici
  - `tools/` - Script di utilità
  - `docs/` - Documentazione
  - `output/` - File di output temporanei

### File Spostati
- Test spostati in `tests/`:
  - `test_generazione_api004.py`
  - `test_comparison_api004.py`
  - `test_comparison.py`
  
- Tool spostati in `tools/`:
  - `compare_folders.py`
  - `debug_ca_motors.py`
  - `check_io_list.py`
  - `installazione_pacchetti.py`

- Documentazione spostata in `docs/`:
  - `RIASSUNTO_PROMPT.md`
  - `RIEPILOGO_RICHIESTE.md`
  - `STORICO_PROMPT_API004.md`

- File temporanei spostati in `output/`:
  - Tutti i file `.txt` di output/debug/comparison

### Configurazione
- ✅ Aggiornato `.gitignore` con pattern completi
- ✅ Creato `.gitattributes` per gestione line endings
- ✅ Aggiornato `requirements.txt` con PyQt6
- ✅ Creato `README.md` principale con documentazione completa

### Fix Import
- ✅ Aggiornati import nei test per includere path root
- ✅ Aggiornati import nei tool per includere path root
- ✅ Creati `__init__.py` per tests e tools

### Bug Fix
- ✅ Fix estensione FIRESHUTTER: ricerca file `.db` invece di `.scl`
- ✅ Fix AllGatesSafe: uso zona dinamica invece di hardcoded SAFE_ZONE1_DB

### Note
- `interfaccia_grafica.py` (tkinter) è legacy e non più utilizzato
- L'applicazione principale usa `interfaccia_grafica_qt.py` (PyQt6)

