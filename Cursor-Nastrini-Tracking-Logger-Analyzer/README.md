# Nastrini Tracking Logger Analyzer

Tool Python con interfaccia Qt per analizzare dati da database SQLite contenenti log di tracking dei nastri trasportatori.

## Caratteristiche

- **Interfaccia grafica Qt**: Interfaccia moderna e intuitiva
- **Struttura gerarchica**: Visualizzazione dati organizzata per NodeId → ConveyorID → PhotocellID
- **Analisi statistiche**: Calcolo di medie, massimi e minimi per Offset, DimX e DimY
- **SlotLength**: Opzione per moltiplicare i valori Offset per una lunghezza slot personalizzata
- **Gestione automatica file**: Ricorda l'ultimo file aperto e carica automaticamente `log01.sqlite` se disponibile
- **Installazione automatica dipendenze**: Installa automaticamente PyQt5 se non presente

## Requisiti

- Python 3.6 o superiore
- PyQt5 (installato automaticamente se mancante)

## Utilizzo

Eseguire l'applicazione:

```bash
python main.py
```

### Funzionalità

1. **Selezione Database**: 
   - Cliccare su "Sfoglia..." per selezionare un file `.sqlite`
   - L'applicazione carica automaticamente l'ultimo file aperto
   - Se non disponibile, carica `log01.sqlite` se presente nella directory corrente

2. **Visualizzazione Dati**:
   - La tabella mostra una struttura gerarchica espandibile:
     - **NodeId**: PLC di riferimento
     - **ConveyorID**: Nastri trasportatori
     - **PhotocellID**: Fotocellule installate
   
3. **Statistiche Visualizzate** (solo per EventType = 1):
   - **Offset**: Media dei valori OffsetCtrl
   - **MaxOffset+**: Valore massimo di Offset
   - **MaxOffset-**: Valore minimo di Offset
   - **DimX**: Media delle dimensioni X (in cm)
   - **DimY**: Media delle dimensioni Y (in cm)

4. **SlotLength**:
   - Inserire un valore in cm nel campo "SlotLength"
   - Abilitare la checkbox "Abilita" per moltiplicare tutti i valori Offset per questo fattore
   - I valori vengono aggiornati automaticamente

## Struttura Database

L'applicazione si aspetta un database SQLite con:
- Tabella `Logs` contenente `MsgId`, `TimeStamp`, `NodeId`
- Tabella `Msg00101` (o simile) con i dati del messaggio 101
- Campi rilevanti: `ConveyorID`, `PhotocellID`, `EventType`, `OffsetCtrl`, `DIM_X`, `DIM_Y`

La struttura del messaggio 101 è definita nel file `logger.conf`.

## Note

- I dati vengono filtrati per `MsgId = 101` e `EventType = 1`
- Le dimensioni DimX e DimY sono già in centimetri nel database
- Il file `last_file.json` viene creato automaticamente per ricordare l'ultimo file aperto

