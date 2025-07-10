import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Selenium WebDriver
def init_driver(driver_path=r"/usr/bin/chromedriver"):  # ← replace with your actual path
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Extract emojis from text
def extract_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return ''.join(emoji_pattern.findall(text))

def append_to_csv(data, filename):
    if not data:
        return
    df = pd.DataFrame(data)
    mode = 'a' if pd.io.common.file_exists(filename) else 'w'
    header = not pd.io.common.file_exists(filename)
    df.to_csv(filename, mode=mode, header=header, index=False)
    print(f"Appended {len(data)} posts to {filename}")

def scrape_tweets(url, filename):
    driver = init_driver()
    try:
        driver.get(url)

        # Wait for initial page load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article[role='article']"))
            )
        except TimeoutException:
            print("Timeout waiting for posts.")
            return []

        tweets_data = []
        seen_tweet_ids = set()
        scroll_count = 0
        max_scrolls = 80
        scroll_pause_time = 8
        last_height = driver.execute_script("return window.pageYOffset")

        while scroll_count < max_scrolls:
            # Use Selenium to find articles for dynamic content
            articles = driver.find_elements(By.CSS_SELECTOR, "article[role='article']")
            print(f"Found {len(articles)} posts on scroll {scroll_count}")
            new_tweets_data = []

            for article in articles:
                try:
                    # Parse article HTML with BeautifulSoup
                    soup = BeautifulSoup(article.get_attribute('outerHTML'), 'html.parser')
                    tweet = soup.find("article", attrs={"role": "article"})

                    # Extract tweet ID (URL of tweet)
                    permalink = tweet.find("a", href=lambda href: href and "/status/" in href)
                    tweet_id = permalink['href'] if permalink else None
                    if not tweet_id:
                        time_elem = tweet.find("time")
                        text_div = tweet.find("div", attrs={"data-testid": "tweetText"})
                        tweet_id = f"{time_elem['datetime']}_{text_div.text[:20]}" if time_elem and text_div else None
                    if not tweet_id or tweet_id in seen_tweet_ids:
                        continue
                    seen_tweet_ids.add(tweet_id)

                    # Extract user name
                    user_name_elem = tweet.find("div", attrs={"data-testid": "User-Name"})
                    user_name = user_name_elem.text.strip() if user_name_elem else ""

                    # Extract timestamp
                    time_elem = tweet.find("time")
                    timestamp = time_elem['datetime'] if time_elem else ""

                    # Extract tweet text
                    text_div = tweet.find("div", attrs={"data-testid": "tweetText"})
                    text = text_div.text.strip() if text_div else ""

                    # Extract emojis from text
                    emojis = extract_emojis(text)

                    # Initialize metrics
                    comments = likes = reposts = 0

                    # try:
                    #     # Wait for metric elements to be visible
                    #     WebDriverWait(driver, 10).until(
                    #         EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[aria-label*='reply'], div[aria-label*='repost'], div[aria-label*='like']"))
                    #     )

                    #     # Comments (Reply)
                    #     comments_elem = article.find_element(By.CSS_SELECTOR, "div[aria-label*='reply']")
                    #     comments_label = comments_elem.get_attribute("aria-label")
                    #     comments_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:Reply|Comment)', comments_label, re.IGNORECASE)
                    #     comments = int(comments_match.group(1).replace(',', '')) if comments_match else 0

                    #     # Reposts (Retweet)
                    #     reposts_elem = article.find_element(By.CSS_SELECTOR, "div[aria-label*='repost']")
                    #     reposts_label = reposts_elem.get_attribute("aria-label")
                    #     reposts_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:Repost|Retweet)', reposts_label, re.IGNORECASE)
                    #     reposts = int(reposts_match.group(1).replace(',', '')) if reposts_match else 0

                    #     # Likes
                    #     likes_elem = article.find_element(By.CSS_SELECTOR, "div[aria-label*='like']")
                    #     likes_label = likes_elem.get_attribute("aria-label")
                    #     likes_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:Like)', likes_label, re.IGNORECASE)
                    #     likes = int(likes_match.group(1).replace(',', '')) if likes_match else 0

                    #     print(f"Comments: {comments}, Reposts: {reposts}, Likes: {likes}")

                    # except NoSuchElementException as e:
                    #     print(f"Metric elements not found: {e}")
                    #     continue
                    # except ValueError as e:
                    #     print(f"Error converting text to integer: {e}")
                    #     continue

                    # Extract image link (if any)
                    image_link = ""
                    image_tag = tweet.find("img", attrs={"alt": "Image"})
                    if image_tag:
                        image_link = image_tag["src"]

                    # Construct tweet URL
                    tweet_url = f"https://x.com{tweet_id}" if tweet_id and "/status/" in tweet_id else ""

                    # Save data to dictionary
                    post_data = {
                        "user_name": user_name,
                        "timestamp": timestamp,
                        "text": text,
                        "emojis": emojis,
                        "comments": comments,
                        "reposts": reposts,
                        "likes": likes,
                        "image_link": image_link,
                        "tweet_url": tweet_url
                    }
                    new_tweets_data.append(post_data)

                except Exception as e:
                    print(f"Error parsing tweet: {e}")
                    continue

            if new_tweets_data:
                append_to_csv(new_tweets_data, filename)
                tweets_data.extend(new_tweets_data)

            # Scroll slightly
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(scroll_pause_time)

            new_height = driver.execute_script("return window.pageYOffset")
            if new_height == last_height:
                print("No new content loaded. Ending scroll.")
                break
            last_height = new_height
            scroll_count += 1

        print(f"Scraped {len(tweets_data)} total posts.")
        return tweets_data

    except Exception as e:
        print(f"Error during scraping: {e}")
        return []

    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://x.com/AWMemorial"  
    filename = 'X AWM.csv'
    tweets = scrape_tweets(url, filename)