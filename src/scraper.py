def scrape_artist_posts(driver, artist):
    display_name = artist["display_name"]
    url_name = artist["url_name"]

    # Navigate to the artist's page
    url = f"https://www.patreon.com/c/{url_name}/posts"
    print(f"Scraping posts for {display_name}: {url}")
    driver.get(url)
