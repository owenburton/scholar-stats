from bs4 import BeautifulSoup
from fuzzywuzzy import process
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def scrape_scholar_from_url(driver, url):
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


def get_author_name(page):
    """Retrieves author's name.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of the html

    Returns:
        str -- author's name
    """
    page_title = page.find("title").string
    author_name = page_title.split(" - ")[0]

    return author_name

def get_author_role(page):
    """Extracts the researcher's current role from Google Scholar profile page.

    Args:
        page (BeautifulSoup): html of the scraped profile

    Returns:
        str: researcher's current role
    """
    role_list = [div.text for div in page.find_all("div", attrs={"class": "gsc_prf_il"})]

    return role_list[0]


def extract_author_names_of_papers(page):
    """Gets list of co-authors for each publication.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of html

    Returns:
        list -- groups of names
    """
    # get authors of each paper
    authors_journals = []
    for auth in page.find_all("div", attrs={"class": "gs_gray"}):
        authors_journals.append(auth.text)
        
    # remove extra gs_gray classes found (the journal names)
    authors_list = [text for index, text in enumerate(authors_journals) if index % 2 == 0]

    # make lists of each group of names
    author_lists = [names_str.split(", ") for names_str in authors_list]

    return author_lists


def extract_citation_counts(page):
    """Gets list of citation counts for each publication.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of html

    Returns:
        list -- a bunch of integers
    """
    # get citations for each paper 
    citations_list = []
    for td in page.find_all("td", attrs={"class": "gsc_a_c"}):
        citation = td.find("a").contents
        citations_list.append(citation)

    # format citations
    citations_list = [int(citation[0]) if len(citation)==1 else 0 for citation in citations_list]

    return citations_list


def get_author_positions_lis(auth_name, auth_lists):
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
    author_positions_lis = []

    for names in auth_lists:
        try: 
            match = process.extractOne(auth_name, names, score_cutoff=75)[0]
        except TypeError: 
            match = None

        if match:
            for i, author in enumerate(names):
                if author == match:

                    if i == len(names)-1 and i > 2:
                        author_positions_lis.append('last')
                    elif i > 4:
                        # author_positions_lis.append('6th or more')
                        author_positions_lis.append('≥ 6th')
                    else:
                        author_positions_lis.append(ordinal(i+1))
                    break
        else:
            if len(names) > 4:
                # author_positions_lis.append('6th or more')
                author_positions_lis.append('≥ 6th')
            else:
                author_positions_lis.append(ordinal(len(names)))
    return author_positions_lis


def get_pos_dfs(pos_lis, num_lis):
    citations_positions_df = pd.DataFrame(list(zip(pos_lis, num_lis)), columns =['positions', 'citations']) 
    return dict(tuple(citations_positions_df.groupby('positions')))


def get_hindexes_dict(dataframes):
    hindexes_dict = {}
    
    for k, df in dataframes.items():
        df.sort_values('citations')
        df.index += 1
        df = df.reset_index()
        df = df.query('citations >= index')
        # checking if there are no citations
        if df.shape[0] <= 0:
            hindexes_dict[k] = 0
        else:
            hindexes_dict[k] = df.shape[0]
        
    return hindexes_dict


def get_counts_dicts(pos_lis, num_lis):
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