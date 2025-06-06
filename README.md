# Lost and Found EUI

Semplice sistema per la gestione degli oggetti smarriti con cinque uffici:
VS, BF, BT, VF e LP.

## Funzionalità principali

- Aggiungi un oggetto smarrito specificando il nome del proprietario
- Segna un oggetto come ritirato specificando chi lo ha prelevato
- Archivia automaticamente gli oggetti scaduti in base alla loro data di
  scadenza
- Gli oggetti archiviati per scadenza vengono contrassegnati come
  "smaltiti" per distinguerli da quelli ritirati
- Gestione delle foto
- Script di schedulazione quotidiana per l'archiviazione
- Ricerca e consultazione dell'archivio dalla voce "Archivio"

## Utilizzo

Ogni oggetto viene archiviato automaticamente alla data di scadenza
calcolata al momento dell'inserimento. Normalmente gli oggetti avvisati
scadono dopo **30 giorni**, quelli non avvisati dopo **90**. Il campo
`proprietario` permette di registrare il nominativo associato all'oggetto
ritrovato.

```python
from lost_and_found import utils

# Aggiungi un oggetto
stato = "avvisato"  # oppure "non_avvisato"
utils.aggiungi_oggetto(
    villa="VS",
    data_ritrovamento="2025-01-01",
    ora_ritrovamento="10:00",
    stato_notifica=stato,
    # 30 giorni se avvisato, altrimenti 90
    giorni_scadenza=30 if stato == "avvisato" else 90,
    proprietario="Mario Rossi",
    descrizione="Ombrello nero",
    operatore="Giulia",
    foto="/percorso/alla/foto.jpg"
)

# L'oggetto scadrà automaticamente dopo il numero di giorni indicato
# e verrà spostato nell'archivio al passaggio dello scheduler o con:
# utils.archivia_scaduti()

# Segna ritiro
utils.ritiro_oggetto("001-VS", "2025-01-15", "proprietario")

# Archivia scaduti
utils.archivia_scaduti()
```

Gli oggetti scaduti vengono aggiunti all'archivio con il campo
`smaltito: true` per distinguerli da quelli ritirati.

Per eseguire l'archiviazione giornaliera si può usare `daily_archive.py` con `schedule` o `cron`.

### Interfaccia Streamlit

Per gestire tramite interfaccia web gli oggetti smarriti è possibile avviare:

```bash
streamlit run streamlit_app.py
```

Da qui si possono inserire nuovi oggetti, cercare tra quelli presenti e
archiviare quelli scaduti. Dal menu laterale è ora disponibile anche la
voce **Archivio** per consultare gli oggetti già archiviati e cercarli per
ID, villa o nome del proprietario.


## Installazione

Per installare le dipendenze necessarie, inclusa `tabulate`, utilizzare:

```bash
pip install -r requirements.txt
```
