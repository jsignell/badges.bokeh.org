import requests


def pip_badge():
    badge_url = "https://img.shields.io/pypi/dm/bokeh.svg"
    badge_request = requests.get(badge_url, stream=True)
    return badge_request.raw.read(decode_content=True).decode('utf-8')
