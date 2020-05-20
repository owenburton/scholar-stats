import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from fuzzywuzzy import process


def scrape_scholar_from_url(url):
    content = requests.get(url).text
    page = BeautifulSoup(content, "lxml")
    return page

def get_author_name(page):
    page_title = page.find("title").string
    author_name = page_title.split(" - ")[0]
    return author_name

def extract_author_names_of_papers(page):
    # get authors & journal names
    # remove journal names (every other item)
    authors_list = [x.text for i, x in enumerate(page.findall("div", attrs={"class": "gs_gray"})) if i%2==0]
    return authors_list

def get_author_positions(authors_list, author_name):
    authors_lists = [names_str.split(", ") for names_str in authors_list]
    author_positions = {}

    for names_list in authors_lists:
        match = process.extractOne(author_name, names_list)[0]

        for i, author in enumerate(names_list):

            if author == match:
                if str(i+1) in author_positions:
                    author_positions[str(i+1)] += 1
                else:
                    author_positions[str(i+1)] = 1
                break
    return author_positions

def order_author_positions(author_positions):
    return OrderedDict(sorted(author_positions.items()))