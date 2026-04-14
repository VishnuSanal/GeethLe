# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeethLe (गीत ले — "take a song") is a Flask web app for sharing music across platforms. Users search for a song and get a permalink with a custom-generated thumbnail containing metadata. The link auto-redirects visitors to their preferred music provider (Spotify, YouTube, or YouTube Music).

## Commands

- **Dev server**: `python run.py` (Flask debug mode)
- **Production**: `gunicorn app:app`
- **Install deps**: `pip install -r requirements.txt`

There are no tests or linting configured.

## Architecture

Two main files handle everything:

- **`app.py`** — Flask route handlers. Defines URL patterns for search (`/<query>`, `/sp/<query>`, `/yt/<query>`, `/ytm/<query>`) and direct ID lookups (`/yt_id/<id>`, `/sp_id/<id>`). Renders templates with Open Graph / Twitter Card metadata for social previews, then auto-redirects to the target platform.

- **`geeth_le.py`** — Core business logic. Orchestrates multiple external APIs:
  - **Spotify API** — track search and metadata retrieval (requires `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` in `.env`)
  - **Odesli API** (song.link) — cross-platform link resolution (e.g., YouTube ID → Spotify track)
  - **Firebase Cloud Storage** — hosts generated thumbnail images (requires `BASE_URL` in `.env` and `service_account_key.json`)
  - **Pillow** — generates thumbnail images overlaying track metadata onto album art using `geist_medium.ttf`

## Key Flow

1. User hits a search route → `search_music()` queries Spotify → gets track metadata
2. `generate()` downloads album art, composites metadata text onto it with Pillow
3. `upload_frame()` uploads the thumbnail to Firebase, returns a signed URL (15-day expiry)
4. Flask renders `index.html` with OG meta tags pointing to the thumbnail, plus a JS redirect to the target platform URL

## Environment

Required env vars in `.env`:
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`
- `BASE_URL` (Firebase storage bucket)

`service_account_key.json` must exist at project root for Firebase auth (sensitive, gitignored).

## Deployment

Hosted on Render. Domain: geethle.tech.
