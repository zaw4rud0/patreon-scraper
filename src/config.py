import json
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """
    A configuration class for managing environment variables and validating file paths.

    This class loads essential configurations from a `.env` file and provides a method
    to validate critical settings such as email, password, and paths for Firefox and
    GeckoDriver binaries. It ensures that all required variables are set and the specified
    paths exist in the file system.
    """
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    FIREFOX_PATH = os.getenv("FIREFOX_PATH")
    GECKO_DRIVER_PATH = os.getenv("GECKO_PATH")
    ARTIST_FILE_PATH = os.getenv("ARTIST_FILE_PATH", os.path.join(PROJECT_ROOT, "artists.json"))
    EXAMPLE_FILE_PATH = os.path.join(PROJECT_ROOT, "artists-example.json")
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", os.path.join(PROJECT_ROOT, "output/"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    REPLACE = os.getenv("REPLACE", "false").lower() == "true"

    @staticmethod
    def validate():
        """
        Validates the configuration settings.
        """
        if not Config.EMAIL or not Config.PASSWORD:
            raise ValueError("EMAIL and PASSWORD must be set in the .env file")

        if not Config.FIREFOX_PATH:
            raise ValueError("FIREFOX_PATH must be specified in the .env file")
        if not os.path.exists(Config.FIREFOX_PATH):
            raise FileNotFoundError(f"FIREFOX_PATH does not exist: {Config.FIREFOX_PATH}")

        if not Config.GECKO_DRIVER_PATH:
            raise ValueError("GECKO_DRIVER_PATH must be specified in the .env file")
        if not os.path.exists(Config.GECKO_DRIVER_PATH):
            raise FileNotFoundError(f"GECKO_DRIVER_PATH does not exist: {Config.GECKO_DRIVER_PATH}")

        Config.ensure_artists_file()

        if not os.path.exists(Config.OUTPUT_FOLDER):
            os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

    @staticmethod
    def ensure_artists_file():
        """
        Ensure `artists.json` exists. If not, create it by copying `artists-example.json`.
        """
        if not os.path.exists(Config.ARTIST_FILE_PATH):
            with open(Config.EXAMPLE_FILE_PATH, "r") as example_file:
                data = json.load(example_file)
            with open(Config.ARTIST_FILE_PATH, "w") as artists_file:
                json.dump(data, artists_file, indent=4)
            print(f"{Config.ARTIST_FILE_PATH} was not found.")
            print(f"A copy of {Config.EXAMPLE_FILE_PATH} has been created as {Config.ARTIST_FILE_PATH}.")
            print(f"Please update {Config.ARTIST_FILE_PATH} with your artist information.")
