import random

from langchain.tools import tool 
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
    fetch_count = max(limit * 3, 20)
    results = sp.search(q=query, type="track", limit=fetch_count)

    songs = []
    for track in results["tracks"]["items"]:
        songs.append({
            "name": track["name"],
            "artist": ", ".join([a["name"] for a in track["artists"]]),
            "album": track["album"]["name"],
            "url": track["external_urls"]["spotify"]
        })
    random.shuffle(songs)
    return songs[:limit]


def autoplay_song(query):
    songs = search_song(query, 1)

    if songs:
        song = songs[0]
        webbrowser.open(song["url"])
        return f"🎵 Playing: {song['name']} - {song['artist']}"
    else:
        print("No song found")

@tool
def play_music(query: str) -> str:
    """
    Play music from Spotify based on a search query.

    Use this tool when the user asks to:
    - play a song
    - play music by an artist
    - listen to music
    - start a track

    The tool searches Spotify for the query and automatically opens
    the first matching track in the user's browser using the Spotify web player.

    Args:
        query (str): Song name, artist name, or music search query.

    Returns:
        str: Confirmation of the song being played.
    """
    return autoplay_song(query)


if __name__=="__main__":
    # Example
    autoplay_song("karan aujla")