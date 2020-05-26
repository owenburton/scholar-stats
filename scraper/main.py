from flask import Flask, request, jsonify
from selenium.webdriver import Chrome, ChromeOptions
import chromedriver_binary

import utils

app = Flask(__name__)

options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1024,768")
options.add_argument("--no-sandbox")

driver = Chrome(chrome_options=options)


@app.route("/", methods=["POST"])
def scrape():
    """route expects a valid Google Scholar profile url, returns stats from that profile"""
    
    url = request.get_json(force=True)["url"]

    assert type(url)==str

    page = scrape_scholar_from_url(driver, url)

    author_name = get_author_name(page)

    authors_list = extract_author_names_of_papers(page)
    citations_list = extract_citation_counts(page)
    
    positions, citations = get_metrics(authors_list, citations_list, author_name)

    response = {"positions": positions, "citations": citations}

    return jsonify(response)

