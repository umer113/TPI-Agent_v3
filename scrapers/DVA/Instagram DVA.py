import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

CHROME_DRIVER_PATH = "/usr/bin/chromedriver"  # new path in Docker

USERNAME = "dvaausgov"
URL = f"https://www.instagram.com/{USERNAME}/"

options = Options()
options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)
time.sleep(5)

SCROLLS = 2
for _ in range(SCROLLS):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

post_links = set()
for a in driver.find_elements(By.TAG_NAME, "a"):
    href = a.get_attribute("href")
    if "/p/" in href:
        post_links.add(href)

print(f"Found {len(post_links)} post links.")

posts_data = []
for link in list(post_links)[:10]:
    driver.get(link)
    time.sleep(2)
    post_date = ""

    try:
        # Wait for captions (try multiple selectors in order)
        wait = WebDriverWait(driver, 10)

        try:
            post_date = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div._a9zs > span"
            )))
            date = post_date.text
        except:
            spans = driver.find_elements(By.CSS_SELECTOR, "ul li div._a9zr span")
            if spans:
                post_date = spans[0].text
        try:
             
            caption_elem = wait.until(EC.presence_of_element_located((
                By.XPATH,
                '//ul//li//div//div//div[2]//div[1]//h1'
            )))
            caption = caption_elem.text

            likes_elem = wait.until(EC.presence_of_element_located((
                By.XPATH,
                '//section[2]//div//div//span//a//span//span'
            )))
            likes = likes_elem.text

            # Optional: extract post age/date (like '6d')
            date_elem = driver.find_element(By.XPATH, '//time')
            post_date = date_elem.get_attribute("datetime")

        except Exception as e:
            print(f"Error scraping {link}: {e}")
            caption = ""
            likes = ""
            post_date = ""

        posts_data.append({
            "url": link,
            "caption": caption,
            "likes": likes,
            "date": post_date
        })
        print(f"Scraped: {link} -> {caption[:50]} | Likes: {likes} | Date: {post_date}")

    except Exception as e:
        print(f"Error loading caption for {link}: {e}")
        # caption = ""
    

df = pd.DataFrame(posts_data)
df.to_csv(f"Instagram DVA.csv", index=False)
print(f"Saved {len(posts_data)} posts to {USERNAME}_posts.csv")

driver.quit()
# # Login with Instagram credentials (create a throwaway account if needed)
# USERNAME = "notaspect372@gmail.com"
# PASSWORD = "test1001!"
