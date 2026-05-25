import datetime
import logging
import os
import tempfile
import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def supabase_upload_frame(video_id, frame_image):
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


def generate(entity_id, album, title, artist, thumbnail_url):
    logger.info(
        f'''#generate: {{
            "entity_id": "{entity_id}",
            "album": "{album}",
            "title": "{title}",
            "artist": "{artist}",
            "thumbnail_url": "{thumbnail_url}"
        }}'''
    )

    frame_image = Image.open(BytesIO(requests.get(thumbnail_url).content)).resize((500, 500))

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

    frame_image_url = supabase_upload_frame(entity_id, frame_image)

    logger.info(f'frame_image_url: {frame_image_url}')

    return frame_image_url


def generate_from_youtube(video_id):
    logger.info("#generate_from_youtube")

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?platform=youtube&type=song&id=" + video_id

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    odesli_response_json = odesli_request.json()

    odesli_itunes_unique_id = odesli_response_json["linksByPlatform"]["itunes"]["entityUniqueId"]

    odesli_itunes_entity = odesli_response_json["entitiesByUniqueId"][odesli_itunes_unique_id]

    itunes_track_id = odesli_itunes_entity["id"]

    itunes_search_request_url = "https://itunes.apple.com/search?media=music&entity=song&attribute=songTerm&limit=1&term=" + query

    logger.info(f'itunes_search_request_url: {itunes_search_request_url}')

    itunes_search_request = requests.get(itunes_search_request_url)

    if itunes_search_request.status_code != 200:
        logger.error("iTunes request failed: " + str(itunes_search_request.status_code))
        exit(1)

    song_result_object = itunes_search_request.json()["results"][0]

    title = song_result_object["trackName"]
    artist = song_result_object["artistName"]
    album = song_result_object["collectionName"]
    thumbnail_url = song_result_object["artworkUrl100"]

    frame_image_url = generate(itunes_track_id, album, title, artist, thumbnail_url)

    return title, f'{album} • {artist}', frame_image_url, f'http://youtu.be/{video_id}'


def generate_from_spotify(spotify_track_id):
    logger.info("#generate_from_spotify")

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?platform=spotify&type=song&id=" + spotify_track_id

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    odesli_response_json = odesli_request.json()

    odesli_itunes_unique_id = odesli_response_json["linksByPlatform"]["itunes"]["entityUniqueId"]

    odesli_itunes_entity = odesli_response_json["entitiesByUniqueId"][odesli_itunes_unique_id]

    itunes_track_id = odesli_itunes_entity["id"]

    itunes_search_request_url = "https://itunes.apple.com/search?media=music&entity=song&attribute=songTerm&limit=1&term=" + query

    logger.info(f'itunes_search_request_url: {itunes_search_request_url}')

    itunes_search_request = requests.get(itunes_search_request_url)

    if itunes_search_request.status_code != 200:
        logger.error("iTunes request failed: " + str(itunes_search_request.status_code))
        exit(1)

    song_result_object = itunes_search_request.json()["results"][0]

    title = song_result_object["trackName"]
    artist = song_result_object["artistName"]
    album = song_result_object["collectionName"]
    thumbnail_url = song_result_object["artworkUrl100"]

    frame_image_url = generate(itunes_track_id, album, title, artist, thumbnail_url)

    return title, f'{album} • {artist}', frame_image_url, f'https://open.spotify.com/track/{spotify_track_id}'


def get_youtube_link(spotify_link):
    logger.info("#get_youtube_link")

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?userCountry=IN&url=" + spotify_link

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    odesli_response_json = odesli_request.json()

    print(odesli_response_json)

    return odesli_response_json["linksByPlatform"]["youtube"]["url"]


def get_youtube_music_link(spotify_link):
    logger.info("#get_youtube_music_link")

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?userCountry=IN&url=" + spotify_link

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    odesli_response_json = odesli_request.json()

    print(odesli_response_json)

    return odesli_response_json["linksByPlatform"]["youtubeMusic"]["url"]


def search_music(target, query):
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

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?platform=itunes&type=song&id=" + itunes_song_id

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    frame_image_url = generate(itunes_song_id, album, title, artist, thumbnail_url)

    odesli_response_json = odesli_request.json()

    # fixme: no spotify entity exists!
    odesli_spotify_unique_id = odesli_response_json["linksByPlatform"]["spotify"]["entityUniqueId"]

    odesli_spotify_entity = odesli_response_json["entitiesByUniqueId"][odesli_spotify_unique_id]

    spotify_track_id = odesli_spotify_entity["id"]

    spotify_link = f'https://open.spotify.com/track/{spotify_track_id}'

    if target == "yt" or target == "youtube":
        return title, f'{album} • {artist}', frame_image_url, get_youtube_link(spotify_link)

    if target == "ytm" or target == "youtubemusic":
        return title, f'{album} • {artist}', frame_image_url, get_youtube_music_link(spotify_link)

    return title, f'{album} • {artist}', frame_image_url, spotify_link
