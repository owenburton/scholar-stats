import streamlit as st
import pandas as pd

from utils import *

st.title("scholar stats")

url = st.text_input("copy/paste the url of a scholar profile from google scholars")

if url:
    page = scrape_scholar_from_url(url)

    author_name = get_author_name(page)
    st.text(author_name)

    authors_list = extract_author_names_of_papers(page)
    st.text(authors_list)

    ## TODO: fix TypeError: 'NoneType' object is not callable from above code
    
    # author_positions = get_author_positions(authors_list, author_name)
    # ordered_positions = order_author_positions(author_positions)

    # positions_df = pd.DataFrame.from_dict(ordered_positions)
    # st.bar_chart(positions_df)