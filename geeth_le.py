import datetime
import logging
import os
import tempfile
import textwrap
from io import BytesIO

import firebase_admin
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import storage

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
BASE_URL = os.getenv('BASE_URL')

firebase_admin.initialize_app(
    credentials.Certificate('service_account_key.json'),
    {'storageBucket': BASE_URL}
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def upload_frame(video_id, frame_image):
    blob = storage.bucket().blob(video_id + ".png")

    if not blob.exists():
        temp_file = tempfile.NamedTemporaryFile(suffix=".png")
        frame_image.save(temp_file.name)

        blob.upload_from_file(file_obj=temp_file, content_type="image/png")

    return blob.generate_signed_url(datetime.timedelta(days=15))


def generate(entity_id, album, title, artist, thumbnail_url):
    logger.info("#generate")

    logger.info(f'entity_id: {entity_id}')
    logger.info(f'album: {album}')
    logger.info(f'title: {title}')
    logger.info(f'artist: {artist}')
    logger.info(f'thumbnail_url: {thumbnail_url}')

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

    text_draw.text(xy=(250, 415), align='centre', text=title_wrapped[0], fill=(233, 227, 241),
                   font=ImageFont.truetype('poppins.ttf', 32),
                   anchor="mm")

    text_draw.text(xy=(250, 455), align='centre', text=description_wrapped, fill=(233, 227, 241),
                   font=ImageFont.truetype('poppins.ttf', 18),
                   anchor="mm")

    frame_image_url = upload_frame(entity_id, frame_image)

    logger.info(f'frame_image_url: {frame_image_url}')

    return frame_image_url


def generate_from_youtube(video_id):
    logger.info("#generate_from_youtube")

    link = "https://www.youtube.com/watch?v=" + video_id

    odesli_request_url = "https://api.song.link/v1-alpha.1/links?userCountry=IN&url=" + link

    logger.info(f'odesli_request_url: {odesli_request_url}')

    odesli_request = requests.get(odesli_request_url)

    if odesli_request.status_code != 200:
        logger.error("Odesli request failed: " + str(odesli_request.status_code))
        exit(1)

    odesli_response_json = odesli_request.json()

    odesli_spotify_unique_id = odesli_response_json["linksByPlatform"]["spotify"]["entityUniqueId"]

    odesli_spotify_entity = odesli_response_json["entitiesByUniqueId"][odesli_spotify_unique_id]

    spotify_track_id = odesli_spotify_entity["id"]

    spotify_request_url = "https://api.spotify.com/v1/tracks/" + spotify_track_id

    logger.info(f'spotify_request_url: {spotify_request_url}')

    access_token = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'grant_type=client_credentials&client_id={SPOTIFY_CLIENT_ID}&client_secret={SPOTIFY_CLIENT_SECRET}'
    ).json()["access_token"]

    spotify_request = requests.get(spotify_request_url,
                                   headers={"Authorization": f'Bearer {access_token}'})

    if spotify_request.status_code != 200:
        logger.error("Spotify request failed: " + str(spotify_request.status_code))
        exit(1)

    spotify_response_json = spotify_request.json()

    title = spotify_response_json["name"]
    artist = spotify_response_json["artists"][0]["name"]
    album = spotify_response_json["album"]["name"]
    thumbnail_url = spotify_response_json["album"]["images"][0]["url"]

    frame_image_url = generate(video_id, album, title, artist, thumbnail_url)

    return title, f'{album} • {artist}', frame_image_url, f'http://youtu.be/{video_id}'


def generate_from_spotify(spotify_track_id):
    logger.info("#generate_from_spotify")

    spotify_request_url = "https://api.spotify.com/v1/tracks/" + spotify_track_id

    logger.info(f'spotify_request_url: {spotify_request_url}')

    access_token = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'grant_type=client_credentials&client_id={SPOTIFY_CLIENT_ID}&client_secret={SPOTIFY_CLIENT_SECRET}'
    ).json()["access_token"]

    spotify_request = requests.get(spotify_request_url,
                                   headers={"Authorization": f'Bearer {access_token}'})

    if spotify_request.status_code != 200:
        logger.error("Spotify request failed: " + str(spotify_request.status_code))
        exit(1)

    spotify_response_json = spotify_request.json()

    title = spotify_response_json["name"]
    artist = spotify_response_json["artists"][0]["name"]
    album = spotify_response_json["album"]["name"]
    thumbnail_url = spotify_response_json["album"]["images"][0]["url"]

    frame_image_url = generate(spotify_track_id, album, title, artist, thumbnail_url)

    return title, f'{album} • {artist}', frame_image_url, f'https://open.spotify.com/track/{spotify_track_id}'


def search_music(query):
    logger.info("#search_music")

    search_request_url = "https://api.spotify.com/v1/search?type=track&limit=1&market=IN&q=" + query

    logger.info(f'search_request_url: {search_request_url}')

    access_token = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'grant_type=client_credentials&client_id={SPOTIFY_CLIENT_ID}&client_secret={SPOTIFY_CLIENT_SECRET}'
    ).json()["access_token"]

    search_request = requests.get(search_request_url,
                                  headers={"Authorization": f'Bearer {access_token}'})

    if search_request.status_code != 200:
        logger.error("Spotify request failed: " + str(search_request.status_code))
        exit(1)

    spotify_track_id = search_request.json()["tracks"]["items"][0]["id"]

    spotify_request_url = "https://api.spotify.com/v1/tracks/" + spotify_track_id

    logger.info(f'spotify_request_url: {spotify_request_url}')

    access_token = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'grant_type=client_credentials&client_id={SPOTIFY_CLIENT_ID}&client_secret={SPOTIFY_CLIENT_SECRET}'
    ).json()["access_token"]

    spotify_request = requests.get(spotify_request_url,
                                   headers={"Authorization": f'Bearer {access_token}'})

    if spotify_request.status_code != 200:
        logger.error("Spotify request failed: " + str(spotify_request.status_code))
        exit(1)

    spotify_response_json = spotify_request.json()

    title = spotify_response_json["name"]
    artist = spotify_response_json["artists"][0]["name"]
    album = spotify_response_json["album"]["name"]
    thumbnail_url = spotify_response_json["album"]["images"][0]["url"]

    frame_image_url = generate(spotify_track_id, album, title, artist, thumbnail_url)

    return title, f'{album} • {artist}', frame_image_url, f'https://open.spotify.com/track/{spotify_track_id}'
