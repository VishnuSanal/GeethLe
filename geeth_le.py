import logging
import os
import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
from ytmusicapi import YTMusic

from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

yt = YTMusic()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _supabase_upload_frame(video_id, frame_image):
    path = f"{video_id}.png"
    bucket = supabase.storage.from_("GeethLe")

    if not _supabase_thumb_exists(bucket, path):
        buffer = BytesIO()
        frame_image.save(buffer, format="PNG")

        bucket.upload(
            path=path,
            file=buffer.getvalue(),
            file_options={"content-type": "image/png"},
        )

    # expires_in is in SECONDS; 15 days = 15 * 24 * 60 * 60
    res = bucket.create_signed_url(path, 60 * 60 * 24 * 15)
    return res["signedURL"]


def _supabase_thumb_exists(bucket, path):
    folder, _, name = path.rpartition("/")
    return any(f["name"] == name for f in bucket.list(folder))

def _find_yt_music_link(artist, title):
    logger.info("#find_yt_music_link")

    results = yt.search(f"{artist} {title}", filter="songs", limit=1)

    youtube_id = results[0]["videoId"]
    return f"https://music.youtube.com/watch?v={youtube_id}"

def _generate(entity_id, album, title, artist, thumbnail_url):
    logger.info(
        f'''#generate: {{
            "entity_id": "{entity_id}",
            "album": "{album}",
            "title": "{title}",
            "artist": "{artist}",
            "thumbnail_url": "{thumbnail_url}"
        }}'''
    )

    thumbnail_512_request = requests.get(thumbnail_url.replace("100x100bb.jpg", "512x512bb.jpg"))

    if thumbnail_512_request.status_code == 200:
        thumbnail_content = thumbnail_512_request.content
    else:
        thumbnail_content = requests.get(thumbnail_url).content

    frame_image = Image.open(BytesIO(thumbnail_content)).resize((500, 500))

    overlay_size = (484, 135)  # 500 - 16

    blur_overlay = Image.new(mode='RGBA', size=overlay_size, color=(0, 0, 0))

    overlay_mask = Image.new('L', overlay_size, 0)

    rounded_rect_draw = ImageDraw.Draw(overlay_mask)
    rounded_rect_draw.rounded_rectangle(((0, 0), overlay_size), 12, fill=127)

    overlay_mask.filter(ImageFilter.BLUR).convert("RGBA")

    frame_image.paste(blur_overlay, (8, 357), overlay_mask)

    text_draw = ImageDraw.Draw(frame_image)

    title_wrapped = textwrap.wrap(title, 29)
    album_wrapped = textwrap.wrap(album, 25)
    artist_wrapped = textwrap.wrap(artist, 25)

    if len(title_wrapped) > 1:
        title_wrapped[0] = title_wrapped[0][0:25] + " ..."

    if len(album_wrapped) > 1:
        album_wrapped[0] = album_wrapped[0][0:21] + " ..."

    if len(artist_wrapped) > 1:
        artist_wrapped[0] = artist_wrapped[0][0:21] + " ..."

    description_wrapped = f'{album_wrapped[0]} • {artist_wrapped[0]}'

    text_draw.text(xy=(250, 415), align='center', text=title_wrapped[0], fill=(233, 227, 241),
                   font=ImageFont.truetype('geist_medium.ttf', 32),
                   anchor="mm")

    text_draw.text(xy=(250, 455), align='center', text=description_wrapped, fill=(233, 227, 241),
                   font=ImageFont.truetype('geist_medium.ttf', 18),
                   anchor="mm")

    frame_image_url = _supabase_upload_frame(entity_id, frame_image)

    logger.info(f'frame_image_url: {frame_image_url}')

    return frame_image_url


def search_music(query):
    logger.info("#search_music")

    search_request_url = "https://itunes.apple.com/search?media=music&entity=song&attribute=songTerm&limit=1&term=" + query

    logger.info(f'search_request_url: {search_request_url}')

    search_request = requests.get(search_request_url)

    if search_request.status_code != 200:
        logger.error("iTunes request failed: " + str(search_request.status_code))
        exit(1)

    song_result_object = search_request.json()["results"][0]

    itunes_song_id = str(song_result_object["trackId"])
    title = song_result_object["trackName"]
    artist = song_result_object["artistName"]
    album = song_result_object["collectionName"]
    thumbnail_url = song_result_object["artworkUrl100"]

    frame_image_url = _generate(itunes_song_id, album, title, artist, thumbnail_url)

    yt_link = _find_yt_music_link(artist, title)

    return title, f'{album} • {artist}', frame_image_url, yt_link