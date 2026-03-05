
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
client_id="2e5953acc6bd47f3a0062b115afbd521"
client_secret="09b641d37621468c85eece61fc2e1976"

auth_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

sp = spotipy.Spotify(auth_manager=auth_manager)

def search_song(query, limit=5):

    results = sp.search(q=query, type="track", limit=limit)

    songs = []
    for track in results["tracks"]["items"]:
        songs.append({
            "name": track["name"],
            "artist": ", ".join([a["name"] for a in track["artists"]]),
            "album": track["album"]["name"],
            "url": track["external_urls"]["spotify"]
        })

    return songs


def autoplay_song(query):
    songs = search_song(query, 1)

    if songs:
        song = songs[0]
        print(f"🎵 Playing: {song['name']} - {song['artist']}")
        webbrowser.open(song["url"])
    else:
        print("No song found")


# Example
autoplay_song("karan aujla")