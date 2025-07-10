import requests
from itertools import cycle
import time
from bs4 import BeautifulSoup
import csv

# ── CONFIG ──────────────────────────────────────────────────────────────────────
proxies_list = [
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',
    'http://beqcfgqd:zx2ta8sl24bs@85.204.255.7:6422',
    'http://beqcfgqd:zx2ta8sl24bs@64.43.90.225:6740',
    'http://beqcfgqd:zx2ta8sl24bs@82.153.248.29:5405',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.51.147:6680',
    'http://beqcfgqd:zx2ta8sl24bs@150.107.202.103:6720',
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',  # duplicate
]
proxy_cycle = cycle(proxies_list)

requests_data = [
    {
        "url": "https://www.dva.gov.au/about/overview/repatriation-commission/"
               "gwen-cherne-veteran-family-advocate-commissioner/"
               "veteran-family-advocate-commissioner-gwen-cherne",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": ("Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/135.0.0.0 Mobile Safari/537.36")
        },
        "cookies": {
            "monsido": "4081743240673336",
            "_ga_XXXXXXXX": "GS1.1.1743507599.3.0.1743507599.0.0.0",
            "_gid": "GA1.3.1095878290.1743940223",
        }
    }
]

session = requests.Session()

with open('DVA Repatriation Commission.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['URL','Title','Content']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for req in requests_data:
        try:
            # rotate proxy
            proxy = next(proxy_cycle)
            proxies = {"http": proxy, "https": proxy}

            resp = session.get(
                req["url"],
                headers=req.get("headers", {}),
                cookies=req.get("cookies", {}),
                proxies=proxies,
                timeout=10
            )
            resp.raise_for_status()
            print(f"[OK]  Fetched {req['url']} → {resp.status_code} via {proxy}")

            soup = BeautifulSoup(resp.content, 'html.parser')

            # Title from <title>
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ''

            # URL
            url = req["url"]

            # find all matching content divs
            content_divs = soup.find_all(
                'div',
                class_="clearfix text-formatted field field--name-body "
                       "field--type-text-with-summary field--label-hidden field__item"
            )

            if content_divs:
                for idx, div in enumerate(content_divs, start=1):
                    content = div.get_text(separator="\n", strip=True)
                    writer.writerow({
                        'URL':     url,
                        'Title':   title,
                        'Content': content
                    })
            else:
                # No divs found: write a blank row with DivIndex=0
                writer.writerow({
                    'URL':     url,
                    'Title':   title,
                    'Content': ''
                })

            time.sleep(1)  # be kind to the server

        except Exception as e:
            print(f"[ERR] Error fetching {req['url']}: {e}")

session.close()
print("Done. Saved DVA_Repatriation_Commission.csv")
