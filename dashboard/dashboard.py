import streamlit as st
import pandas as pd
from PIL import Image

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

# example_url = "https://scholar.google.co.uk/citations?hl=en&user=JicYPdAAAAAJ"
example_url = "https://scholar.google.com/citations?user=D2H5EFEAAAAJ&hl=en"
input_url = st.text_input(
    "copy/paste the url of a scholar profile from google scholars",
    example_url)

if input_url:

    if validate_url(input_url):
        response = hit_scraper_api(input_url)

        if "name" in response:
            st.text(response["name"])

            # st.json(response)
            positions, hindexes, citations = response["positions"], response["hindexes"], response["citations"]

            ordered_positions, ordered_citations = order_dicts(positions, citations)

            positions = list(ordered_citations.keys())
            hindex_vals = list(hindexes.values())
            citation_counts = list(ordered_citations.values())
            publication_counts = list(ordered_positions.values())

            df = pd.DataFrame({
                "positions": positions,
                "h-index": hindex_vals,
                "publications": publication_counts,
                "citations": citation_counts
            })

            df["portion_of_citations"] = (100 * df.citations / df.citations.sum()).round(0)
            df.portion_of_citations = df.portion_of_citations / 100

            citations_chart = make_chart(df[["positions", "portion_of_citations"]])
            st.altair_chart(citations_chart, use_container_width=True)

            df.portion_of_citations = (df.portion_of_citations * 100).astype(str) + '%'

            st.table(df.set_index("positions"))
        
        else:
            st.text(response["message"])

    else:
        st.text("invalid url")