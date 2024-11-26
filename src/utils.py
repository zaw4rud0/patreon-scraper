import json
import os
import re

import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime

from src.config import Config


def load_artists(file_path="artists.json"):
    """
    Utility method to load artists from a JSON file.

    :param file_path: Path to the JSON file containing artist data.
    :return: List of artist dictionaries.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Artist file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")


async def download_image(session, url, folder_path):
    """
    Downloads an image from a URL and saves it to a specified folder with the given file name.

    :param session: An aiohttp ClientSession instance.
    :param url: The URL of the image to download.
    :param folder_path: The folder path where the image will be saved.
    :return: The relative path to the downloaded image.
    """
    folder_path.mkdir(parents=True, exist_ok=True)

    try:
        async with session.get(url) as response:
            if response.status == 200:
                content_disposition = response.headers.get("Content-Disposition")
                if content_disposition:
                    match = re.search(r'filename="([^"]+)"', content_disposition)
                    if match:
                        file_name = match.group(1)
                    else:
                        raise ValueError("Filename not found in Content-Disposition header.")
                else:
                    raise ValueError("Content-Disposition header is missing.")

                file_path = folder_path / file_name

                if file_path.exists():
                    # If the file already exists, skip downloading
                    return str(file_path.relative_to(Config.OUTPUT_FOLDER))

                with open(file_path, "wb") as f:
                    f.write(await response.read())
                return str(file_path.relative_to(Config.OUTPUT_FOLDER))
            else:
                print(f"Failed to download {url}: {response.status}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None


async def store_post_images(posts):
    """
    Stores images for posts asynchronously and updates their image attributes.

    :param posts: A list of post dictionaries with a 'date' and 'images' attribute.
    :return: The list of posts with updated 'images' attributes.
    """
    async with aiohttp.ClientSession() as session:
        tasks = []

        for post in posts:
            post_date = datetime.strptime(post["date"], "%Y-%m-%d")
            year = post_date.year
            month = f"{post_date.month:02d}"

            folder_path = Path(Config.OUTPUT_FOLDER) / "images" / str(year) / str(month)
            for url in post["images"]:
                tasks.append(download_image(session, url, folder_path))

        # Gather all results
        downloaded_paths = await asyncio.gather(*tasks)

        # Update post 'images' attributes
        index = 0
        for post in posts:
            updated_images = []
            for _ in post["images"]:
                relative_path = downloaded_paths[index]
                if relative_path:
                    updated_images.append(relative_path)
                index += 1
            post["images"] = updated_images

    return posts


def save_posts_to_file(posts, artist_name: str, output_folder):
    """
    Save posts to a JSON file for the given artist by appending new data to existing data.

    :param posts: List of post dictionaries.
    :param artist_name: The artist's name.
    :param output_folder: Path to the base output folder.
    """
    artist_folder = os.path.join(output_folder, artist_name)
    posts_file = os.path.join(artist_folder, "posts.json")

    os.makedirs(artist_folder, exist_ok=True)

    existing_posts = []

    # Load existing posts if the file exists
    if os.path.exists(posts_file):
        with open(posts_file, "r") as file:
            try:
                existing_posts = json.load(file)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {posts_file}, starting fresh.")

    # Append only new posts (based on unique ID)
    existing_post_ids = {post["id"] for post in existing_posts}
    new_posts = [post for post in posts if post["id"] not in existing_post_ids]
    updated_posts = existing_posts + new_posts

    # Save the updated list of posts
    with open(posts_file, "w") as file:
        json.dump(updated_posts, file, indent=4)
    print(f"Appended {len(new_posts)} new posts to {posts_file}")
