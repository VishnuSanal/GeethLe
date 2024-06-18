from flask import Flask, render_template, redirect

import geeth_le

app = Flask(__name__)

app.static_folder = 'static'


@app.route('/')
def welcome():
    return render_template('landing.html')


@app.route('/<query>')
@app.route('/<target>/<query>')  # target = ""/sp/spotify, yt/youtube, ytm/youtubemusic
def search_music(query, target=""):
    if len(query) == 0 or query == "favicon.ico":
        return render_template('landing.html')

    title, description, frame_url, redirect_url = geeth_le.search_music(target.lower(), query)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url, "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)


@app.route("/sp")
@app.route("/spotify")
@app.route("/yt")
@app.route("/youtube")
@app.route("/ytm")
@app.route("/youtubemusic")
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)  # you know what this is :)


@app.route('/yt_id/<video_id>')
def generate_from_youtube(video_id):
    title, description, frame_url, redirect_url = geeth_le.generate_from_youtube(video_id)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url,
                "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)


@app.route('/sp_id/<spotify_track_id>')
def generate_from_spotify(spotify_track_id):
    title, description, frame_url, redirect_url = geeth_le.generate_from_spotify(spotify_track_id)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url,
                "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)
