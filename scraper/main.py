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
        authors_list = extract_author_names_of_papers(page)
        citations_list = extract_citation_counts(page)

        if len(authors_list)==0 or len(citations_list)==0:
            return jsonify({"message": "No author positions or citations found."})
    except:
        return jsonify({"message": "Could not find author positions or citations."})
    
    try:
        positions, citations = get_metrics(authors_list, citations_list, author_name)
    except:
        return jsonify({"message": "Could not get author metrics."})

    response = {
        "name": author_name, 
        "positions": positions, 
        "citations": citations
        }

    return jsonify(response)

