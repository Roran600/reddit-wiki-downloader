# Reddit Wiki Backup

Zálohovanie Reddit wiki stránok bez API - len cez requests + BeautifulSoup.

## Čo to robí

- Sťahuje všetky wiki stránky z reddit subredditov
- Ukladá obsah v dvoch formátoch: **HTML** aj **Markdown**
- Automaticky rieši rate limiting (Reddit API obmedzenia)
- Loguje chyby pre diagnostiku

## Inštalácia

```bash
# Klonovanie / vytvorenie adresára
cd reddit-wiki-zaloha

# Vytvorenie virtuálneho prostredia
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Inštalácia závislostí
pip install -r requirements.txt
```

## Konfigurácia

Uprav súbor `config.json`:

```json
{
    "subreddits": [
        "nba",
        "soccer",
        "hockey"
    ],
    "rate_limit_delay": 5,
    "user_agent": "RedditWikiBackup/1.0 (by u/username)"
}
```

| Parameter | Popis |
|-----------|-------|
| `subreddits` | Zoznam subredditov na zálohovanie |
| `rate_limit_delay` | Sekundy medzi požiadavkami (default: 5) |
| `user_agent` | Identifikátor - odporúčam zmeniť na tvoje username |

## Spustenie

```bash
source venv/bin/activate
python backup.py
```

## Výstup

Zálohy sa ukladajú do adresára `backups/`:

```
backups/
└── r_nba/
    ├── index.html
    ├── index.md
    ├── rules.html
    ├── rules.md
    └── ...
```

- `.html` - surový HTML výstup z Reddit
- `.md` - Markdown verzia (priamo z Reddit API)

## Rate Limiting

Reddit má prísne limity na požiadavky. Skript obsahuje:
- Čakanie medzi požiadavkami (nastaviteľné v config)
- Exponential backoff pri 429 chybách (automatické spomalenie)
- Retry logika (až 5 pokusov)

### Ak dostávaš 429 chyby

1. Zvýš `rate_limit_delay` v config.json (napr. na 10)
2. Počkaj 10-15 minút
3. Spusti znova

## Riešenie problémov

### Žiadne súbory sa nestiahli
- Skontroluj `errors.log` - obsahuje detaily chýb
- Pravdepodobne rate limiting - uprav delay

### Chyba "list indices must be integers or slices"
- Zastaralá verzia - stiahni aktuálny kód

### Wiki stránky sú prázdne
- Niektoré wiki vyžadujú prihlásenie (súkromné wiki)
- Skontroluj či máš prístup cez prehliadač

## Poznámky

- Reddit API nie je oficiálne potrebné - používa verejné endpointy
- Súkromné wiki (len pre moderatorov) môžu vyžadovať auth
- Skript je určený pre osobné zálohy - neporušuj Terms of Service

## Spustenie cez run_backup.sh

Pre jednoduchšie spustenie a bezpečné ukončenie použi skript `run_backup.sh`:

```bash
./run_backup.sh
```

**Výhody:**
- Automaticky aktivuje virtuálne prostredie
- Ukladá PID procesu pre sledovanie
- Pri Ctrl+C vykoná **graceful ukončenie** (pošle SIGINT namiesto SIGKILL)
- Všetky už stiahnuté súbory zostanú zachované
- Čistý výstup so správami o stave

**Ukončenie:**
- Stlač `Ctrl+C` pre bezpečné ukončenie
- Skript počká max 10s na čistené ukončenie
- Ak proces neodpovie, núdzovo ukončí (SIGKILL)
