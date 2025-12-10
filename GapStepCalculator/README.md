# Gap Step Calculator

Applicazione Python con interfaccia grafica Qt per calcolare Step e Gap in base a Portata, Velocità Conveyor e Lunghezza Max Bag.

## Installazione

Le dipendenze verranno installate automaticamente all'avvio se non sono già presenti.

In alternativa, puoi installarle manualmente:

```bash
pip install -r requirements.txt
```

## Utilizzo

Esegui l'applicazione con:

```bash
python main.py
```

## Formule

- **Step [m]**: Calcolato come `(Velocità * 3600) / Portata`
  - La portata viene convertita da [1/h] a [1/s] per il calcolo
- **Gap [m]**: Calcolato come `Step - Lunghezza Max Bag`

## Input

- **Portata [1/h]**: Numero di bag all'ora
- **Velocità Conveyor [m/s]**: Velocità del nastro trasportatore in metri al secondo
- **Lunghezza Max Bag [m]**: Lunghezza massima del bag in metri

## Output

- **Step [m]**: Distanza tra i bag
- **Gap [m]**: Spazio tra i bag (Step - Lunghezza Max Bag)


