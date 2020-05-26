import streamlit as st
import pandas as pd

from utils import *

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# TODO:
# write description of the app
# insert a gif of how it works
# add titles to the graphs
# add author picture
# add in a slider to sort by year
# have them just type in a name, then choose one from dropdown
# summarize most impactful work (T5 summarization)
# add a cache of scholar data for fast lookups

# to deploy: you could just deploy the frontend streamlit on whatever works, and 
# hit your scraping api that's on cloud run: https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp

options = Options()
options.headless = True
driver = Chrome(options=options)

st.title("Scholar Stats")

st.write(
    """
    Scholar Stats makes it easier to gauge a researcher's contributions.\n

    While [Google Scholar](https://scholar.google.com/citations?user=JicYPdAAAAAJ&hl=en&oi=ao) provides summary metrics that are often used in hiring, 
    promotions, and other important decisions, those metrics don't give a full picture of that person's contributions
    to their field. Scholar Stats improves upon those Scholar profiles by layering in the 
    researcher's individual level of work for each of their  publications.
    """
    )

example_url = "https://scholar.google.co.uk/citations?hl=en&user=JicYPdAAAAAJ"
url = st.text_input(
    "copy/paste the url of a scholar profile from google scholars",
    example_url)

if url:
    page = scrape_scholar_from_url(driver, url)

    author_name = get_author_name(page)
    st.text(author_name)

    authors_list = extract_author_names_of_papers(page)
    citations_list = extract_citation_counts(page)
    
    positions, citations = get_metrics(authors_list, citations_list, author_name)
    ordered_positions, ordered_citations = order_dicts(positions, citations)

    positions1 = list(ordered_citations.keys())
    citation_counts = list(ordered_citations.values())

    positions2 = list(ordered_positions.keys())
    position_counts = list(ordered_positions.values())

    citations_df = pd.DataFrame({
        "position": positions1,
        "citations": citation_counts
    })

    positions_df = pd.DataFrame({
        "position": positions2,
        "frequency": position_counts
    })

    citations_chart = make_chart(citations_df, "citations")
    positions_chart = make_chart(positions_df, "frequency")

    st.altair_chart(citations_chart, use_container_width=True)
    st.altair_chart(positions_chart, use_container_width=True)