# Lost and Found EUI

Semplice sistema per la gestione degli oggetti smarriti con cinque uffici:
VS, BF, BT, VF e LP.

## Funzionalità principali

- Aggiungi un oggetto smarrito
- Segna un oggetto come ritirato
- Archivia automaticamente gli oggetti scaduti
- Gestione delle foto
- Script di schedulazione quotidiana

## Utilizzo

```python
from lost_and_found import utils

# Aggiungi un oggetto
utils.aggiungi_oggetto(
    villa="VS",
    data_ritrovamento="2025-01-01",
    ora_ritrovamento="10:00",
    stato_notifica="non_avvisato",
    giorni_scadenza=30,
    utente="Mario Rossi",
    foto="/percorso/alla/foto.jpg"
)

# Segna ritiro
utils.ritiro_oggetto("001-VS", "2025-01-15")

# Archivia scaduti
utils.archivia_scaduti()
```

Per eseguire l'archiviazione giornaliera si può usare `daily_archive.py` con `schedule` o `cron`.

### Interfaccia Streamlit

Per gestire tramite interfaccia web gli oggetti smarriti è possibile avviare:

```bash
streamlit run streamlit_app.py
```

Da qui si possono inserire nuovi oggetti, cercare tra quelli presenti e
archiviare quelli scaduti.
