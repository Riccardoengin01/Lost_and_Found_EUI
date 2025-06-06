diff --git a/README.md b/README.md
index 35be9c8417d41652070aaf6e8021c649203c0c2c..f36ccb3fb45e30ec2bdcd0f3e2a547046fe90a4d 100644
--- a/README.md
+++ b/README.md
@@ -14,50 +14,52 @@ VS, BF, BT, VF e LP.
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
+    descrizione="Ombrello nero",
+    operatore="Giulia",
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
