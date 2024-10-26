# your_project_name/cli.py

import typer
from spotiseek.database import initialize_database
from spotiseek.soulseek import download_song
from spotiseek.spotify import get_songs_to_download

app = typer.Typer()


@app.command()
def init():
    """Initialize the songs.db database."""
    initialize_database()
    print("Created songs.db and tables.")


@app.command()
def download_playlist(playlist_name: str):
    """Initialize the songs.db database."""
    songs = get_songs_to_download(playlist_name=playlist_name)

    download_song(songs=songs)


if __name__ == "__main__":
    app()
