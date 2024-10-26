import sqlite3
from pathlib import Path

# Define the path to the SQLite database file
DATABASE_NAME = "songs.db"


class DatabaseHandler:
    def __init__(self, db_name):
        """Initialize the database handler with the database name."""
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Establish a database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = (
                sqlite3.Row
            )  # Optional: access columns by name
            print("Database connection established.")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """
        Execute a query that modifies the database (INSERT, UPDATE, DELETE).

        :param query: The SQL query to execute.
        :param params: A tuple of parameters to pass to the query.
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            print("Query executed successfully.")
        except sqlite3.Error as e:
            self.connection.rollback()
            print(f"An error occurred: {e}")
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """
        Fetch all results from a SELECT query.

        :param query: The SELECT query to execute.
        :param params: A tuple of parameters to pass to the query.
        :return: A list of sqlite3.Row objects.
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            print("Data fetched successfully.")
            return results
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """
        Fetch a single result from a SELECT query.

        :param query: The SELECT query to execute.
        :param params: A tuple of parameters to pass to the query.
        :return: A single sqlite3.Row object or None.
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            print("Data fetched successfully.")
            return result
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursor.close()

    def __enter__(self):
        """Enable use of 'with' context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the connection is closed when exiting the context."""
        self.close()


def initialize_database():
    """Initializes the SQLite database by executing SQL scripts from the queries/setup/ directory."""
    # Ensure the database directory exists

    # Use a context manager to handle the database connection
    # Define the path to the directory containing SQL scripts
    sql_dir = Path("queries/setup")
    if not sql_dir.exists():
        raise FileNotFoundError(f"The directory {sql_dir} does not exist.")

    # Get all .sql files in the directory, sorted to ensure consistent execution order
    sql_files = sorted(sql_dir.glob("*.sql"))

    if not sql_files:
        raise FileNotFoundError(f"No .sql files found in the directory {sql_dir}.")

    with DatabaseHandler(DATABASE_NAME) as db_handler:
        # Execute each SQL file
        for sql_file in sql_files:
            with sql_file.open("r", encoding="utf-8") as f:
                sql_script = f.read()
                try:
                    db_handler.execute_query(sql_script)
                    print(f"Executed {sql_file.name} successfully.")
                except sqlite3.Error as e:
                    print(f"An error occurred while executing {sql_file.name}: {e}")
                    raise


def get_downloaded_songs() -> set:
    # Use a context manager to handle the database connection
    with DatabaseHandler(DATABASE_NAME) as db_handler:
        downloaded_songs = db_handler.fetch_all("SELECT SongId FROM downloaded_songs")
        song_ids = {row["SongId"] for row in downloaded_songs}

    return song_ids


def insert_downloaded_songs(song_id: int):
    with DatabaseHandler(DATABASE_NAME) as db_handler:
        db_handler.execute_query(
            "INSERT INTO downloaded_songs(SongId) VALUES (?)", (song_id,)
        )
