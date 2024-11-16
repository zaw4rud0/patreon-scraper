from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def scrape_artist_posts(driver, artist):
    display_name = artist["display_name"]
    url_name = artist["url_name"]

    # Navigate to the artist's page
    url = f"https://www.patreon.com/c/{url_name}/posts"
    print(f"Scraping posts for {display_name}: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//div[@data-tag='post-card']"))
        )

        post_elements = driver.find_elements(By.XPATH, "//div[@data-tag='post-card']")

        # Extract data from each post
        all_posts_data = []
        for post_element in post_elements:
            post_data = extract_post_data(post_element)
            if post_data:
                all_posts_data.append(post_data)

        print(all_posts_data)

        return all_posts_data

    except Exception as e:
        print(f"Error extracting all posts: {e}")
        return []


def extract_post_data(post_element):
    """
    Extracts date, title, text, and tags from a single post element.

    Args:
        post_element (WebElement): The WebElement representing the post.

    Returns:
        dict: A dictionary containing the post's date, title, text, and tags.
    """
    try:
        # Extract title
        title_element = post_element.find_element(By.XPATH, ".//span[@data-tag='post-title']/a")
        title = title_element.text.strip()

        # Extract date
        date_element = post_element.find_element(By.XPATH, ".//a[@data-tag='post-published-at']/span/span")
        date = date_element.text.strip()

        # Extract post text
        paragraph_elements = post_element.find_elements(By.XPATH, ".//div[@class='sc-b20d4e5f-0 jOibYJ']/p") # TODO: Doesn't extract text realiably
        post_text = "\n\n".join(paragraph.text.strip() for paragraph in paragraph_elements).strip()

        # Extract tags
        tag_elements = post_element.find_elements(By.XPATH, ".//a[@data-tag='post-tag']")
        tags = [tag.text.strip() for tag in tag_elements]

        return {
            "title": title,
            "date": date,
            "text": post_text,
            "tags": tags,
        }

    # TODO: Click on Load More button whenever it appears at the end of the page

    except Exception as e:
        print(f"Error extracting post data: {e}")
        return None
