# GeethLe (गीत ले) - Search for Songs from **Anywhere**!

> :warning: some features stopped working due to the latest changes to the Spotify API switching to a paid-only model. Working on figuring out a fix - but might take a bit of time! more details on <a href=https://github.com/VishnuSanal/GeethLe/issues/2>this issue</a>

### What?

GeethLe makes sharing music easy! Search for any song from anywhere with geethle.tech/<your+fav+song> and instantly get a permalink to the song along with a thumbnail with metadata. It’ll redirect you to YouTube Music, saving time when sharing tracks.

Sooo, say you're talking to someone over WhatsApp & want to mention about a song. And, you're too lazy to go find the link. :D Don't worry, I have your back!

```https://geethle.tech/<query>```

GeethLe finds the track, generates a custom thumbnail with metadata + it redirects to YouTube Music once you click on the link. 🙂

### How to use?

- ```https://geethle.tech/<query>```

### Architecture

```
  ┌──────────────────────────────────────────────┐
  │              geethle.tech                    │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
                 /<query>
                      │
                      ▼
  ┌───────────────────────────────────────────────┐
  │                  app.py                       │
  │              (Flask Routes)                   │
  └───────────────────┬───────────────────────────┘
                      │
                      ▼
  ┌──────────────────────────────────────────────┐
  │               geeth_le.py                    │
  │           (Core Business Logic)              │
  │                                              │
  │  search_music()  ──► iTunes Search API       │
  │               │                              │
  │               ▼                              │
  │  ┌─────────────────────────────────┐         │
  │  │  _generate()                    │         │
  │  │  Download album art             │         │
  │  │  Overlay title + artist + album │         │
  │  │  (Pillow + Geist font)          │         │
  │  └────────────┬────────────────────┘         │
  │               ▼                              │
  │  ┌─────────────────────────────────┐         │
  │  │  _supabase_upload_frame()       │         │
  │  │  Upload to Supabase Storage     │         │
  │  │  Return signed URL (15-day TTL) │         │
  │  └─────────────────────────────────┘         │
  │               │                              │
  │               ▼                              │
  │  ┌─────────────────────────────────┐         │
  │  │  _find_yt_music_link()          │         │
  │  │  ytmusicapi search              │         │
  │  └─────────────────────────────────┘         │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  ┌───────────────────────────────────────────────┐
  │            index.html (Template)              │
  │                                               │
  │  - OG / Twitter Card meta tags                │
  │    (title, description, thumbnail URL)        │
  │  - JS redirect to YouTube Music               │
  └───────────────────┬───────────────────────────┘
                      │
                      ▼
                YouTube Music
```

#### External APIs

```
  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
  │  iTunes API  │    │  ytmusicapi  │    │  Supabase Storage    │
  │              │    │              │    │                      │
  │  - Search    │    │  - Song      │    │  - Thumbnail hosting │
  │  - Metadata  │    │    lookup    │    │  - Signed URLs       │
  │  - Album art │    │              │    │                      │
  └──────────────┘    └──────────────┘    └──────────────────────┘
```

### Credits

- Uses the [iTunes Search API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/) to fetch music metadata.
- Uses [ytmusicapi](https://github.com/sigma67/ytmusicapi) to resolve YouTube Music links.
- Uses [Geist](https://vercel.com/font) font for the thumbnails.
- **[@AkashChand6n](https://github.com/AkashChand6n)** with whose convo lead me to this idea ;__;
- **[@AbhiramVAnand](https://github.com/AbhiramVAnand)** for helping me with stuff
- **[@anima-regem](https://github.com/anima-regem)**, **[@AbhiramKunnath](https://github.com/AbhiramKunnath)** & **[@SherhinShoukath](https://github.com/SherhinShoukath)** for suggestions & feedback

### Example

<p align="center">
  <img src="https://github.com/user-attachments/assets/2c8c6a41-5616-4727-ad5c-12c5ff1eba7f" height=600 style="pointer-events: none;  cursor: default;" />
</p>
