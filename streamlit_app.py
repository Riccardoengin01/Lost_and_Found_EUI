import os
import json
from datetime import datetime, date
import streamlit as st
from lost_and_found import utils

st.title("Lost & Found - EUI")

menu = st.sidebar.radio(
    "Seleziona sezione",
    ("Aggiungi oggetto", "Lista oggetti")
)

if menu == "Aggiungi oggetto":
    st.header("Aggiungi un nuovo oggetto")
    with st.form("add_item"):
        villa = st.selectbox("Ufficio di raccolta", utils.UFFICI)
        data_r = st.date_input("Data di ritrovamento", value=date.today())
        ora_r = st.time_input("Ora di ritrovamento", value=datetime.now().time())
        stato = st.selectbox("Stato notifica", ["non_avvisato", "avvisato"])
        giorni = st.number_input("Giorni alla scadenza", min_value=1, max_value=365, value=30)
        utente = st.text_input("Utente")
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
            item = utils.aggiungi_oggetto(
                villa=villa,
                data_ritrovamento=data_r.strftime("%Y-%m-%d"),
                ora_ritrovamento=ora_r.strftime("%H:%M"),
                stato_notifica=stato,
                giorni_scadenza=int(giorni),
                utente=utente,
                foto=foto_path,
            )
            st.success(f"Oggetto aggiunto con ID {item['id']}")

else:
    st.header("Oggetti presenti")
    query = st.text_input("Cerca per ID, villa o utente")
    try:
        with open(utils.LOST_ITEMS_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        items = []
    if query:
        q = query.lower()
        items = [i for i in items if q in i["id"].lower() or q in i["villa"].lower() or (i.get("utente") and q in i["utente"].lower())]
    if items:
        st.dataframe(items)
    else:
        st.write("Nessun oggetto trovato")

    st.subheader("Segna ritiro")
    with st.form("ritiro"):
        id_ritiro = st.text_input("ID oggetto")
        data_r = st.date_input("Data ritiro", value=date.today())
        submit_r = st.form_submit_button("Ritira")
        if submit_r and id_ritiro:
            item = utils.ritiro_oggetto(id_ritiro, data_r.strftime("%Y-%m-%d"))
            if item:
                st.success("Oggetto ritirato")
            else:
                st.error("ID non trovato")

    if st.button("Archivia oggetti scaduti"):
        n = utils.archivia_scaduti()
        st.write(f"Oggetti archiviati: {n}")
