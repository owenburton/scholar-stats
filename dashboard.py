import streamlit as st
import pandas as pd
import altair as alt

from utils import *

from selenium.webdriver import PhantomJS

# TODO: switch to headless chrome, as phantomjs is deprecated

driver = PhantomJS()

st.title("scholar stats")

url = st.text_input("copy/paste the url of a scholar profile from google scholars")

if url:
    page = scrape_scholar_from_url(driver, url)

    author_name = get_author_name(page)
    st.text(author_name)

    authors_list = extract_author_names_of_papers(page)
    
    author_positions = get_author_positions(authors_list, author_name)
    ordered_positions = order_author_positions(author_positions)

    positions = list(ordered_positions.keys())
    frequency = list(ordered_positions.values())

    positions_df = pd.DataFrame({
        "position": positions,
        "frequency": frequency
    })

    ## TODO: move chart specifics to utls

    chart = alt.Chart(positions_df).mark_bar().encode(
        x='position', 
        y='frequency',
        color=alt.Color(
            "position", 
            scale=alt.Scale(scheme="greenblue"), 
            legend=None
            )
        ).configure_axis(
            grid=False
        ).configure_axisX(
            labelAngle=0
        ).configure_view(
            strokeWidth=0
        )

    st.altair_chart(chart, use_container_width=True)