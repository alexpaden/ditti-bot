import os

import requests


def test_connect_imgur():
    client_id = os.getenv("IMGUR_CLIENT")
    client_secret = os.getenv("IMGUR_SECRET")
    headers = {"Authorization": f"Client-ID {client_id}"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    url = "https://api.imgur.com/oauth2/token"
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    assert "access_token" in response_json or response.status_code == 500
