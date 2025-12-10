# Tool Nastri Leonardo - Generatore Configurazioni

Tool per la generazione automatica di file di configurazione SCL/DB per sistemi di nastri trasportatori Leonardo.

## 📋 Indice

- [Descrizione](#descrizione)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Struttura Progetto](#struttura-progetto)
- [Test](#test)
- [Strumenti](#strumenti)

## 📖 Descrizione

Questo tool permette di generare automaticamente file di configurazione per sistemi PLC basati su:
- File Excel di input con la tabella macchine
- Selezione di CAB_PLC e ordine componenti
- Generazione di file `.scl` e `.db` per configurazioni API

## 🔧 Requisiti

- Python 3.8+
- PyQt6 (per interfaccia grafica)
- pandas
- openpyxl

## 📦 Installazione

1. Clona il repository:
```bash
git clone <repository-url>
cd Nastrini-e-Coriandoli
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

Oppure esegui lo script di installazione automatica:
```bash
python installazione_pacchetti.py
```

## 🚀 Utilizzo

### Interfaccia Grafica

Avvia l'applicazione con interfaccia grafica PyQt6:

```bash
python main.py
```

L'interfaccia permette di:
- Selezionare il file Excel di input
- Scegliere il CAB_PLC (es. API004, API002, etc.)
- Impostare l'ordine dei componenti
- Generare automaticamente i file di configurazione

### Utilizzo da Script

```python
from elaborazione_principale import process_excel
from PyQt6.QtCore import QThread

# Configurazione
selected_cab_plc = "API004"
order = ["CP21", "DC11", "CA11", "CA31"]
excel_file_path = "Input/Machine_Table_per_tool_AI.xlsx"

# Esegui elaborazione
status_var = DummyStatusVar()
root = DummyRoot()
success, message = process_excel(selected_cab_plc, status_var, root, order, excel_file_path)
```

## 📁 Struttura Progetto

```
.
├── main.py                      # Entry point principale
├── config.py                    # Gestione configurazioni
├── requirements.txt             # Dipendenze Python
├── README.md                    # Questo file
│
├── elaborazione_principale.py   # Logica principale di elaborazione
├── creazione_file.py            # Generazione file SCL/DB
├── funzioni_elaborazione.py     # Funzioni di supporto
├── interfaccia_grafica_qt.py    # Interfaccia PyQt6
├── io_data.py                   # Gestione dati I/O
│
├── Input/                       # File di input
│   ├── Machine_Table_per_tool_AI.xlsx
│   ├── IO_LIST/
│   └── ...
│
├── Configurazioni/              # Output generati (ignorato da git)
│   └── API004/
│       └── API004/
│
├── tests/                       # Test automatici
│   ├── test_generazione_api004.py
│   ├── test_comparison_api004.py
│   └── test_comparison.py
│
├── tools/                       # Script di utilità
│   ├── compare_folders.py
│   ├── debug_ca_motors.py
│   ├── check_io_list.py
│   └── installazione_pacchetti.py
│
├── docs/                        # Documentazione
│   ├── RIASSUNTO_PROMPT.md
│   ├── RIEPILOGO_RICHIESTE.md
│   └── STORICO_PROMPT_API004.md
│
├── output/                      # File di output temporanei
│
├── Generazione_Allarmi/         # Tool generazione allarmi
├── GapStepCalculator/           # Calcolatore gap step
└── Cursor-Nastrini-Tracking-Logger-Analyzer/  # Logger analyzer
```

## 🧪 Test

Esegui i test di generazione:

```bash
# Test generazione API004
python tests/test_generazione_api004.py

# Test confronto file generati
python tests/test_comparison_api004.py
```

## 🛠️ Strumenti

### Confronto Cartelle
```bash
python tools/compare_folders.py
```

### Debug Motori CA
```bash
python tools/debug_ca_motors.py
```

### Verifica IO List
```bash
python tools/check_io_list.py
```

## 📝 Note

- I file generati vengono salvati in `Configurazioni/<CAB_PLC>/API0##/`
- I file temporanei vengono salvati in `output/`
- La configurazione dell'applicazione viene salvata in `app_config.json` (ignorato da git)

## 🔍 Troubleshooting

### Errore import PyQt6
Assicurati di aver installato PyQt6:
```bash
pip install PyQt6
```

### File Excel non trovato
Verifica che il file Excel sia presente in `Input/` e che il percorso sia corretto.

### Errori di generazione
Controlla i log nella console per dettagli sugli errori. I file di debug vengono salvati in `output/`.

## 📄 Licenza

[Specificare licenza se applicabile]

## 👥 Autori

[Specificare autori se applicabile]

