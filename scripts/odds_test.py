from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.headless = True
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
driver = webdriver.Chrome(options=options)

def setup_driver():
    """Set up Selenium WebDriver."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment if you don't want the browser to open up
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_sport_event(url):
    """Scrape sport event details."""
    driver = setup_driver()
    driver.get(url)
    
    # Wait for the dynamic content to load
    time.sleep(5)  # Adjust based on the page's loading time
    
    # Locate and extract participant names and other details
    participants = driver.find_elements(By.CSS_SELECTOR, ".participants .participant-vertical")
    for participant in participants:
        # Extract and print team name and other details
        team_name = participant.find_element(By.CSS_SELECTOR, ".show-for-medsmall").text
        print(f"Team Name: {team_name}")
    
    # Extract additional information as needed
    # Example: Betting odds
    odds = driver.find_elements(By.CSS_SELECTOR, ".selection-odds")
    for odd in odds:
        print(f"Odds: {odd.text}")
    
    # Clean up
    driver.quit()

if __name__ == "__main__":
    url = 'https://app.hardrock.bet/sport-leagues/ice_hockey/691036012789334019'
    scrape_sport_event(url)
