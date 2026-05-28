from flask import Flask, render_template, redirect, abort

import geeth_le

app = Flask(__name__)

app.static_folder = 'static'

_NON_QUERY_PATHS = {
    'favicon.ico', 'robots.txt', 'sitemap.xml', 'ads.txt',
    'apple-touch-icon.png', 'apple-touch-icon-precomposed.png',
}


@app.route('/')
def welcome():
    return render_template('landing.html')


@app.route('/<query>')
def search_music(query):
    if query in _NON_QUERY_PATHS:
        abort(404)

    result = geeth_le.search_music(query)
    if result is None:
        return render_template('landing.html')

    title, description, frame_url, redirect_url = result

    metadata = {'title': title, 'description': description, 'frame_url': frame_url, "redirect_url": redirect_url}
    return render_template('index.html', metadata=metadata)