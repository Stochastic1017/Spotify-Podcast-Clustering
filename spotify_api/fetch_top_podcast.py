import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import csv

def setup_webdriver(download_dir):
    """Sets up and returns a WebDriver instance with download directory configured."""
    try:
        geckodriver_path = "/home/stochastic1017/.wdm/drivers/geckodriver/linux64/v0.35.0/geckodriver"
        service = FirefoxService(executable_path=geckodriver_path)
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
        options.set_preference("pdfjs.disabled", True)
        
        driver = webdriver.Firefox(service=service, options=options)
        return driver
    except Exception as e:
        raise Exception(f"Failed to setup WebDriver: {str(e)}")

def extract_podcast_data(driver, genre):
    """Extracts podcast details including name, publisher, ID, and image for the given genre."""
    data = []
    try:
        podcasts = driver.find_elements(By.CLASS_NAME, "Show_show__jq9gl")
        for podcast in podcasts:
            try:
                name_element = podcast.find_element(By.CSS_SELECTOR, "div.w-full div.text-accent0 span span")
                publisher_element = podcast.find_element(By.CSS_SELECTOR, "div.w-full.text-white.uppercase.text-left.font-light span span")
                follow_link = podcast.find_element(By.CSS_SELECTOR, "a[href*='open.spotify.com/show']")

                podcast_name = name_element.text.strip()
                podcast_publisher = publisher_element.text.strip()
                podcast_link = follow_link.get_attribute("href")
                podcast_id = podcast_link.split("/")[-1]
                
                data.append({
                    "podcast_genre": genre,
                    "podcast_name": podcast_name,
                    "podcast_publisher": podcast_publisher,
                    "podcast_id": podcast_id,
                })
            except Exception as inner_e:
                print(f"Error extracting data for one podcast: {inner_e}")
    except Exception as e:
        print(f"Error extracting podcast data for genre '{genre}': {e}")
    return data

# Main Script
download_dir = "/home/stochastic1017/Downloads"
driver = setup_webdriver(download_dir)
driver.get("https://podcastcharts.byspotify.com/")
all_genre = [
    "Arts", "Business", "Comedy", "Education", "Fiction", "Health & Fitness",
    "History", "Leisure", "Music", "News", "Religion & Spirituality", "Science", 
    "Society & Culture", "Sports", "Technology", "True Crime", "TV & Film"
]

print("\nExtracting podcast data by genre...\n")
genre_podcast_data = []

try:
    # Locate and click on the dropdown
    dropdown = driver.find_element(By.ID, "categoryDropdown")
    driver.execute_script("window.scrollBy(0, -150); arguments[0].scrollIntoView({block: 'center'});", dropdown)
    time.sleep(2)
    dropdown.click()
    time.sleep(2)

    # Loop through each genre
    for genre in all_genre:
        try:
            # Select genre from dropdown
            genre_option = driver.find_element(By.XPATH, f"//span[text()='{genre}']")
            genre_option.click()
            print(f"Selected genre: {genre}")
            time.sleep(1)  # Wait for the page to load

            # Extract data for the selected genre
            data = extract_podcast_data(driver, genre)
            genre_podcast_data.extend(data)

            # Reopen the dropdown for the next genre
            dropdown.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error processing genre '{genre}': {e}")

finally:
    driver.quit()

# Output the collected data
output_file = "top_podcasts_all_genre.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["podcast_genre", "podcast_name", "podcast_publisher", "podcast_id"])
    writer.writeheader()
    writer.writerows(genre_podcast_data)

print(f"\nData saved to {output_file}")
