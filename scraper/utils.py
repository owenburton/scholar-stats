from bs4 import BeautifulSoup
from fuzzywuzzy import process
import pandas as pd
from typing import List

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver


def scrape_scholar_from_url(driver: WebDriver, url: str) -> BeautifulSoup:
    """Scrapes a given scholar profile page by clicking "Show More" button
    until all publications are shown.

    Arguments:
        driver {webdriver class} -- this is to automate the clicking and scraping
        url {string} -- a profile from Google Scholar

    Returns:
        [BeautifulSoup object] -- [nested data structure of the html]
    """
    driver.get(url)
    button_xpath = "/html/body/div/div[13]/div[2]/div/div[4]/form/div[2]/div/button"
    
    # click the "Show More" button until all publications are displayed
    while True:  
        try:
            button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()

        # exit loop when the button is no longer clickable after 2 seconds   
        except TimeoutException:
            break
    
    html = driver.page_source
    page = BeautifulSoup(html, "lxml")

    return page


def get_author_name(page: BeautifulSoup) -> str:
    """Retrieves author's name.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of the html

    Returns:
        str -- author's name
    """
    page_title = page.find("title").string
    author_name = page_title.split(" - ")[0]

    return author_name

def get_author_role(page: BeautifulSoup) -> str:
    """Extracts the researcher's current role from Google Scholar profile page.

    Args:
        page (BeautifulSoup): html of the scraped profile

    Returns:
        str: researcher's current role
    """
    role_list = [div.text for div in page.find_all("div", attrs={"class": "gsc_prf_il"})]

    return role_list[0]


def get_publications_data(page: BeautifulSoup) -> List[dict]:
    pubs_data = []
    for tr in page.find_all("tr", attrs={"class": "gsc_a_tr"}):
        # check if it contains an attribute specific to duplicates
        if tr.find_all("a")[1].has_attr("data-eud"):
            continue
        
        else:
            td1, td2, td3 = tr.find_all("td")
            
            authors = td1.find("div").contents
            if len(authors) < 1:
                continue
            else:
                authors = authors[0].split(", ")
                # authors = [name for name in authors if name!="..."]
            
            citations = td2.find("a").contents
            if len(citations) < 1:
                continue
            else:
                citations = int(citations[0])
                
            year = td3.find("span").contents    
            if len(year) < 1:
                year = None
            else:
                year = int(year[0])
            
            data = {
                "authors": authors, 
                "citations": citations, 
                "year": year
            }
            pubs_data.append(data)
        
    return pubs_data


def get_author_positions_lis(auth_name: str, auth_lists: List[List]) -> List[str]:
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
    author_positions_lis = []

    for names in auth_lists:
        try: 
            matches = process.extract(auth_name, names, limit=2)

            if matches:
                # make sure they're not too far off origianl name
                if matches[0][1] > 74:
                    
                    if len(matches) == 2:
                        # if one's better, take that one
                        if matches[0][1] > matches[1][1]:
                            match = matches[0][0]
                
                        else:
                            full_name_lis = auth_name.split()
                            last_name = full_name_lis.pop()
                            initials = "".join([name[0] for name in full_name_lis])
                            shortened_auth_name = initials + " " + last_name
                            match = process.extractOne(shortened_auth_name, [name[0] for name in matches])[0]
                    else:
                        match = matches[0][0]
                else:
                    match = None
            else:
                match = None
        except TypeError: 
            match = None

        if match:
            for i, author in enumerate(names):
                if author == match:

                    if i == len(names)-1 and i > 2:
                        author_positions_lis.append('last')
                    elif i > 4:
                        author_positions_lis.append('≥6th')
                    else:
                        author_positions_lis.append(ordinal(i+1))
                    break
        else:
            if len(names) > 4:
                author_positions_lis.append('≥6th')
            else:
                author_positions_lis.append(ordinal(len(names)))
    return author_positions_lis


def get_pos_dfs(pos_lis: List[str], num_lis: List[int]) -> dict:
    citations_positions_df = pd.DataFrame(list(zip(pos_lis, num_lis)), columns =['positions', 'citations']) 
    return dict(tuple(citations_positions_df.groupby('positions')))


def get_hindexes(dataframes: dict) -> dict:
    hindexes_dict = {}
    
    for k, df in dataframes.items():
        df.sort_values('citations')
        df = df.reset_index()
        df = df.query('citations >= index')
        # checking if there are no citations
        if df.shape[0] <= 0:
            hindexes_dict[k] = 0
        else:
            hindexes_dict[k] = df.shape[0]

    overall_dict = {}
    for k, df in dataframes.items():
        df.sort_values('citations')
        df.index += 1
        df = df.reset_index()
        df = df.query('citations >= index')
        # checking if there are no citations
        if df.shape[0] <= 0:
            overall_dict[k] = 0
        else:
            overall_dict[k] = df.shape[0]
    overall_hindex = sum(overall_dict.values())
        
    return hindexes_dict, overall_hindex


def get_counts_dicts(pos_lis: List[str], num_lis: List[int]) -> dict:
    d1 = {}
    d2 = {}

    for position, num in zip(pos_lis, num_lis):
        if position in d1:
            d1[position] += 1
            d2[position] += num
        else:
            d1[position] = 1
            d2[position] = num
    return d1, d2