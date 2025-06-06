import os
import json
from datetime import datetime, date
import pandas as pd
import streamlit as st
from lost_and_found import utils

st.title("Lost & Found - EUI")

menu = st.sidebar.radio(
    "Seleziona sezione",
    ("Aggiungi oggetto", "Lista oggetti", "Archivio")
)

if menu == "Aggiungi oggetto":
    st.header("Aggiungi un nuovo oggetto")
    with st.form("add_item"):
        villa = st.selectbox("Ufficio di raccolta", utils.UFFICI)
        data_r = st.date_input("Data di ritrovamento", value=date.today())
        ora_r = st.time_input("Ora di ritrovamento", value=datetime.now().time())
        stato = st.selectbox("Stato notifica", ["non_avvisato", "avvisato"])
        proprietario = st.text_input("Proprietario (nome e cognome)")
        foto = st.file_uploader("Foto", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Salva")
        if submit:
            foto_path = None
            if foto is not None:
                upload_dir = os.path.join("uploads")
                os.makedirs(upload_dir, exist_ok=True)
                foto_path = os.path.join(upload_dir, foto.name)
                with open(foto_path, "wb") as f:
                    f.write(foto.read())
            giorni_scadenza = 30 if stato == "avvisato" else 90
            item = utils.aggiungi_oggetto(
                villa=villa,
                data_ritrovamento=data_r.strftime("%Y-%m-%d"),
                ora_ritrovamento=ora_r.strftime("%H:%M"),
                stato_notifica=stato,
                giorni_scadenza=giorni_scadenza,
                proprietario=proprietario,
                foto=foto_path,
            )
            st.success(f"Oggetto aggiunto con ID {item['id']}")

elif menu == "Lista oggetti":
    st.header("Oggetti presenti")
    query = st.text_input("Cerca per ID, villa o proprietario")
    try:
        with open(utils.LOST_ITEMS_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        items = []
    if query:
        q = query.lower()
        items = [i for i in items if q in i["id"].lower() or q in i["villa"].lower() or (i.get("proprietario") and q in i["proprietario"].lower())]
    if items:
        df = pd.DataFrame([
            {
                "ID": i["id"],
                "villa": i["villa"],
                "data/ora ritrovamento": f"{i['data_ritrovamento']} {i['ora_ritrovamento']}",
                "stato_notifica": i["stato_notifica"],
                "proprietario": i.get("proprietario"),
                "ritirato": i.get("ritirato"),
                "archiviato": i.get("archiviato"),
                "foto": f"[link]({i['foto']})" if i.get("foto") else "",
            }
            for i in items
        ])
        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.write("Nessun oggetto trovato")

    st.subheader("Segna ritiro")
    with st.form("ritiro"):
        id_ritiro = st.text_input("ID oggetto")
        data_r = st.date_input("Data ritiro", value=date.today())
        ritirato_da = st.selectbox("Ritirato da", ["proprietario", "delegato"])
        submit_r = st.form_submit_button("Ritira")
        if submit_r and id_ritiro:
            item = utils.ritiro_oggetto(
                id_ritiro,
                data_r.strftime("%Y-%m-%d"),
                ritirato_da,
            )
            if item:
                st.success("Oggetto ritirato")
            else:
                st.error("ID non trovato")

    if st.button("Archivia oggetti scaduti"):
        n = utils.archivia_scaduti()
        st.write(f"Oggetti archiviati: {n}")

else:
    st.header("Archivio")
    query = st.text_input("Cerca per ID, villa o proprietario", key="archivio_query")
    try:
        with open(utils.ARCHIVE_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        items = []
    if query:
        q = query.lower()
        items = [i for i in items if q in i["id"].lower() or q in i["villa"].lower() or (i.get("proprietario") and q in i["proprietario"].lower())]
    if items:
        df = pd.DataFrame([
            {
                "ID": i["id"],
                "villa": i["villa"],
                "data/ora ritrovamento": f"{i['data_ritrovamento']} {i['ora_ritrovamento']}",
                "stato_notifica": i["stato_notifica"],
                "proprietario": i.get("proprietario"),
                "ritirato": i.get("ritirato"),
                "archiviato": i.get("archiviato"),
                "foto": f"[link]({i['foto']})" if i.get("foto") else "",
            }
            for i in items
        ])
        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.write("Nessun oggetto archiviato trovato")
