import json


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
