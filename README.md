# WordSelah — v1 (demo)

A small desktop companion that shows one scripture at a time, with a personal
declaration written underneath it. This is the first demo: the window, the
verses, and the declarations.

## Run it

Needs Python 3 with Tkinter (included with the python.org installers for
Windows and macOS; on Debian/Ubuntu run `sudo apt install python3-tk`).

```
python main.py
```

- **HIDE** sends the window to the taskbar/dock.
- **Space bar** shows a new scripture (a temporary key for testing).

## What is in the demo

| File | What it does |
|---|---|
| `main.py` | The window: gold-on-brown card, the verse, the declaration, the stats row and the HIDE button. |
| `bible_verse.py` | The references and the declarations shown under each verse. `{name}` in a declaration is replaced by the user's name. No scripture text is stored here. |
| `bible_api.py` | Fetches a King James Version verse from the free bible-api.com service and caches it on disk. |

## About the verses

- The verse text is the **King James Version** (public domain), fetched from the free
  [bible-api.com](https://bible-api.com) service. No API key is needed.
- Each verse is saved to `~/.wordselah/kjv_cache.json` the first time it is shown, so it is
  downloaded once and still works offline afterwards. The first run needs an internet connection.
- The declarations under each verse are personal and live in `bible_verse.py`.

## If verses will not load

The window shows the reason, and the full error is printed in the Run window. To test the
connection on its own, run `bible_api.py` (right-click > Run in PyCharm). A certificate error
on macOS is fixed by running `Install Certificates.command` in the Python folder, or
`pip install certifi`.

## Not built yet (placeholders in the demo)

- The two-hour timer. The footer text is a placeholder.
- The **Read** and **Saved** counters. They show 0 until the database step.
- Asking for the user's name. `USER_NAME` in `main.py` is set to a placeholder.

## Roadmap

| Version | What gets built | Focus |
|---|---|---|
| **v1 — Smart Desktop** | Two-hour scheduler, saved preferences, no-repeat logic, SQLite | Python architecture and persistence |
| **v2 — Personal Companion** | Favorites, prayer journal, birthdays, search | Database design and CRUD |
| **v3 — Web Application** | FastAPI, responsive website, user accounts, sync | Backend engineering and REST APIs |
| **v4 — Production Ready** | Offline PWA, notifications, automated tests, deployment | Security, reliability, production workflows |
