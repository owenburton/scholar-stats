import streamlit as st
import pandas as pd

from utils import *

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
    response = hit_scraper_api(url)
    positions, citations = response["positions"], response["citations"]

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

    citations_chart = make_chart(
        citations_df, 
        y_label_str="citations",
        title_str="total citations by author position"
        )
    positions_chart = make_chart(
        positions_df, 
        y_label_str="frequency",
        title_str="total publications by author position"
        )

    st.altair_chart(citations_chart, use_container_width=True)
    st.altair_chart(positions_chart, use_container_width=True)