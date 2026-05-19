# 🧡🤒 De Liefhebbers — Oranje Koorts Dashboard

Live nieuwsfeed en dashboard richting het WK 2026, gemaakt voor de WhatsApp-groep
**🧡🤒De Liefhebbers🤒🧡🇳🇱🏆🎒**.

De feed wordt **elke ochtend automatisch bijgewerkt** via GitHub Actions
die RSS-feeds van Nederlandse voetbalbronnen scraped.

## ⚡ Snelle deploy (15 minuten)

### 1. Repo aanmaken op GitHub

1. Ga naar [github.com/new](https://github.com/new)
1. Maak een nieuwe **public** repo aan (Pages werkt gratis op public repos), bijvoorbeeld `de-liefhebbers`
1. Sla op je laptop dit hele mapje (de inhoud van deze ZIP) op
1. Upload de bestanden naar de repo, of vanaf de commandline:
   
   ```bash
   cd de-liefhebbers
   git init
   git add .
   git commit -m "🧡 Eerste versie Liefhebbers Dashboard"
   git branch -M main
   git remote add origin https://github.com/JOUW_NAAM/de-liefhebbers.git
   git push -u origin main
   ```

### 2. GitHub Pages aanzetten

1. In je repo → **Settings** → **Pages**
1. Bij **Source** kies `Deploy from a branch`
1. Bij **Branch** kies `main` en folder `/ (root)`
1. Save

Na ~1 minuut staat je site live op:
**`https://JOUW_NAAM.github.io/de-liefhebbers/`**

Deze link kun je delen in de WhatsApp-groep. 📲

### 3. Workflow-rechten aanzetten

Belangrijk: GitHub Actions moet commits terug kunnen pushen.

1. Repo → **Settings** → **Actions** → **General**
1. Scroll naar **Workflow permissions**
1. Kies `Read and write permissions`
1. Save

### 4. De eerste run handmatig starten

1. Repo → tab **Actions** → klik op de workflow `Update Liefhebbers Nieuws`
1. Klik rechtsboven op **Run workflow** → **Run workflow**
1. Wacht ~30 sec, je ziet of het lukt

Vanaf morgen draait het elke dag automatisch om **05:00 UTC** (07:00 NL zomertijd).

## 📂 Bestandsstructuur

```
.
├── index.html                    De app zelf
├── data/
│   └── nieuws.json              Wordt elke dag door Actions bijgewerkt
├── scripts/
│   ├── update_nieuws.py         Python-scraper
│   └── requirements.txt         Python-dependencies
├── .github/workflows/
│   └── update-nieuws.yml        Cron-job: dagelijks 07:00 NL
└── README.md
```

## 🔧 Aanpassingen

### Andere of meer bronnen toevoegen

Open `scripts/update_nieuws.py` en pas de lijst `FEEDS` aan:

```python
FEEDS = [
    {"naam": "NOS Voetbal", "url": "https://feeds.nos.nl/nosvoetbal"},
    {"naam": "Eigen bron", "url": "https://voorbeeld.nl/rss"},
]
```

### Andere trefwoorden

Pas `ORANJE_TREFWOORDEN`, `WK_ALGEMEEN_TREFWOORDEN` of `HOT_TREFWOORDEN` aan.

### Andere update-frequentie

In `.github/workflows/update-nieuws.yml`, pas de cron-expressie aan:

```yaml
schedule:
  - cron: '0 5 * * *'    # Dagelijks 07:00 NL (huidige)
  # - cron: '0 */6 * * *'  # Elke 6 uur
  # - cron: '0 5,17 * * *' # 2x per dag: 07:00 en 19:00 NL
```

### De WK-selectie bijwerken

De selectie-lijst staat **hardcoded in `index.html`** (in het blok
“Waarschijnlijke WK-selectie”). Om bij te werken:

1. Open `index.html` in een editor
1. Zoek op `speler-naam` om alle spelers te vinden
1. Pas namen of percentages aan
1. Commit en push — GitHub Pages updatet automatisch binnen 1-2 minuten

> **Tip**: Op 27 mei om 14:45 maakt Koeman de definitieve selectie bekend.
> Werk daarna alle percentages bij naar 100% (of 0%) en zet ze in volgorde.

## 🐛 Troubleshooting

**“Nieuws wordt geladen…” blijft staan**
→ Open de browser console (F12). Meestal komt het door:

- `data/nieuws.json` bestaat niet (run workflow handmatig)
- CORS-fout: open de pagina via `https://...github.io/...` en niet via `file://`

**Workflow faalt met permission denied**
→ Stap 3 hierboven (Workflow permissions) overgeslagen.

**Sommige feeds geven 0 entries**
→ Sommige RSS-feeds blokkeren GitHub IP’s. Niet erg, andere bronnen vangen het op.

**Geen nieuws-items na een update?**
→ De trefwoordenfilter is misschien te strikt. Pas `update_nieuws.py` aan.

## 🏆 Plan voor het WK

- **Tot 27 mei**: dagelijks WK-selectienieuws
- **27 mei 14:45**: Koeman maakt selectie bekend → handmatig bijwerken
- **30 mei**: voorbereiding start in Zeist
- **3 juni**: NL – Algerije in De Kuip
- **14 juni 22:00**: NL – Japan in Dallas (aftrap! 🚀)
- **19 juli**: finale in MetLife Stadium, New York

## 💡 Credits

- Initiële versie gegenereerd met Claude (Anthropic)
- RSS-feeds: NOS, Voetbalzone, AD, Voetbal International
- Geen affiliatie met genoemde media; alleen koppen + samenvattingen worden getoond met bronvermelding en link naar het origineel

-----

🧡 Voor De Liefhebbers — alle wedstrijden, alle koorts, één doel: **WERELDKAMPIOEN** 🏆