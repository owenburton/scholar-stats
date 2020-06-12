from collections import OrderedDict
from pandas import DataFrame
from altair import Chart
import altair as alt
import streamlit as st
import requests

# caching for fast load times during local tests
# not suitable for deployed app because it doesn't 
# account for a scholar's changing metrics as add more publications
# @st.cache(allow_output_mutation=True, suppress_st_warning=True)
def validate_url(url: str) -> bool:
    """Uses the requests library to check if a given URL returns a 200 response

    Args:
        url (str): URL string given by the user

    Returns:
        bool: Returns True if it got a 200 response, False if not
    """
    try:
        response = requests.get(url)
        return response.status_code == requests.codes.ok

    except:
        return False

# @st.cache(allow_output_mutation=True, suppress_st_warning=True)
def hit_scraper_api(url: str) -> dict:
    """Sends a post request to the scraper API and gets back a json response as a Python dictionary

    Args:
        url (str): A verified URL given by the user

    Returns:
        dict: Either an error message, or the scraped metrics for a given author
    """
    payload = {"url": url}
    # scraper_url = "http://0.0.0.0:8080" # local deploy
    scraper_url = "https://scholarscraper-st2oqocqiq-uw.a.run.app" # deployed API on Cloud Run
    response = requests.post(url=scraper_url, json=payload) 

    return response.json()


def order_one(dct: dict) -> OrderedDict:
    """Sorts the scholar's metrics alphanumerically, then preserves that order

    Args:
        dct (dict): scraped scholar metrics

    Returns:
        OrderedDict: the properly arranged scholar metrics
    """
    return OrderedDict(sorted(dct.items()))


def order_dicts(dict1: dict, dict2: dict) -> OrderedDict:
    """Sorts the metrics contained in two dictionaries

    Args:
        dict1 (dict): publication counts for author position
        dict2 (dict): citation counts for each author position

    Returns:
        OrderedDict: the properly sorted scholar metrics
    """
    return order_one(dict1), order_one(dict2)

# @st.cache(allow_output_mutation=True, suppress_st_warning=True)
def make_chart(df: DataFrame) -> Chart:
    """Generates a horizontal bar chart of percentages of total citations by author position

    Args:
        df (DataFrame): dataframe of decimals by author position

    Returns:
        Chart: the rendered visualization
    """
    return alt.Chart(df).mark_bar().encode(
        alt.X(
            'portion_of_citations', 
            axis=alt.Axis(
                title="percentage of citations", 
                tickCount=5, 
                format='%'
                )
            ),
        alt.Y(
            'positions', 
            axis=alt.Axis(title="author position"), 
            sort=None
            ),
        color=alt.Color(
            "positions", 
            scale=alt.Scale(scheme="greenblue"), 
            legend=None
            )
        ).properties(
            title='citations by author position'
        ).configure_axisX(
            labelAngle=0
        ).configure_axis(
            grid=False
        ).configure_view(
            strokeWidth=0
        )