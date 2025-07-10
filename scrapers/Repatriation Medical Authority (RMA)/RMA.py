import requests
from itertools import cycle
from bs4 import BeautifulSoup
import csv
proxies_list = [
    'http://beqcfgqd:zx2ta8sl24bs@176.113.66.110:5791',
    'http://beqcfgqd:zx2ta8sl24bs@66.225.236.89:6118',
    'http://beqcfgqd:zx2ta8sl24bs@94.177.21.47:5416',
    'http://beqcfgqd:zx2ta8sl24bs@85.204.255.7:6422',
    'http://beqcfgqd:zx2ta8sl24bs@64.43.90.225:6740',
    'http://beqcfgqd:zx2ta8sl24bs@82.153.248.29:5405',
    'http://beqcfgqd:zx2ta8sl24bs@145.223.51.147:6680',
    'http://beqcfgqd:zx2ta8sl24bs@150.107.202.103:6720',
    'http://beqcfgqd:zx2ta8sl24bs@172.245.158.37:5990',
]
proxy_pool = cycle(proxies_list)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
}
cookies = {
    "PHPSESSID": "e23c8a9f2fdb24674efffc1493551123"
}

base_url = "http://www.rma.gov.au/"

def get_with_rotating_proxies(base_url, headers, cookies, proxy_pool):
    proxy = next(proxy_pool)
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }
    
    try:
        response = requests.get(base_url, headers=headers, cookies=cookies, proxies=proxy_dict, verify=False)  # `verify=False` is equivalent to `--insecure`
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
def extract_and_write_to_csv(base_url):
    response = get_with_rotating_proxies(base_url, headers, cookies, proxy_pool)

    if response:
        print("Request succeeded!")
        print("Response status code:", response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        with open('RMA.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Section', 'Type', 'Name', 'URL', 'Content'])  
            for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                section = 'Headings'
                type_ = h_tag.name
                name = h_tag.get_text(strip=True)
                url = ''
                content = ''
                writer.writerow([section, type_, name, url, content])
            for p_tag in soup.find_all('p'):
                section = 'Paragraphs'
                type_ = 'p'
                name = ''
                url = ''
                content = p_tag.get_text(strip=True)
                writer.writerow([section, type_, name, url, content])
            for img_tag in soup.find_all('img'):
                section = 'Images'
                type_ = 'img'
                name = img_tag.get('alt', '')
                url = img_tag.get('src', '')
                content = ''
                writer.writerow([section, type_, name, base_url+url, content])
            for a_tag in soup.find_all('a', href=True):
                section = 'Links'
                type_ = 'a'
                name = a_tag.get_text(strip=True)
                url = a_tag['href']
                content = ''
                writer.writerow([section, type_, name, url, content])


    else:
        print("Request failed")
extract_and_write_to_csv(base_url)
