# import requests
# from bs4 import BeautifulSoup
# import csv
# import random
# url = "https://www.dva.gov.au/about/our-work-response-royal-commission-defence-and-veteran-suicide"
# proxies_list = [
    # '145.223.51.147:6680',
    # '150.107.202.103:6720',
    # '172.245.158.37:5990',
#     # Add more proxies as needed
# ]

# proxy = random.choice(proxies_list)
# response = requests.get(url,proxies={"http": proxy, "https": proxy})
# if response.status_code != 200:
#     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
#     exit()


# soup = BeautifulSoup(response.content, 'html.parser')
# csv_file = open("scraped_about_pg_data.csv", "w", newline="", encoding="utf-8")
# csv_writer = csv.writer(csv_file)
# csv_writer.writerow(["Section", "Type", "Name", "URL", "Content"])
# links = soup.find_all("a", href=True)
# for link in links:
#     name = link.text.strip()
#     href = link.get("href", "")
#     full_url = requests.compat.urljoin(url, href)  
#     csv_writer.writerow(["Link", "Hyperlink", name, full_url, ""])
# content_sections = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"])
# for section in content_sections:
#     section_name = section.name.upper() 
#     content = section.text.strip()
#     csv_writer.writerow(["Content", section_name, "", url, content])
# images = soup.find_all("img")
# for img in images:
#     img_src = img.get("src", "")
#     img_alt = img.get("alt", "")
#     full_img_url = requests.compat.urljoin(url, img_src)  
#     csv_writer.writerow(["Image", "Image", img_alt, full_img_url, ""])
# csv_file.close()

# print("Scraping completed. Data saved to 'scraped_data.csv'.")






import requests
import random
from itertools import cycle
from bs4 import BeautifulSoup
import csv
proxies_list = [
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',
    'http://beqcfgqd:zx2ta8sl24bs@85.204.255.7:6422',
    'http://beqcfgqd:zx2ta8sl24bs@64.43.90.225:6740',
    'http://beqcfgqd:zx2ta8sl24bs@82.153.248.29:5405',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.51.147:6680',
    'https//beqcfgqd:zx2ta8sl24bs@150.107.202.103:6720',
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',  # duplicate
]

proxies_cycle = cycle(proxies_list)
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "if-modified-since": "Sun, 06 Apr 2025 11:17:35 GMT",
    "if-none-match": "1743938255",
    "priority": "u=0, i",
    "referer": "https://www.dva.gov.au/?page=2",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
}
url = "https://www.dva.gov.au/about/our-work-response-royal-commission-defence-and-veteran-suicide"
def make_request():
    proxy = next(proxies_cycle)
    proxies = {
        "http": proxy,
        "https": proxy
    }
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            print("Request successful!")
            parse_and_store_content(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
def parse_and_store_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    with open("DVA Website About.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header for CSV
        writer.writerow(["Section", "Type", "Name", "URL", "Content"])
        main_content = soup.find_all(['main', 'section', 'article'])
        for section in main_content:
            headings = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                writer.writerow(['Main Content', 'Heading', heading.get_text(strip=True), '', ''])
            links = section.find_all('a')
            for link in links:
                link_text = link.get_text(strip=True)
                link_url = link.get('href', '')
                writer.writerow(['Main Content', 'Link', link_text, link_url, ''])
            paragraphs = section.find_all('p')
            for p in paragraphs:
                writer.writerow(['Main Content', 'Paragraph', 'Paragraph', '', p.get_text(strip=True)])

        images = soup.find_all('img')
        for img in images:
            img_url = img.get('src', '')
            img_alt = img.get('alt', 'No Alt Text')
            writer.writerow(['Main Content', 'Image', img_alt, img_url, ''])
make_request()
