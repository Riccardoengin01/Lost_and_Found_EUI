import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from datetime import datetime, timedelta

import pytest

from lost_and_found import utils


def setup_temp_env(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    foto_dir = tmp_path / "foto"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(foto_dir, exist_ok=True)
    # Avoid salvataggio CSV per non alterare i tipi
    monkeypatch.setattr(utils, "_save_csv", lambda *a, **k: None)
    monkeypatch.setattr(utils, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(utils, "FOTO_DIR", str(foto_dir))
    monkeypatch.setattr(utils, "LOST_ITEMS_FILE", str(data_dir / "lost_items.json"))
    monkeypatch.setattr(utils, "ARCHIVE_FILE", str(data_dir / "archivio.json"))
    monkeypatch.setattr(utils, "LOST_ITEMS_CSV", str(data_dir / "oggetti_attivi.csv"))
    monkeypatch.setattr(utils, "ARCHIVE_CSV", str(data_dir / "archivio.csv"))
    return data_dir, foto_dir


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_aggiungi_oggetto(tmp_path, monkeypatch):
    data_dir, _ = setup_temp_env(tmp_path, monkeypatch)

    item = utils.aggiungi_oggetto(
        villa="VS",
        data_ritrovamento="2025-01-01",
        ora_ritrovamento="10:00",
        stato_notifica="avvisato",
        giorni_scadenza=30,
        proprietario="Mario",
        descrizione="Ombrello",
        operatore="Giulia",
    )

    assert item["id"] == "001-VS"
    assert item["data_scadenza"] == "2025-01-31"

    saved = load_json(os.path.join(data_dir, "lost_items.json"))
    assert len(saved) == 1
    assert saved[0]["descrizione"] == "Ombrello"


def test_ritiro_oggetto(tmp_path, monkeypatch):
    data_dir, _ = setup_temp_env(tmp_path, monkeypatch)

    item = utils.aggiungi_oggetto(
        villa="VS",
        data_ritrovamento="2025-01-01",
        ora_ritrovamento="10:00",
        stato_notifica="avvisato",
        giorni_scadenza=30,
    )

    result = utils.ritiro_oggetto(item["id"], "2025-01-15", "Mario")

    assert result is not None
    assert result["ritirato"] is True
    assert result["data_ritiro"] == "2025-01-15"

    lost = load_json(os.path.join(data_dir, "lost_items.json"))
    assert lost == []
    archive = load_json(os.path.join(data_dir, "archivio.json"))
    assert len(archive) == 1
    assert archive[0]["ritirato_da"] == "Mario"


def test_archivia_scaduti(tmp_path, monkeypatch):
    data_dir, _ = setup_temp_env(tmp_path, monkeypatch)

    today = datetime.now().date()
    old_date = (today - timedelta(days=31)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    utils.aggiungi_oggetto(
        villa="VS",
        data_ritrovamento=old_date,
        ora_ritrovamento="10:00",
        stato_notifica="avvisato",
        giorni_scadenza=30,
    )
    utils.aggiungi_oggetto(
        villa="VS",
        data_ritrovamento=today_str,
        ora_ritrovamento="12:00",
        stato_notifica="avvisato",
        giorni_scadenza=30,
    )



    count = utils.archivia_scaduti()
    assert count == 1

    lost = load_json(os.path.join(data_dir, "lost_items.json"))
    archive = load_json(os.path.join(data_dir, "archivio.json"))
    assert len(lost) == 1
    assert len(archive) == 1
    assert archive[0]["smaltito"] is True
