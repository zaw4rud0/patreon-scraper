import os
from dotenv import load_dotenv

load_dotenv()


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
