import asyncio
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from src.date_utils import parse_date
from src.utils import store_post_images, save_posts_to_file


def scrape_artist_posts(driver, artist, output_folder):
    """
    Scrape posts from an artist's Patreon page, including loading more posts until the end.
    Handles consent modals or other obstructing elements.

    :param driver: Selenium WebDriver instance.
    :param artist: dict containing artist information with 'display_name' and 'url_name' keys.
    :returns: A list of dictionaries, each representing a post's data.
    """
    url_name = artist["url_name"]

    url = f"https://www.patreon.com/c/{url_name}/posts"
    driver.get(url)

    wait_for_user_to_dismiss_consent()

    unique_post_ids = set()
    last_post_count = -1

    try:
        while True:
            new_posts = []

            # Wait for posts to load
            WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, "//div[@data-tag='post-card']"))
            )

            # Extract all visible post elements
            post_elements = driver.find_elements(By.XPATH, "//div[@data-tag='post-card']")

            # Extract data from the new posts and append to the list
            for post in post_elements:
                post_data = extract_post_data(post)
                if post_data and post_data["id"] not in unique_post_ids:
                    unique_post_ids.add(post_data["id"])
                    new_posts.append(post_data)

            new_posts = asyncio.run(store_post_images(new_posts))
            save_posts_to_file(new_posts, artist["url_name"], output_folder)

            # Break the loop if the number of posts does not change
            if len(unique_post_ids) == last_post_count:
                break
            last_post_count = len(unique_post_ids)

            if not click_load_more(driver):
                break
    except TimeoutException:
        print("Timed out waiting for posts to load.")
    except Exception as e:
        print(f"An error occurred: {e}")


def wait_for_user_to_dismiss_consent():
    """
    Waits for the user to manually dismiss the consent dialog.
    The user must press Enter to continue the script.
    """
    input("Please dismiss the consent dialog (click the 'Reject non-essential' button) and press Enter to continue...")
    print("Continuing script execution...")


def click_load_more(driver):
    """
    Clicks the "Load more" button if it exists and is clickable.

    :param driver: Selenium WebDriver instance.
    :return: True if the button was clicked, False otherwise.
    """
    try:
        initial_post_count = len(driver.find_elements(By.XPATH, "//div[@data-tag='post-card']"))

        load_more_button = driver.find_element(By.XPATH,
                                               "//button[@type='button' and not(@aria-disabled='true') and .//div[text()='Load more']]")
        if load_more_button.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            load_more_button.click()

            # Wait for the number of posts to increase
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//div[@data-tag='post-card']")) > initial_post_count
            )
            return True
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
        pass
    return False


def extract_post_data(post_element):
    """
    Extracts data from a single post element.

    :param post_element: WebElement representing a post.
    :returns: A dictionary containing the post's title, date, text, and tags, or None if extraction fails.
    """
    try:
        expand_post_content(post_element)

        title = get_element_text(post_element, ".//span[@data-tag='post-title']/a")
        date = extract_post_date(post_element)
        content = extract_post_text(post_element)
        tags = extract_post_tags(post_element)

        images = extract_image_urls(post_element)

        url = get_element_attribute(post_element, ".//span[@data-tag='post-title']/a", "href")
        post_id = url.split("-")[-1]

        return {"id": post_id, "title": title, "date": date, "content": content, "images": images, "tags": tags, "url": url}

    except StaleElementReferenceException:
        pass
    except Exception:
        pass

    return None


def expand_post_content(post_element):
    """
    Expands the post content if a "Show more" button is present.

    :param post_element: WebElement representing a post.
    """
    try:
        show_more_button = post_element.find_element(By.XPATH, ".//button[contains(text(), 'Show more')]")
        if show_more_button.is_displayed():
            for _ in range(2):
                try:
                    show_more_button.click()
                    WebDriverWait(post_element, 5).until(
                        ec.presence_of_all_elements_located(
                            (By.XPATH, ".//div[@class='sc-b20d4e5f-0 jOibYJ']/p")
                        )
                    )
                    return
                except TimeoutException:
                    continue
                except ElementClickInterceptedException:
                    continue
    except NoSuchElementException:
        pass


def get_element_text(parent, xpath):
    """
    Retrieves text content from a child element of the given parent.

    :param parent: Parent WebElement.
    :param xpath: str XPath to locate the child element.
    :returns: str Text content of the element or an empty string if not found.
    """
    try:
        element = parent.find_element(By.XPATH, xpath)
        return element.text.strip()
    except NoSuchElementException:
        return ""


def extract_post_date(post_element):
    """
    Extract the raw post date text from the post element.

    :param post_element: WebElement representing a post.
    :return: str The date or None if not found.
    """
    raw_date = get_element_text(post_element, ".//a[@data-tag='post-published-at']/span/span") or \
               get_element_text(post_element, ".//a[@data-tag='post-published-at']/span")

    return parse_date(raw_date)


def get_element_attribute(parent, xpath, attribute):
    """
    Retrieves an attribute value from a child element of the given parent.

    :param parent: Parent WebElement.
    :param xpath: str XPath to locate the child element.
    :param attribute: str The attribute to retrieve (e.g., 'href').
    :returns: str Attribute value or an empty string if not found.
    """
    try:
        element = parent.find_element(By.XPATH, xpath)
        return element.get_attribute(attribute)
    except NoSuchElementException:
        return ""


def extract_post_text(post_element):
    """
    Extracts the text content from a post.

    :param post_element: WebElement representing a post.
    :returns: str Combined text content from all paragraphs.
    """
    paragraphs = post_element.find_elements(By.XPATH, ".//div[@class='sc-b20d4e5f-0 jOibYJ']/p")
    return "\n".join(paragraph.text.strip() for paragraph in paragraphs)


def extract_post_tags(post_element):
    """
    Extracts tags from a post.

    :param post_element: WebElement representing a post.
    :returns: list A list of tag strings.
    """
    tags = post_element.find_elements(By.XPATH, ".//a[@data-tag='post-tag']")
    return [tag.text.strip() for tag in tags]


def extract_image_urls(post_element):
    """
    Extracts image URLs from a post.

    :param post_element: WebElement representing a post.
    :returns: list A list of image URLs or an empty list if none are found.
    """
    try:
        # Find all image elements inside the image grid
        image_elements = post_element.find_elements(By.XPATH, ".//div[contains(@class, 'image-grid')]//img")

        # Extract the 'src' attribute of each image element
        image_urls = [img.get_attribute("src") for img in image_elements]
        return image_urls
    except NoSuchElementException:
        return []
