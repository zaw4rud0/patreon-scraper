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
            posts = scrape_artist_posts(driver, artist)
            save_posts_to_file(posts, artist["url_name"])
    finally:
        print("Scraping complete.")


def save_posts_to_file(posts, artist_name):
    # Convert OUTPUT_FOLDER to string to avoid type issues
    output_folder = str(Config.OUTPUT_FOLDER)
    artist_url_name = str(artist_name)

    # Determine the directory and file path
    artist_folder = os.path.join(output_folder, artist_url_name)
    posts_file = os.path.join(artist_folder, "posts.json")

    # Ensure the artist folder exists
    os.makedirs(artist_folder, exist_ok=True)

    # Write posts to the file
    with open(posts_file, "w") as file:
        json.dump(posts, file, indent=4)
    print(f"Saved {len(posts)} posts to {posts_file}")


if __name__ == "__main__":
    main()
