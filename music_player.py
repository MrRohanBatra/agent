import http.server
import socketserver
import threading
import webbrowser
import urllib.parse
import requests
import spotipy

client_id="2e5953acc6bd47f3a0062b115afbd521"
client_secret="09b641d37621468c85eece61fc2e1976"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

auth_code = None


class CallbackHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        global auth_code

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            auth_code = params.get("code")[0]

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication successful. You can close this tab.")

            threading.Thread(target=httpd.shutdown).start()


def start_server():
    global httpd
    httpd = socketserver.TCPServer(("127.0.0.1", 8888), CallbackHandler)
    httpd.serve_forever()


def get_token():

    url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, data=data)
    return response.json()["access_token"]


def login():

    scope = "user-modify-playback-state user-read-playback-state"

    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )

    webbrowser.open(auth_url)


def search_and_play(token, query):

    sp = spotipy.Spotify(auth=token)

    results = sp.search(q=query, type="track", limit=1)

    track = results["tracks"]["items"][0]

    print("Playing:", track["name"], "-", track["artists"][0]["name"])
    devices = sp.devices()

    if not devices["devices"]:
        print("❌ No Spotify device found. Open Spotify app first.")
        return

    sp.start_playback(uris=[track["uri"]])


if __name__ == "__main__":

    print("Starting callback server...")

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    login()

    server_thread.join()

    token = get_token()

    query = input("Song: ")

    search_and_play(token, query)