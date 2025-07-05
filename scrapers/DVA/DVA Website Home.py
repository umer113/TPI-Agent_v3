import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin  
from webdriver_manager.chrome import ChromeDriverManager 


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.binary_location = "/usr/bin/chromium"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

# ✅ Use the ChromeDriver path that works inside Docker
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

BASE_URL = "https://clik.dva.gov.au/"

try:
    driver.get("https://clik.dva.gov.au/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    def normalize_url(url):
        if url.startswith('http'):
            return url
        else:
            return urljoin(BASE_URL, url)
    navbar = soup.find('nav')  
    navbar_links = []
    if navbar:
        for a in navbar.find_all('a', href=True):
            name = a.text.strip()
            url = normalize_url(a['href'])
            navbar_links.append({'Section': 'Navbar', 'Type': 'Link', 'Name': name, 'URL': url})
    else:
        print("Navbar not found.")
    footer = soup.find('footer')  
    footer_links = []
    if footer:
        for a in footer.find_all('a', href=True):
            name = a.text.strip()
            url = normalize_url(a['href'])
            footer_links.append({'Section': 'Footer', 'Type': 'Link', 'Name': name, 'URL': url})
    else:
        print("Footer not found.")
    banner = soup.find('div', class_='site-banner-outter bg-with-image')  # Adjust selector if needed
    banner_data = []
    if banner:
        h1_tag = banner.find('h1')
        p_tags = banner.find_all('p')

        if h1_tag:
            banner_data.append({
                'Section': 'Banner',
                'Type': 'H1',
                'Content': h1_tag.get_text(strip=True),
                'URL': ''
            })
        for p in p_tags:
            banner_data.append({
                'Section': 'Banner',
                'Type': 'P',
                'Content': p.get_text(strip=True),
                'URL': ''
            })
    else:
        print("Banner not found.")
    important_notice_h2 = soup.find('h2', string=lambda text: text and 'Important Notice' in text)
    notice_data = []
    if important_notice_h2:
        notice_section = important_notice_h2.find_next('div')
        if notice_section:
            for element in notice_section.find_all(['h2', 'h3', 'p', 'a']):
                if element.name in ['h2', 'h3', 'p']:
                    text = element.get_text(strip=True)
                    links = element.find_all('a')
                    if links:
                        for link in links:
                            normalized_url = normalize_url(link['href'])
                            notice_data.append({
                                'Section': 'Important Notice',
                                'Type': 'Link',
                                'Content': link.text.strip(),
                                'URL': normalized_url
                            })
                    else:
                        notice_data.append({
                            'Section': 'Important Notice',
                            'Type': element.name.upper(),
                            'Content': text,
                            'URL': ''
                        })
                elif element.name == 'a':
                    normalized_url = normalize_url(element['href'])
                    notice_data.append({
                        'Section': 'Important Notice',
                        'Type': 'Link',
                        'Content': element.text.strip(),
                        'URL': normalized_url
                    })
        else:
            print("Important Notice content section not found.")
    else:
        print("Important Notice heading not found.")
    libraries_h2 = soup.find('h2', string='CLIK Libraries')  
    libraries_data = []
    if libraries_h2:
        libraries_section = libraries_h2.find_next('div')
        if libraries_section:
            for element in libraries_section.find_all(['h2', 'h3', 'p', 'a']):
                if element.name in ['h2', 'h3', 'p']:
                    text = element.get_text(strip=True)
                    links = element.find_all('a')
                    if links:
                        for link in links:
                            normalized_url = normalize_url(link['href'])
                            libraries_data.append({
                                'Section': 'CLIK Libraries',
                                'Type': 'Link',
                                'Content': link.text.strip(),
                                'URL': normalized_url
                            })
                    else:
                        libraries_data.append({
                            'Section': 'CLIK Libraries',
                            'Type': element.name.upper(),
                            'Content': text,
                            'URL': ''
                        })
                elif element.name == 'a':
                    normalized_url = normalize_url(element['href'])
                    libraries_data.append({
                        'Section': 'CLIK Libraries',
                        'Type': 'Link',
                        'Content': element.text.strip(),
                        'URL': normalized_url
                    })
        else:
            print("CLIK Libraries content section not found.")
    else:
        print("CLIK Libraries heading not found.")
    images = soup.find_all('img')
    image_data = []
    for img in images:
        src = normalize_url(img.get('src', ''))
        alt = img.get('alt', '')
        image_data.append({
            'Section': 'Images',
            'Type': 'Image',
            'Content': alt,
            'URL': src
        })
    combined_data = (
        navbar_links  + banner_data + notice_data + libraries_data + footer_links + image_data
    )
    df_combined = pd.DataFrame(combined_data)
    df_combined.to_csv('DVA Website Home.csv', index=False)
finally:
    driver.quit()