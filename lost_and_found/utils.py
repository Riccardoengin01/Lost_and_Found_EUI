import json
import os
import shutil
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FOTO_DIR = os.path.join(os.path.dirname(__file__), 'foto')

LOST_ITEMS_FILE = os.path.join(DATA_DIR, 'lost_items.json')
ARCHIVE_FILE = os.path.join(DATA_DIR, 'archivio.json')

# Uffici di raccolta presenti al campus
# VS - Villa Schifanoia
# BF - Badia Fiesolana
# BT - Buontalenti
# VF - Villa La Fonte
# LP - Villa Il Poggiolo
UFFICI = ["VS", "BF", "BT", "VF", "LP"]


def _load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _next_id(villa, items):
    prefix = villa
    numbers = [int(item['id'].split('-')[0]) for item in items if item['villa'] == villa]
    next_num = max(numbers) + 1 if numbers else 1
    return f"{next_num:03d}-{prefix}"


def salva_immagine(path_foto):
    if not path_foto:
        return None
    if not os.path.exists(FOTO_DIR):
        os.makedirs(FOTO_DIR, exist_ok=True)
    filename = os.path.basename(path_foto)
    dest_path = os.path.join(FOTO_DIR, filename)
    shutil.copy(path_foto, dest_path)
    return dest_path


def aggiungi_oggetto(villa, data_ritrovamento, ora_ritrovamento,
                     stato_notifica, giorni_scadenza=30, utente=None,
                     foto=None, logo=None):
    items = _load_json(LOST_ITEMS_FILE)
    item_id = _next_id(villa, items)
    scadenza = (datetime.strptime(data_ritrovamento, '%Y-%m-%d') +
                timedelta(days=giorni_scadenza)).strftime('%Y-%m-%d')
    foto_path = salva_immagine(foto) if foto else None
    item = {
        'id': item_id,
        'villa': villa,
        'data_ritrovamento': data_ritrovamento,
        'ora_ritrovamento': ora_ritrovamento,
        'stato_notifica': stato_notifica,
        'data_scadenza': scadenza,
        'utente': utente,
        'ritirato': False,
        'data_ritiro': None,
        'foto': foto_path,
        'logo': logo
    }
    items.append(item)
    _save_json(LOST_ITEMS_FILE, items)
    return item


def ritiro_oggetto(id_oggetto, data_ritiro):
    items = _load_json(LOST_ITEMS_FILE)
    for item in items:
        if item['id'] == id_oggetto:
            item['ritirato'] = True
            item['data_ritiro'] = data_ritiro
            _save_json(LOST_ITEMS_FILE, items)
            return item
    return None


def archivia_scaduti():
    items = _load_json(LOST_ITEMS_FILE)
    archive = _load_json(ARCHIVE_FILE)
    today = datetime.now().date()
    remaining = []
    for item in items:
        scadenza = datetime.strptime(item['data_scadenza'], '%Y-%m-%d').date()
        if not item['ritirato'] and today > scadenza:
            archive.append(item)
        else:
            remaining.append(item)
    _save_json(ARCHIVE_FILE, archive)
    _save_json(LOST_ITEMS_FILE, remaining)
    return len(archive)
