import streamlit as st
import pandas as pd
from PIL import Image

from utils import *

st.title("Scholar Stats 📈")
st.write("Get a clearer view of researchers' contributions.\n")

st.write(
    """
    While [Google Scholar](https://scholar.google.com/citations?user=JicYPdAAAAAJ&hl=en&oi=ao) provides summary metrics that are often used in hiring, promotions, and other important decisions, those metrics don't give a full picture of that person's contributions to their field.
    
    💡 This app improves upon those Scholar profiles by layering in the researcher's individual level of work for each of their publications.
    
    💻 The code is available [here](https://github.com/owenburton/scholar-stats).
    """
    )

# example_url = "https://scholar.google.co.uk/citations?hl=en&user=JicYPdAAAAAJ"
example_url = "https://scholar.google.com/citations?user=D2H5EFEAAAAJ&hl=en"
input_url = st.text_input(
    "copy/paste the url of a profile from Google Scholar",
    example_url)

if input_url:

    if validate_url(input_url):
        response = hit_scraper_api(input_url)

        if "name" in response:
            # st.json(response)
            positions, hindexes, citations = response["positions"], response["hindexes"], response["citations"]

            overall_hindex = sum(hindexes.values())
            total_citations = sum(citations.values())

            st.write(
                f"""
                ### {response['name']}
                overall h-index: {overall_hindex}\n
                total citations: {total_citations}
                """)

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

            # add a lil space
            st.text("")
            st.altair_chart(citations_chart, use_container_width=True)

            st.write(
                """
                *Note:* Google Scholar pages don't account for duplicate publications when calculating overall h-index, 
                but [seem to do so](https://github.com/owenburton/scholar-stats/blob/master/notebooks/scrape-author-positions.ipynb) for total citations. 🔍 
                This app does not consider duplicates, because they're rare.
                """
                )

            df.portion_of_citations = (df.portion_of_citations * 100).astype(str) + '%'

            st.table(df.drop(columns=['portion_of_citations']).set_index("positions"))
        
        else:
            st.text(response["message"])

    else:
        st.text("invalid url")