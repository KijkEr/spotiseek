import ffmpeg
import os


class AudioConverter:
    """
    A class to convert audio files to 320 kbps MP3 format using ffmpeg-python.
    """

    def convert_to_mp3(self, input_file, output_file):
        """
        Converts the input audio file to a 320 kbps MP3 file.

        Parameters:
        - input_file (str): Path to the input audio file.
        - output_file (str): Path where the output MP3 file will be saved.
        """

        # Check if the input file exists
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"The input file '{input_file}' does not exist.")

        try:
            # Use ffmpeg to convert the audio file to 320 kbps MP3
            (
                ffmpeg.input(input_file)
                .output(
                    output_file, acodec="libmp3lame", audio_bitrate="320k", format="mp3"
                )
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"Conversion successful: '{output_file}' has been created.")
        except ffmpeg.Error as e:
            print("An error occurred during conversion:")
            print(e.stderr.decode())
            raise e
