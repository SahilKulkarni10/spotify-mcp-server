import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="3915910da4d6499a8ac95f24252a7f80",
    client_secret="abff2abefa394213b5f9a69f65bf5300",
    redirect_uri="http://localhost:8080",
    scope="playlist-modify-public playlist-modify-private"
))

token = sp.auth_manager.get_access_token()
print(f"ACCESS TOKEN: {token['access_token']}")