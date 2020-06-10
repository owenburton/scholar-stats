import streamlit as st
import pandas as pd

from utils import *

st.title("ScholarStats 📈")
st.write("Get a clearer view of researchers' contributions.\n")

st.write(
    """
    While [Google Scholar](https://scholar.google.com/) provides summary metrics used to quantify individual scientific output (which influences careers, funding, accolades, etc.), these metrics don't give a full picture of a scientist's contributions to their field.
    
    💡 This app improves upon Google Scholar profiles by approximating a researcher's level of contribution to their publication record, using author byline position as a proxy.
    
    💻 The code is available [here](https://github.com/owenburton/scholar-stats).
    """
    )

example_url = "https://scholar.google.com/citations?user=5Iqe53IAAAAJ&hl=en&oi=ao"
input_url = st.text_input(
    "Copy & paste the URL of a profile from Google Scholar",
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
                {response['role']}\n
                overall h-index: {overall_hindex}\n
                total citations: {total_citations}
                """)

            ordered_positions, ordered_citations = order_dicts(positions, citations)
            ordered_positions.move_to_end('last')
            ordered_citations.move_to_end('last')

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

            df.portion_of_citations = (df.portion_of_citations * 100).astype(str) + '%'

            st.table(df.drop(columns=['portion_of_citations']).set_index("positions"))

            # *Note:* Google Scholar pages don't account for duplicate publications when calculating overall h-index, 
            #     but [seem to do so](https://github.com/owenburton/scholar-stats/blob/master/notebooks/scrape-author-positions.ipynb) for total citations. 🔍 
            #     This app does not consider duplicates, because they're rare.
            st.write(
                """
                ⚠️ **Disclaimer**: 
                - This app inherits any shortcomings in the way Google Scholar indexes publication records and citations (e.g., total publication counts include items other than peer-reviewed articles, such as conference abstracts; e.g., citation counts may include citations by indexed items that are not peer reviewed).
                - Google Scholar profiles truncate the list of co-authors for each publication, so "last author" stats may be innacurate for some profiles.
                - This app abides by Google’s [Terms of Service](https://policies.google.com/terms?hl=en-US) and is not to be used in any such manner that violates these terms. The user of this app is granted nonexclusive, personal non-profit use.

                ✉️ **Contact**:
                - Questions? Suggestions? <scholarstats.app@gmail.com>
                - [Owen Burton](https://owenburton.github.io) & [Zachary Burton](https://www.linkedin.com/in/zb1/) 

                © Copyright 2020 ScholarStats
                """
                )
        
        else:
            st.text(response["message"])

    else:
        st.text("invalid url")