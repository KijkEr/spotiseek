import sqlite3
from pathlib import Path

# Define the path to the SQLite database file
DATABASE_NAME = "songs.db"


def initialize_database():
    """Initializes the SQLite database by executing SQL scripts from the queries/setup/ directory."""
    # Ensure the database directory exists
    db_path = Path(DATABASE_NAME)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Use a context manager to handle the database connection
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Define the path to the directory containing SQL scripts
        sql_dir = Path("queries/setup")
        if not sql_dir.exists():
            raise FileNotFoundError(f"The directory {sql_dir} does not exist.")

        # Get all .sql files in the directory, sorted to ensure consistent execution order
        sql_files = sorted(sql_dir.glob("*.sql"))

        if not sql_files:
            raise FileNotFoundError(f"No .sql files found in the directory {sql_dir}.")

        # Execute each SQL file
        for sql_file in sql_files:
            with sql_file.open("r", encoding="utf-8") as f:
                sql_script = f.read()
                try:
                    cursor.executescript(sql_script)
                    print(f"Executed {sql_file.name} successfully.")
                except sqlite3.Error as e:
                    print(f"An error occurred while executing {sql_file.name}: {e}")
                    raise

        # Commit the changes
        conn.commit()


def get_downloaded_songs() -> set:
    db_path = Path(DATABASE_NAME)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Use a context manager to handle the database connection
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.executescrupt("SELECT SongId FROM downloaded_songs")
        song_ids = {row["SongId"] for row in cursor.fetchall()}
        conn.commit()

    return song_ids
