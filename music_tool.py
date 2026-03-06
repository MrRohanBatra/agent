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
    open_browser=True
)

sp = spotipy.Spotify(auth_manager=auth_manager)

def autoplay_song(query):
    # Search for the track
    results = sp.search(q=query, type="track", limit=1)
    
    if not results or not results["tracks"]["items"]:
        return "❌ No song found for that query."
        
    track = results["tracks"]["items"][0]
    track_name = track["name"]
    artist_name = track["artists"][0]["name"]
    track_uri = track["uri"]
    
    # Check for active devices
    devices = sp.devices()
    if not devices or not devices["devices"]:
        return "❌ No active Spotify device found. Please open the Spotify app first."
        
    try:
        # Check the current playback state
        current_playback = sp.current_playback()
        
        # If music is already playing, add to the queue so we don't interrupt
        if current_playback and current_playback.get('is_playing'):
            sp.add_to_queue(track_uri)
            return f"🎵 Added to queue: {track_name} - {artist_name}"
            
        # If nothing is playing, start the playback immediately
        else:
            sp.start_playback(uris=[track_uri])
            return f"🎵 Playing: {track_name} - {artist_name}"
            
    except Exception as e:
        return f"❌ Failed to play/queue song. Error: {str(e)}"

@tool
def play_music(query: str) -> str:
    """
    Play music from Spotify or add to queue based on a search query.

    Use this tool when the user asks to:
    - play a song
    - queue a track
    - listen to music

    The tool searches Spotify for the query. If music is already playing, 
    it adds the track to the queue. If paused, it starts playing immediately.

    Args:
        query (str): Song name, artist name, or music search query.

    Returns:
        str: Confirmation of the song being played or queued.
    """
    return autoplay_song(query)

if __name__=="__main__":
    # Example test
    print(play_music("karan aujla"))