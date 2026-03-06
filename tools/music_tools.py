import random
from langchain.tools import tool
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = "2e5953acc6bd47f3a0062b115afbd521"
client_secret = "09b641d37621468c85eece61fc2e1976"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=REDIRECT_URI,
    scope="user-modify-playback-state user-read-playback-state",
    cache_path="spotify_token.json",
    open_browser=True
)

sp = spotipy.Spotify(auth_manager=auth_manager)

def autoplay_song(query: str, no_of_songs: int = 1):
    results = sp.search(q=query, type="track", limit=no_of_songs)

    if not results or not results["tracks"]["items"]:
        return "No song found for that query."

    tracks = results["tracks"]["items"]

    devices = sp.devices()
    if not devices or not devices["devices"]:
        return "No active Spotify device found"

    try:
        current_playback = sp.current_playback()

        responses = []

        for i, track in enumerate(tracks):
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            track_uri = track["uri"]

            if i == 0 and not (current_playback and current_playback.get("is_playing")):
                sp.start_playback(uris=[track_uri])
                responses.append(f"Playing: {track_name} - {artist_name}")
            else:
                sp.add_to_queue(track_uri)
                responses.append(f"Queued: {track_name} - {artist_name}")

        return "\n".join(responses)

    except Exception as e:
        return f"❌ Failed to play/queue song. Error: {str(e)}"

@tool
def play_music(query: str, no_of_songs: int = 1) -> str:
    """
    Play music on Spotify based on a search query.

    This tool searches Spotify for tracks matching the query and then plays them.
    If Spotify is already playing something, the tracks will be added to the queue.
    If nothing is playing, the first track will start playing immediately.

    The number of tracks returned is controlled by `no_of_songs`.

    When to use:
    - User asks to play a specific song → use no_of_songs = 1
    - User asks to play songs from an artist → use 3–5 songs
    - User asks for multiple songs or a vibe/genre → use 5–10 songs

    Examples:
    - "Play Shape of You" → query="Shape of You", no_of_songs=1
    - "Play some Arijit Singh songs" → query="Arijit Singh", no_of_songs=5
    - "Play some chill music" → query="chill music", no_of_songs=7

    Args:
        query (str): Song name, artist name, or general music search query.
        no_of_songs (int): Number of songs to fetch and play/queue.

    Returns:
        str: Confirmation showing which songs were played or queued.
    """

    return autoplay_song(query, no_of_songs)
if __name__=="__main__":
    # Example test
    print(play_music("karan aujla"))