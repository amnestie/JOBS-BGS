#!/usr/bin/env python3
"""
Collector fuer den Arbeitsmarkt-Tracker Braunschweig.

Laeuft in GitHub Actions (oder lokal): fragt die BA-Jobsuche fuer Braunschweig
(10 km) ab und schreibt einen Tages-Snapshot in docs/data.json. Das Dashboard
(docs/index.html) liest diese Datei. Idempotent: mehrfach am selben Tag
ueberschreibt den heutigen Snapshot statt zu duplizieren.
"""

import json
import os
import time
import datetime

import requests

API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
DATA = os.path.join("docs", "data.json")

WO = "Braunschweig"
UMKREIS = 10

# (dimension, wert, extra_params)
QUERIES = [
    ("gesamt",      "alle",        {}),
    ("neu",         "heute",       {"veroeffentlichtseit": 1}),
    ("neu",         "7_tage",      {"veroeffentlichtseit": 7}),
    ("arbeitszeit", "vollzeit",    {"arbeitszeit": "vz"}),
    ("arbeitszeit", "teilzeit",    {"arbeitszeit": "tz"}),
    ("arbeitszeit", "homeoffice",  {"arbeitszeit": "ho"}),
    ("arbeitszeit", "minijob",     {"arbeitszeit": "mj"}),
    ("angebotsart", "arbeit",      {"angebotsart": 1}),
    ("angebotsart", "ausbildung",  {"angebotsart": 4}),
    ("angebotsart", "praktikum",   {"angebotsart": 34}),
    ("befristung",  "befristet",   {"befristung": 1}),
    ("befristung",  "unbefristet", {"befristung": 2}),
]


def fetch_count(session, extra_params):
    params = {"wo": WO, "umkreis": UMKREIS, "size": 1, "page": 1}
    params.update(extra_params)
    r = session.get(API_URL, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("maxErgebnisse", len(data.get("stellenangebote", [])))


def main():
    today = datetime.date.today().isoformat()
    session = requests.Session()

    werte, fehler = {}, []
    for dimension, wert, extra in QUERIES:
        key = f"{dimension}/{wert}"
        try:
            werte[key] = fetch_count(session, extra)
            print(f"  {key:24} {werte[key]:>6}")
        except Exception as e:
            fehler.append(f"{key}: {e}")
            print(f"  [FEHLER] {key}: {e}")
        time.sleep(0.4)

    if os.path.exists(DATA):
        with open(DATA, encoding="utf-8") as f:
            doc = json.load(f)
    else:
        doc = {"meta": {"wo": WO, "umkreis": UMKREIS}, "snapshots": []}

    # heutigen Snapshot ersetzen (idempotent), dann anhaengen + sortieren
    doc["snapshots"] = [s for s in doc["snapshots"] if s["datum"] != today]
    doc["snapshots"].append({"datum": today, "werte": werte})
    doc["snapshots"].sort(key=lambda s: s["datum"])
    doc["meta"]["wo"] = WO
    doc["meta"]["umkreis"] = UMKREIS
    doc["meta"]["aktualisiert"] = datetime.datetime.now(
        datetime.timezone.utc).isoformat(timespec="seconds")

    os.makedirs("docs", exist_ok=True)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"\nSnapshot {today} geschrieben ({len(werte)} Werte, "
          f"{len(doc['snapshots'])} gesamt).")
    if fehler:
        print("Fehler:", *fehler, sep="\n  ")


if __name__ == "__main__":
    main()
