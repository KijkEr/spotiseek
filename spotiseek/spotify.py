import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from spotiseek.database import get_downloaded_songs

load_dotenv()
SPOTIFY_SCOPE = "playlist-read-private"
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

spotipy_client = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
    )
)


def get_songs_to_download(playlist_name: str):
    playlist_id = get_playlist_id(playlist_name=playlist_name)
    songs = fetch_playlist_songs(playlist_id=playlist_id)
    downloaded_song_ids = get_downloaded_songs()
    songs = [s for s in songs if s.get("song_id") not in downloaded_song_ids]


def get_playlist_id(playlist_name: str) -> str:
    """Retrieves the Spotify playlist ID for the specified playlist name.

    Returns:
        str: The Spotify playlist ID.
    """
    playlists = spotipy_client.user_playlists("kesselba").get("items")
    for playlist in playlists:
        if playlist.get("name") == playlist_name:
            return playlist.get("id")
    return ""


def fetch_playlist_songs(playlist_id: int) -> list:
    """Fetches songs from the specified Spotify playlist."""
    songs = []
    if playlist_id:
        results = spotipy_client.playlist_tracks(playlist_id=playlist_id).get(
            "items", []
        )
        for item in results:
            track = item.get("track", {})
            songs.append(
                {
                    "artists": [
                        artist.get("name")
                        for artist in track.get("album", {}).get("artists", [])
                    ],
                    "song": track.get("name"),
                    "song_id": track.get("id"),
                }
            )

    return songs
