#!/usr/bin/env python3
"""
Update Oranje/WK-nieuws voor De Liefhebbers nieuwsfeed.

Scraped RSS-feeds van Nederlandse voetbalbronnen, filtert op trefwoorden
en schrijft het resultaat naar data/nieuws.json.

Wordt elke dag uitgevoerd door GitHub Actions.
"""

import feedparser
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# === CONFIGURATIE ===

# RSS-feeds om te scrapen
FEEDS = [
    {
        "naam": "NOS Voetbal",
        "url": "https://feeds.nos.nl/nosvoetbal",
    },
    {
        "naam": "Voetbalzone",
        "url": "https://www.voetbalzone.nl/rss.xml",
    },
    {
        "naam": "AD Voetbal",
        "url": "https://www.ad.nl/voetbal/rss.xml",
    },
    {
        "naam": "VI",
        "url": "https://www.vi.nl/rss",
    },
]

# Trefwoorden die een artikel ORANJE-gerelateerd maken
ORANJE_TREFWOORDEN = [
    "oranje", "nederlands elftal", "knvb", "koeman",
    "memphis", "depay", "van dijk", "frenkie de jong", "gakpo",
    "dumfries", "verbruggen", "reijnders", "gravenberch", "timber",
    "malen", "weghorst", "brobbey", "lang", "ake", "aké",
    "ons oranje", "onsoranje", "de jong",
]

# Trefwoorden die een artikel ALGEMEEN WK-nieuws maken
WK_ALGEMEEN_TREFWOORDEN = [
    "wk 2026", "wk-2026", "wereldkampioenschap",
    "fifa", "world cup", "wk voetbal",
    "groep f", "japan",  # bij twijfel: Japan-nieuws is voor ons relevant
]

# Trefwoorden die als HOT markeren (urgent / breaking)
HOT_TREFWOORDEN = [
    "selectie", "blessure", "geblesseerd", "afgevallen", "afgehaakt",
    "definitief", "bekend gemaakt", "bekendgemaakt",
    "twijfel", "uitvaller", "fit", "rentree", "comeback",
]

# Maximaal aantal items in de uiteindelijke JSON
MAX_ITEMS = 20

# Pad naar output JSON
OUTPUT_PAD = Path(__file__).parent.parent / "data" / "nieuws.json"


def bevat_trefwoord(tekst: str, trefwoorden: list) -> bool:
    """Check of een trefwoord in de tekst voorkomt (case-insensitive, hele woorden)."""
    tekst_lower = tekst.lower()
    for woord in trefwoorden:
        # Match hele woorden met word boundary
        if re.search(r'\b' + re.escape(woord.lower()) + r'\b', tekst_lower):
            return True
    return False


def classificeer(titel: str, samenvatting: str) -> dict:
    """Bepaal categorie en of het 'hot' is."""
    volledige_tekst = f"{titel} {samenvatting}"

    is_oranje = bevat_trefwoord(volledige_tekst, ORANJE_TREFWOORDEN)
    is_wk = bevat_trefwoord(volledige_tekst, WK_ALGEMEEN_TREFWOORDEN)
    is_hot = bevat_trefwoord(volledige_tekst, HOT_TREFWOORDEN)

    # Categorie: oranje wint van wk-algemeen
    if is_oranje:
        categorie = "oranje"
    elif is_wk:
        categorie = "algemeen"
    else:
        return None  # niet relevant

    return {
        "categorie": categorie,
        "hot": is_hot,
    }


def schoonmaken_tekst(html: str) -> str:
    """Strip HTML-tags en truncate."""
    # Verwijder HTML
    schoon = re.sub(r'<[^>]+>', '', html or '')
    # Verwijder dubbele whitespace
    schoon = re.sub(r'\s+', ' ', schoon).strip()
    # Truncate
    if len(schoon) > 300:
        schoon = schoon[:297] + "..."
    return schoon


def parse_datum(entry) -> str:
    """Probeer een leesbare datum te maken."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    return datetime.now(timezone.utc).isoformat()


def haal_nieuws_op():
    """Haal alle feeds op en filter."""
    alle_items = []

    for feed_config in FEEDS:
        print(f"📡 Ophalen: {feed_config['naam']}")
        try:
            feed = feedparser.parse(feed_config['url'])
            if feed.bozo:
                print(f"  ⚠️  Waarschuwing: {feed.bozo_exception}")

            for entry in feed.entries[:30]:  # max 30 per feed
                titel = entry.get('title', '').strip()
                samenvatting = schoonmaken_tekst(entry.get('summary', ''))
                link = entry.get('link', '')
                datum_iso = parse_datum(entry)

                if not titel:
                    continue

                classificatie = classificeer(titel, samenvatting)
                if classificatie is None:
                    continue

                alle_items.append({
                    "titel": titel,
                    "samenvatting": samenvatting,
                    "bron": feed_config['naam'],
                    "link": link,
                    "datum": datum_iso,
                    "categorie": classificatie['categorie'],
                    "hot": classificatie['hot'],
                })

            print(f"  ✓ {feed_config['naam']}: {len(feed.entries)} entries gescand")
        except Exception as e:
            print(f"  ❌ Fout bij {feed_config['naam']}: {e}")
            continue

    # Sorteer op datum (nieuwste eerst)
    alle_items.sort(key=lambda x: x['datum'], reverse=True)

    # Dedup op titel (kan in meerdere feeds voorkomen)
    gezien = set()
    unieke_items = []
    for item in alle_items:
        # Normaliseer titel voor dedup
        sleutel = re.sub(r'\W+', '', item['titel'].lower())[:80]
        if sleutel not in gezien:
            gezien.add(sleutel)
            unieke_items.append(item)

    # Limiteer
    return unieke_items[:MAX_ITEMS]


def main():
    print("=" * 60)
    print("🧡 DE LIEFHEBBERS — NIEUWS UPDATE 🧡")
    print(f"Tijd: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    items = haal_nieuws_op()

    output = {
        "laatste_update": datetime.now(timezone.utc).isoformat(),
        "aantal_items": len(items),
        "items": items,
    }

    OUTPUT_PAD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PAD, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(items)} items geschreven naar {OUTPUT_PAD}")

    # Korte samenvatting
    oranje = sum(1 for i in items if i['categorie'] == 'oranje')
    algemeen = sum(1 for i in items if i['categorie'] == 'algemeen')
    hot = sum(1 for i in items if i['hot'])
    print(f"   🧡 Oranje: {oranje}")
    print(f"   ⚽ Algemeen: {algemeen}")
    print(f"   🔥 Hot: {hot}")


if __name__ == "__main__":
    main()
