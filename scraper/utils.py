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
    """Retrieves author's name.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of the html

    Returns:
        str -- author's name
    """
    page_title = page.find("title").string
    author_name = page_title.split(" - ")[0]

    return author_name


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
    authors_list = [text for i,text in enumerate(authors_journals) if i%2==0]

    # make lists of each group of names
    author_lists = [names_str.split(", ") for names_str in authors_list]

    return author_lists


def extract_citation_counts(page):
    """Gets list of citation counts for each publication.

    Arguments:
        page {BeautifulSoup object} -- nested data structure of html

    Returns:
        lsit -- a bunch of integers
    """
    # get citations for each paper 
    citations_list = []
    for td in page.find_all("td", attrs={"class": "gsc_a_c"}):
        citation = td.find("a").contents
        citations_list.append(citation)

    # format citations
    citations_list = [int(c[0]) if len(c)==1 else 0 for c in citations_list]

    return citations_list


def get_author_positions_lis(auth_name, auth_lists):
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
    author_positions_lis = []

    for names in auth_lists:
        match = process.extractOne(auth_name, names)[0]

        for i, author in enumerate(names):
            if author == match:

                if i == len(names)-1 and i > 2:
                    author_positions_lis.append('last')
                else:
                    author_positions_lis.append(ordinal(i+1))
                break
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
            hindexes_dict[k] = df.shape[0] - 1
        
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


# def get_metrics(author_lists, citations_list, author_name):
#     """Produces two dictionaries. Both have author positions as keys and 
#     the 

#     Arguments:
#         author_lists {[type]} -- [description]
    #     citations_list {[type]} -- [description]
    #     author_name {[type]} -- [description]

    # Returns:
    #     [type] -- [description]
    # """
    # author_positions = {}
    # citations_by_author_position = {}

    # for names, c in zip(author_lists, citations_list):
    #     match = process.extractOne(author_name, names)[0]
        
    #     for i, author in enumerate(names):
            
    #         if author == match:
    #             if str(i+1) in author_positions:
    #                 author_positions[str(i+1)] += 1
    #                 citations_by_author_position[str(i+1)] += c

    #             else:
    #                 author_positions[str(i+1)] = 1
    #                 citations_by_author_position[str(i+1)] = c
    #             break

    # return author_positions, citations_by_author_position