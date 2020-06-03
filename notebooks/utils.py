# from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_authors(url):
    authors = None
    try:
        r = requests.get(url, timeout=2)
        
        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            try:
                authors = soup.select_one("#gsc_vcd_table > div:nth-child(1) > div.gsc_vcd_value").text
            except AttributeError:
                authors = None
            
    except Exception as e:
        print(str(e))
        
    finally:
        return authors

def get_authors_list(links_lis):
    with Pool() as p:
        authors_lis = p.map(get_authors, links_lis)
    return authors_lis

zack_url = "https://scholar.google.com/citations?user=X7FY3wUAAAAJ&hl=en&oi=ao"
hinton_url = "https://scholar.google.com/citations?user=JicYPdAAAAAJ&hl=en&oi=ao"
malcolm_url = "https://scholar.google.de/citations?user=bcO-7KwAAAAJ&hl=en&oi=ao"

options = ChromeOptions()
options.headless = True
driver = Chrome(options=options)

button_xpath = "/html/body/div/div[13]/div[2]/div/div[4]/form/div[2]/div/button"

# base_url = malcolm_url
# base_url = zack_url
base_url = hinton_url
driver.get(base_url)
count = 0

while True:  
    try:
        button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()
        count += 1
        print(f"click number: {count}")
        
    except TimeoutException:
        print('not clickable')
        break
        
html = driver.page_source
base_page = BeautifulSoup(html, "lxml")
driver.close()

links = []
for td in base_page.find_all("td", attrs={"class": "gsc_a_t"}):
    link = td.find("a").get("data-href")
    links.append(link)
print("number of publication links found: ", len(links))

# authors_lis = get_authors_list(links)

# print(authors_lis[:50])