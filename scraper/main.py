from flask import Flask, request, jsonify
from selenium.webdriver import Chrome, ChromeOptions
import chromedriver_binary
from fuzzywuzzy import fuzz

from utils import *

app = Flask(__name__)

options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1024,768")
options.add_argument("--no-sandbox")

driver = Chrome(chrome_options=options)

example_url = "https://scholar.google.com/citations?user=JicYPdAAAAAJ&hl=en&oi=ao"

@app.route("/", methods=["POST"])
def scrape():
    """route expects a valid Google Scholar profile url, returns stats from that profile"""
    
    url = request.get_json(force=True)["url"]

    if type(url) != str:
        return jsonify({"message": "Given url is not a string."})

    
    if fuzz.ratio(url, example_url) < 50:
        return jsonify({"message": "Given url doesn't look like a scholar profile page."})

    try:
        page = scrape_scholar_from_url(driver, url)
    except:
        return jsonify({"message": "Could not scrape given url."})

    try:
        author_name = get_author_name(page)
    except:
        return jsonify({"message": "Could not find author name."})

    try:
        role = get_author_role(page)
    except:
        return jsonify({"message": "Could not find author's current role."})

    try:
        pubs_data = get_publications_data(page)
    except:
        return jsonify({"message": "Could not extract publications data."})

    try:
        authors_list = [pub["authors"] for pub in pubs_data]
        citations_list = [pub["citations"] for pub in pubs_data]

        if len(authors_list)==0 or len(citations_list)==0:
            return jsonify({"message": "Either no author positions or no citations found."})
    except:
        return jsonify({"message": "Could not get positions or citations."})
    
    try:
        auth_pos_lis = get_author_positions_lis(author_name, authors_list)
    except:
        return jsonify({"message": "Couldn't get author positions list."})

    try:
        dfs = get_pos_dfs(auth_pos_lis, citations_list)
    except:
        return jsonify({"message": "Couldn't get citations by position dataframes."})
    
    try:
        hindexes_dict, overall_hindex = get_hindexes(dfs)
    except:
        return jsonify({"message": "Couldn't get the h-indexes dictionary."})

    try:
        positions, citations = get_counts_dicts(auth_pos_lis, citations_list)
    except:
        return jsonify({"message": "Could not get one of the counts dictionaries."})

    response = {
        "name": author_name,
        "role": role,
        "overall_hindex": overall_hindex,
        "hindexes": hindexes_dict, 
        "positions": positions, 
        "citations": citations
        }

    return jsonify(response)

