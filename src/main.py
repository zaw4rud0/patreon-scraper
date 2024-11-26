import json
import os
import time

from src.config import Config
from src.driver import init_driver
from src.login import login
from src.scraper import scrape_artist_posts
from src.utils import load_artists


def main():
    Config.validate()

    driver = init_driver()

    try:
        login(driver)

        # Wait a few seconds to allow session to stabilize
        time.sleep(5)

        artists = load_artists(Config.ARTIST_FILE_PATH)
        for artist in artists:
            print(f"Scraping posts for artist: {artist['display_name']} ({artist['url_name']})")
            scrape_artist_posts(driver, artist, Config.OUTPUT_FOLDER)
    finally:
        print("Scraping complete.")


if __name__ == "__main__":
    main()
