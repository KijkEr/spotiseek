import typer

from spotiseek.database import initialize_database
from spotiseek.soulseek import SoulSeek
from spotiseek.spotify import get_songs_to_download
from spotiseek.audioconverter import AudioConverter

app = typer.Typer()


@app.command()
def init():
    """Initialize the songs.db database."""
    initialize_database()
    print("Created songs.db and tables.")


@app.command()
def download_playlist(playlist_name: str):
    """Download songs from a Spotify playlist."""
    songs = get_songs_to_download(playlist_name=playlist_name)

    sls = SoulSeek()

    sls.download_songs(songs=songs)


@app.command()
def convert_to_mp3():
    """Convert all songs to 320 kbps mp3."""

    audio_converter = AudioConverter()


if __name__ == "__main__":
    app()
