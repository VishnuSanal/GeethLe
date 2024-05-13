from flask import Flask, render_template, redirect

import geeth_le

app = Flask(__name__)

app.static_folder = 'static'


@app.route('/yt/<video_id>')
def generate_from_youtube(video_id):
    title, description, frame_url, redirect_url = geeth_le.generate_from_youtube(video_id)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url,
                "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)


@app.route('/sp/<spotify_track_id>')
def generate_from_spotify(spotify_track_id):
    title, description, frame_url, redirect_url = geeth_le.generate_from_spotify(spotify_track_id)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url,
                "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)


@app.route('/<query>')
@app.route('/search/<query>')
def search_music(query):
    if len(query) == 0:
        return render_template('landing.html')

    title, description, frame_url, redirect_url = geeth_le.search_music(query)

    metadata = {'title': title, 'description': description, 'frame_url': frame_url, "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)


@app.route('/')
def welcome():
    return render_template('landing.html')


@app.route("/sp")
@app.route("/yt")
@app.route('/search')
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)  # you know what this is :)
