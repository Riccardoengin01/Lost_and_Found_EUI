import csv
import json
import os
import shutil
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FOTO_DIR = os.path.join(os.path.dirname(__file__), 'foto')

LOST_ITEMS_FILE = os.path.join(DATA_DIR, 'lost_items.json')
ARCHIVE_FILE = os.path.join(DATA_DIR, 'archivio.json')
LOST_ITEMS_CSV = os.path.join(DATA_DIR, 'oggetti_attivi.csv')
ARCHIVE_CSV = os.path.join(DATA_DIR, 'archivio.csv')

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


CSV_FIELDS = [
    'id',
    'villa',
    'data_ritrovamento',
    'ora_ritrovamento',
    'stato_notifica',
    'descrizione',
    'operatore',
    'data_scadenza',
    'proprietario',
    'ritirato',
    'data_ritiro',
    'ritirato_da',
    'smaltito',
    'archiviato',
    'foto',
    'logo',
]


def _load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _save_csv(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in data:
            writer.writerow({k: item.get(k, '') for k in CSV_FIELDS})


def _load_data(json_path, csv_path):
    if os.path.exists(csv_path):
        return _load_csv(csv_path)
    return _load_json(json_path)


def _save_data(json_path, csv_path, data):
    _save_json(json_path, data)
    _save_csv(csv_path, data)


def _next_id(villa, items):
    prefix = villa
    numbers = [int(item['id'].split('-')[0]) for item in items if item['villa'] == villa]
    next_num = max(numbers) + 1 if numbers else 1
    return f"{next_num:03d}-{prefix}"


def salva_immagine(path_foto):
    """Save a provided photo in the local ``FOTO_DIR`` and return its path."""
    if not path_foto:
        return None
    if not os.path.exists(FOTO_DIR):
        os.makedirs(FOTO_DIR, exist_ok=True)
    filename = os.path.basename(path_foto)
    dest_path = os.path.join(FOTO_DIR, filename)
    shutil.copy(path_foto, dest_path)
    return dest_path


def aggiungi_oggetto(
    villa,
    data_ritrovamento,
    ora_ritrovamento,
    stato_notifica,
    giorni_scadenza=30,
    proprietario=None,
    descrizione=None,
    operatore=None,
    foto=None,
    logo=None,
):
    """Create a lost item entry and persist it to disk."""
    items = _load_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV)
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
        'descrizione': descrizione,
        'operatore': operatore,
        'data_scadenza': scadenza,
        'proprietario': proprietario,
        'ritirato': False,
        'data_ritiro': None,
        'ritirato_da': None,
        'smaltito': False,
        'archiviato': False,
        'foto': foto_path,
        'logo': logo
    }
    items.append(item)
    _save_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV, items)
    return item


def ritiro_oggetto(id_oggetto, data_ritiro, ritirato_da):
    """Mark an item as collected and move it to the archive."""
    items = _load_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV)
    archive = _load_data(ARCHIVE_FILE, ARCHIVE_CSV)
    remaining = []
    found_item = None
    for item in items:
        if item['id'] == id_oggetto:
            item['ritirato'] = True
            item['data_ritiro'] = data_ritiro
            item['ritirato_da'] = ritirato_da
            item['archiviato'] = True
            archive.append(item)
            found_item = item
        else:
            remaining.append(item)
    if found_item is None:
        return None
    _save_data(ARCHIVE_FILE, ARCHIVE_CSV, archive)
    _save_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV, remaining)
    return found_item


def archivia_scaduti():
    """Archive all items whose expiry date has passed."""
    items = _load_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV)
    archive = _load_data(ARCHIVE_FILE, ARCHIVE_CSV)
    today = datetime.now().date()
    remaining = []
    newly_archived = 0
    for item in items:
        scadenza = datetime.strptime(item['data_scadenza'], '%Y-%m-%d').date()
        if not item['ritirato'] and today > scadenza:
            item['archiviato'] = True
            item['smaltito'] = True
            archive.append(item)
            newly_archived += 1
        else:
            remaining.append(item)
    _save_data(ARCHIVE_FILE, ARCHIVE_CSV, archive)
    _save_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV, remaining)
    return newly_archived


def archivia_oggetto(id_oggetto):
    """Archive a single item by ID without altering its data."""

    items = _load_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV)
    archive = _load_data(ARCHIVE_FILE, ARCHIVE_CSV)
    remaining = []
    archived_item = None

    for item in items:
        if item["id"] == id_oggetto:
            item["archiviato"] = True
            archive.append(item)
            archived_item = item
        else:
            remaining.append(item)

    if archived_item is None:
        return None

    _save_data(ARCHIVE_FILE, ARCHIVE_CSV, archive)
    _save_data(LOST_ITEMS_FILE, LOST_ITEMS_CSV, remaining)
    return archived_item
