import logging
import logging.config
import time

import yaml
from requests.exceptions import HTTPError
from slskd_api import SlskdClient
from thefuzz import fuzz

from spotiseek.database import insert_downloaded_songs

with open("./spotiseek/logging.yml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger("spotiseek")

API_HOST = "http://localhost:5030"
SLSKD_API_KEY = "EGkiYvu5H#r&#j%Pa3o2"


class SoulSeek:
    def __init__(self) -> None:
        self.slskd = SlskdClient(API_HOST, SLSKD_API_KEY)

    def download_songs(self, songs: list):
        for song in songs:
            self.download_song(song=song)

    def download_song(self, song: dict):
        """Attempts to download a song by finding the best match on Soulseek.

        Args:
            cur: The SQLite database cursor for recording the download.
            song (dict): The song dictionary containing details for the download.
        """
        match_parameters = [
            {"file_extension": "mp3", "bit_rate_target": 320},
            {"file_extension": "flac", "bit_rate_target": 0},
            {"file_extension": "mp3", "bit_rate_target": 0},
        ]
        for params in match_parameters:
            try:
                responses = self.get_responses(song)
                if not responses:
                    continue  # Skip if no responses
                matching_file = self.get_best_matching_song(
                    file_extension=params["file_extension"],
                    bit_rate_target=params["bit_rate_target"],
                    match_string=f"{song.get('song')} {' '.join(song.get('artists'))}",
                    responses=responses,
                )
                if matching_file:
                    files, username, _ = matching_file
                    self.slskd.transfers.enqueue(username=username, files=[files])
                    logger.info(f"Downloading: {files.get('filename')}")
                    # Insert into DB
                    insert_downloaded_songs(song.get("song_id"), song.get("song"))
                    logger.info(
                        f"Finished downloading: {song.get('song')} {' '.join(song.get('artists'))}"
                    )

                    break
            except IndexError:  # More specific error handling can be added here
                logger.info(
                    f"Did not find: {song.get('song')} {' '.join(song.get('artists'))}. Trying again."
                )
                continue
            except (
                HTTPError
            ) as e:  # Properly handle HTTP errors from the Soulseek client
                logger.info(f"HTTP error occurred: {e}")

    def get_responses(self, song: dict) -> dict:
        """Initiates a search on Soulseek for the given song and waits for search completion.

        Args:
            song (dict): The song dictionary containing 'song' and 'artists' keys.
        """
        search_text = f"{song.get('song')} {' '.join(song.get('artists'))}"
        logger.info(f"Starting download of: {search_text}")
        search_id = self.slskd.searches.search_text(searchText=search_text).get("id")
        state = self.slskd.searches.state(id=search_id).get("state")
        while "Completed" not in state:
            time.sleep(5)
            state = self.slskd.searches.state(id=search_id).get("state")
        responses = self.slskd.searches.search_responses(id=search_id)

        return responses

    def get_best_matching_song(
        self,
        file_extension: str,
        bit_rate_target: int,
        match_string: str,
        responses: dict,
    ) -> dict:
        """Finds the best matching song file from Soulseek responses based on criteria.

        Args:
            file_extension (str): Desired file extension (e.g., 'mp3').
            bit_rate_target (int): Minimum desired bit rate.
            match_string (str): The search string to match against filenames.
        """
        filtered_responses = [s for s in responses if s.get("fileCount", 0) >= 1]
        matching_files = []
        for user in filtered_responses:
            for file in user["files"]:
                if (
                    file_extension in file["filename"].lower()
                    and file.get("bitRate", 0) >= bit_rate_target
                ):
                    ratio = fuzz.ratio(file["filename"].lower(), match_string.lower())
                    matching_files.append((file, user.get("username"), ratio))
        matching_file = (
            sorted(matching_files, key=lambda x: x[-1], reverse=True)[0]
            if matching_files
            else None
        )

        return matching_file
