from ffmpeg import FFmpeg, FFmpegError
import os

import platform
from pathlib import Path


class AudioConverter:
    """
    A class to convert audio files to 320 kbps MP3 format using ffmpeg-python.
    """

    def convert_all_songs(
        self,
    ):
        flac_files = self.get_flac_files()

        for flac_file in flac_files:
            system = platform.system()
            if system == "Windows":
                flac_file = str(flac_file)
                output_file = flac_file.replace(".flac", ".mp3")
            elif system in ("Darwin", "Linux"):
                flac_file = flac_file.as_posix()
                output_file = flac_file.replace(".flac", ".mp3")
            self.convert_to_mp3(input_file=flac_file, output_file=output_file)

    def convert_to_mp3(self, input_file, output_file):
        """
        Converts an audio file to a 320 kbps MP3 file.

        Parameters:
        input_file (str): The path to the input audio file.
        output_file (str): The path where the output MP3 file will be saved.
        """
        print(input_file)
        print(output_file)
        try:
            ffmpeg = (
                FFmpeg()
                .input(input_file)
                .output(
                    output_file,
                    {"b:a": "320k"},
                )
            )
            ffmpeg.execute()
            print(f"Conversion successful: '{output_file}' has been created.")
        except FFmpegError as e:
            print("An error occurred during conversion:", e)

    def get_flac_files(
        self,
    ):
        """
        Retrieves all .flac files from the appropriate slskd directory based on the operating system.

        Returns:
            List[Path]: A list of paths to .flac files.
        """
        system = platform.system()
        if system == "Windows":
            # Get the %LOCALAPPDATA% environment variable
            local_app_data = os.getenv("LOCALAPPDATA")
            if local_app_data is None:
                raise EnvironmentError(
                    "The 'LOCALAPPDATA' environment variable is not set."
                )
            base_dir = Path(local_app_data) / "slskd"
        elif system in ("Darwin", "Linux"):
            # On macOS or Linux
            home_dir = Path.home()
            base_dir = home_dir / "local" / "share" / "slskd"
        else:
            raise NotImplementedError(f"Unsupported operating system: {system}")

        if not base_dir.is_dir():
            raise FileNotFoundError(f"The directory '{base_dir}' does not exist.")

        # Collect all .flac files
        flac_files = list(base_dir.rglob("*.flac"))
        return flac_files
