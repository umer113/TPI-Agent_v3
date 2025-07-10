import requests
from bs4 import BeautifulSoup
from itertools import cycle
import time
import pandas as pd

# ── CONFIG ──────────────────────────────────────────────────────────────────────
BASE_URL     = "https://www.awm.gov.au"
LISTING_PATH = "/articles"

proxies = [
    'http://beqcfgqd:zx2ta8sl24bs@91.217.72.56:6785',
    'http://beqcfgqd:zx2ta8sl24bs@103.37.181.190:6846',
    'http://beqcfgqd:zx2ta8sl24bs@45.43.183.159:6471',
    'http://beqcfgqd:zx2ta8sl24bs@64.137.18.245:6439',
    'http://beqcfgqd:zx2ta8sl24bs@104.238.50.211:6757',
    'http://beqcfgqd:zx2ta8sl24bs@89.249.192.133:6532',
    'http://beqcfgqd:zx2ta8sl24bs@103.101.88.235:5959',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.45.130:6983',
    'http://beqcfgqd:zx2ta8sl24bs@45.38.78.112:6049',
    'http://beqcfgqd:zx2ta8sl24bs@85.204.255.7:6422',
    'http://beqcfgqd:zx2ta8sl24bs@64.43.90.225:6740',
    'http://beqcfgqd:zx2ta8sl24bs@82.153.248.29:5405',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.51.147:6680',
    'http://beqcfgqd:zx2ta8sl24bs@150.107.202.103:6720',
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',
]

proxy_pool = cycle(proxies)

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

# ── HELPERS ────────────────────────────────────────────────────────────────────
def fetch_url(url):
    """Try each proxy in the pool once. Return page text or None if all fail."""
    for _ in range(len(proxies)):
        proxy = next(proxy_pool)
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
            resp.raise_for_status()
            print(f"[OK]  {url}  via {proxy}")
            return resp.text
        except Exception as e:
            print(f"[ERR] {url}  via {proxy}  -> {e}")
    print(f"[FAIL] All proxies failed for {url}")
    return None

# ── STEP 1: PAGINATION TO COLLECT ALL ARTICLE LINKS (ONLY 2 PAGES) ────────────
article_urls = set()

for page in range(1):  # only pages 0 and 1
    if page == 0:
        url = BASE_URL + LISTING_PATH
    else:
        url = f"{BASE_URL}{LISTING_PATH}?page={page}"

    html = fetch_url(url)
    if not html:
        print(f"Stopping early, failed to fetch page {page}")
        break

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="article--card")
    if not cards:
        print(f"No articles found on page {page}, stopping.")
        break

    for card in cards:
        a = card.find("a", href=True)
        if a:
            href = a["href"]
            if href.startswith("/"):
                href = BASE_URL + href
            article_urls.add(href)

    print(f"Page {page}: found {len(cards)} articles, total unique URLs so far: {len(article_urls)}")
    time.sleep(1)

print(f"Total articles to scrape: {len(article_urls)}")

# ── STEP 2: SCRAPE EACH ARTICLE ────────────────────────────────────────────────
records = []
for art_url in article_urls:
    time.sleep(1)
    html = fetch_url(art_url)
    if not html:
        continue

    soup = BeautifulSoup(html, "html.parser")
    # Title
    title_tag = soup.find("span", {"property": "schema:name"})
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Content
    content_div = soup.find("div", class_="paragraphs-item-free-text")
    if content_div:
        parts = content_div.find_all(["div", "p"])
        content = " ".join(p.get_text(" ", strip=True) for p in parts)
    else:
        content = ""

    records.append({
        "url":     art_url,
        "title":   title,
        "content": content,
    })

# ── STEP 3: SAVE TO CSV ────────────────────────────────────────────────────────
df = pd.DataFrame(records)
df.to_csv("articles.csv", index=False, encoding="utf-8-sig")
print("Saved articles.csv")
