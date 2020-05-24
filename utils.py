from bs4 import BeautifulSoup
from collections import OrderedDict
from fuzzywuzzy import process

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def scrape_scholar_from_url(driver, url):
    driver.get(url)
    button_xpath = "/html/body/div/div[13]/div[2]/div/div[4]/form/div[2]/div/button"
    
    while True:  
        try:
            button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()
            
        except TimeoutException:
            break

    html = driver.page_source
    page = BeautifulSoup(html, "lxml")

    return page

def get_author_name(page):
    page_title = page.find("title").string
    author_name = page_title.split(" - ")[0]

    return author_name

def extract_author_names_of_papers(page):
    # get authors of each paper
    authors_journals = []
    for auth in page.find_all("div", attrs={"class": "gs_gray"}):
        authors_journals.append(auth.text)
        
    # remove extra gs_gray classes found (the journal names)
    authors_list = [text for i,text in enumerate(authors_journals) if i%2==0]

    # make lists of each group of names
    author_lists = [names_str.split(", ") for names_str in authors_list]

    return author_lists

def extract_citation_counts(page):
    # get citations for each paper 
    citations_list = []
    for td in page.find_all("td", attrs={"class": "gsc_a_c"}):
        citation = td.find("a").contents
        citations_list.append(citation)

    # format citations
    citations_list = [int(c[0]) if len(c)==1 else None for c in citations_list]

    return citations_list


def get_metrics(author_lists, citations_list, author_name):
    author_positions = {}
    citations_by_author_position = {}

    for names, c in zip(author_lists, citations_list):
        match = process.extractOne(author_name, names)[0]
        
        for i, author in enumerate(names):
            
            if author == match:
                if str(i+1) in author_positions:
                    author_positions[str(i+1)] += 1
                    if c:
                        citations_by_author_position[str(i+1)] += c

                else:
                    author_positions[str(i+1)] = 1
                    if c:
                        citations_by_author_position[str(i+1)] = c
                break

    return author_positions, citations_by_author_position

def order_stuff(dct):
    return OrderedDict(sorted(dct.items()))

def order_dicts(dict1, dict2):
    return order_stuff(dict1), order_stuff(dict2)