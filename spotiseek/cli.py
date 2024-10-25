# your_project_name/cli.py

import typer
from spotiseek.database import initialize_database

app = typer.Typer()


@app.command()
def init():
    """Initialize the songs.db database."""
    initialize_database()
    print("Created songs.db and tables.")


@app.command()
def test():
    """Initialize the songs.db database."""
    pass


if __name__ == "__main__":
    app()
