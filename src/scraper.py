from datetime import datetime, timedelta

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def scrape_artist_posts(driver, artist):
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

    all_posts = []
    last_post_count = -1

    try:
        while True:
            # Wait for posts to load
            WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, "//div[@data-tag='post-card']"))
            )

            # Extract all visible post elements
            post_elements = driver.find_elements(By.XPATH, "//div[@data-tag='post-card']")

            # Extract data from the new posts and append to the list
            for post in post_elements:
                post_data = extract_post_data(post)
                if post_data and post_data not in all_posts:
                    all_posts.append(post_data)

            # Break the loop if the number of posts does not change
            if len(post_elements) == last_post_count:
                break
            last_post_count = len(post_elements)

            # Try to click the "Load more" button if present
            try:
                load_more_button = driver.find_element(By.XPATH, "//button[@type='button' and not(@aria-disabled='true') and .//div[text()='Load more']]")
                if load_more_button.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    load_more_button.click()
                    # Allow some time for new posts to load
                    WebDriverWait(driver, 5).until(
                        ec.presence_of_all_elements_located((By.XPATH, "//div[@data-tag='post-card']"))
                    )
                else:
                    break
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                # If the button is not present or clickable, assume all posts are loaded
                break

    except TimeoutException:
        print("Timed out waiting for posts to load.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return all_posts


def wait_for_user_to_dismiss_consent():
    """
    Waits for the user to manually dismiss the consent dialog.
    The user must press Enter to continue the script.
    """
    input("Please dismiss the consent dialog (click the 'Reject non-essential' button) and press Enter to continue...")
    print("Continuing script execution...")


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

        url = get_element_attribute(post_element, ".//span[@data-tag='post-title']/a", "href")
        post_id = url.split("-")[-1]

        return {"id": post_id, "title": title, "date": date, "content": content, "tags": tags, "url": url}

    except StaleElementReferenceException:
        pass
    except Exception:
        pass

    return None


def expand_post_content(post_element):
    """
    Expands the post content if a "Show more" button is present.

    :param post_element: WebElement representing a post.
    :returns: None
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
    :return: str Raw date text or None if not found.
    """
    raw_date = get_element_text(post_element, ".//a[@data-tag='post-published-at']/span/span") or \
               get_element_text(post_element, ".//a[@data-tag='post-published-at']/span")

    print(raw_date)
    return parse_post_date(raw_date)


def parse_post_date(raw_date):
    """
    Parse and normalize the raw post date to the format 'YYYY-MM-DD'.

    :param raw_date: str Raw date text.
    :return: str Date in 'YYYY-MM-DD' format or None if parsing fails.
    """
    if not raw_date:
        return None  # Return None if no date is found

    today = datetime.now()

    try:
        if raw_date.lower() == "today":
            return today.strftime("%Y-%m-%d")
        elif raw_date.lower() == "yesterday":
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "days ago" in raw_date.lower():
            days_ago = int(raw_date.split()[0])
            return (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        elif "hours ago" in raw_date.lower():
            hours_ago = int(raw_date.split()[0])
            return (today - timedelta(hours=hours_ago)).strftime("%Y-%m-%d")
        else:
            # Handle specific dates like "November 26" or "November 26, 2024"
            date_parts = raw_date.split(",")

            if len(date_parts) == 2:
                # Case: "November 26, 2024" (Month Day, Year)
                date_obj = datetime.strptime(raw_date, "%b %d, %Y")
            elif len(date_parts) == 1:
                # Case: "November 26" (Month Day, no Year)
                date_obj = datetime.strptime(raw_date, "%B %d")
                # Assign the current year or adjust for December in January
                if date_obj.month > today.month or (date_obj.month == today.month and date_obj.day > today.day):
                    date_obj = date_obj.replace(year=today.year - 1)
                else:
                    date_obj = date_obj.replace(year=today.year)
            else:
                raise ValueError(f"Unexpected date format: {raw_date}")

            return date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error parsing date '{raw_date}': {e}")
        return None


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
