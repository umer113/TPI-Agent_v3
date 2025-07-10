import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Common request headers
common_headers = {
    "sec-ch-ua-platform": "Android",
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0"
        " Mobile Safari/537.36"
    ),
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?1",
}

# Common cookies (use as-is or update with fresh values)
common_cookies = {
    "_gid": "GA1.3.1046864615.1743240670",
    "monsido": "4081743240673336",
    "_ga_XXXXXXXX": "GS1.1.1743243185.2.1.1743244433.0.0.0",
    "bm_mi": "3C2F88576EB2B1328DF4957982B85D2D~YAAQvvzUF1LjGqOVAQAAWGSd6Bth1EnnrqM/55ra+zZ0CT0o/"
             "5KLuglk/gQSB7kCoLjQwgCbOP906LWlWZpl4fyxcq+yuzGM8msirSFwu1nYdAotFYTHknHGqft33p+"
             "DMIqxmyzvdQzeuYdus7Xtt+oHgGiH8SCgPKX1NtMBWZW5lrG7FfXOfvaS8Odl3AA6lUi25CyUP+fK7"
             "uNQhboYal3H0DmCqbBPi5mqlDApqeGHtAMdQKrVixy2OwbwEhSMMuabDb2ibFZ+tu0ohB4YO1xQHwc"
             "FgoOG6YNswq0nSqtQBryENbhxkjofmazHpE8JywMoO2eWWQm3Txnd52nHkh6EaeI=~1",
    "_gat_gtag_UA_129191797_1": "1",
    "_gat_gtag_UA_67990327_1": "1",
    "_ga_MN793G4JHJ": "GS1.1.1743364571.3.0.1743364571.0.0.0",
    "_ga_FT6SLY9TWT": "GS1.1.1743364376.9.1.1743364574.0.0.0",
    "_ga_0XT7NFV9ZS": "GS1.1.1743364376.9.1.1743364574.0.0.0",
    "bm_sv": "AF7F1D971ACA5FD425CC7DC6D72B9CBC~YAAQvvzUF3PjGqOVAQAAJqGg6Buy7dRTKosyL4YNrqYTl"
             "oJ4Bouxg3EjnJ3fZ0HOiZaZW6nbfsodMC9h0XpffP79Cs0AxpmAR4zH0aL3GIeC4Rhi7ozMlQBhupO"
             "lz+hXJ55VeO7KgaJtW6ym4VjIN/7yh4uk68j3bp+0VK+4ZudN6dkpyRXhfBQXhrNWcT96qjllYRrY"
             "EZ6ZZbPI34HZcdPfFJ0xtuu1BJcV0TFWPeeBL7e3zGyCiwLzvkpECEXA~1",
    "_ga": "GA1.1.1075414505.1743240668",
}

proxies_list = [
    'http://beqcfgqd:zx2ta8sl24bs@91.217.72.56:6785',
    'http://beqcfgqd:zx2ta8sl24bs@103.37.181.190:6846',
    'http://beqcfgqd:zx2ta8sl24bs@45.43.183.159:6471',
    'http://beqcfgqd:zx2ta8sl24bs@64.137.18.245:6439',
    'http://beqcfgqd:zx2ta8sl24bs@104.238.50.211:6757',
    'http://beqcfgqd:zx2ta8sl24bs@89.249.192.133:6532',
    'http://beqcfgqd:zx2ta8sl24bs@103.101.88.235:5959',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.45.130:6983',
    'http://beqcfgqd:zx2ta8sl24bs@45.38.78.112:6049',

]
# List of proxies to rotate through
def get_html(url):
    """
    Attempt to fetch `url` using each proxy in turn.
    Returns the `requests.Response` on success or None if all proxies fail.
    """
    for proxy in proxies_list:
        try:
            resp = requests.get(
                url,
                headers=common_headers,
                cookies=common_cookies,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
            if resp.status_code == 200:
                return resp
            else:
                print(f"[{proxy}] Status {resp.status_code} for {url}")
        except Exception as e:
            print(f"[{proxy}] Error fetching {url}: {e}")
    print(f"All proxies failed for {url}")
    return None

def parse_listing_page(listing_url):
    """
    Fetch listing page and extract article-relative URLs from
    each <a class="card"> inside <div class="col-md-6"> blocks.
    """
    resp = get_html(listing_url)
    if not resp:
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    hrefs = []
    for div in soup.find_all('div', class_='col-md-6'):
        a = div.find('a', class_='card')
        if a and a.get('href'):
            hrefs.append(a['href'])
    return hrefs

def parse_article(path):
    """
    Given a relative article path, fetch full page and extract:
      - url: absolute URL
      - title: text of the <h1> inside .field--name-node-title
      - content: text inside the specific body selector
    """
    base = "https://www.dva.gov.au"
    full_url = urljoin(base, path)
    resp = get_html(full_url)
    if not resp:
        return full_url, None, None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # 1. Title
    title = ""
    title_div = soup.find('div', class_='field--name-node-title')
    if title_div:
        h1 = title_div.find('h1')
        title = h1.get_text(strip=True) if h1 else title_div.get_text(strip=True)

    # 2. Content: using the complete class selector

    blocks = soup.find_all(
        "div",
        class_="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item"
    )

    # you said you want the 4th one (index 3)
    if len(blocks) > 3:
        content_div = blocks[3]

        # get _all_ text inside it (paras, lists, links, etc)
        # `separator` controls what string goes between tags
        full_text = content_div.get_text(separator="\n", strip=True)

        content = full_text
    else:
        content = ""
        
    return full_url, title, content

def main():
    urls = [
        "https://www.dva.gov.au/about/news/vetaffairs",
        "https://www.dva.gov.au/about/news/vetaffairs?page=1"
    ]

    csv_filename = 'DVA Veteran Affairs.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['url', 'title', 'content'])
        writer.writeheader()

        for listing_url in urls:
            print(f"Processing listing: {listing_url}")
            article_paths = parse_listing_page(listing_url)

            for path in article_paths:
                full_url, title, content = parse_article(path)
                if title is None:
                    print(f"  → Skipped (failed to fetch): {full_url}")
                    continue

                writer.writerow({
                    'url': full_url,
                    'title': title,
                    'content': content
                })
                print(f"  → Saved article: {full_url}")

if __name__ == "__main__":
    main()
