from collections import OrderedDict
import altair as alt
import streamlit as st
import requests

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def validate_url(url):
    try:
        response = requests.get(url)
        return response.status_code == requests.codes.ok
    except:
        return False

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def hit_scraper_api(url):
    payload = {"url": url}
    scraper_url = "http://0.0.0.0:8080" # local deploy
    # scraper_url = "https://scholarscraper-st2oqocqiq-uw.a.run.app" # deployed api on Cloud Run
    r = requests.post(url=scraper_url, json=payload) 

    return r.json()


def order_one(dct):
    return OrderedDict(sorted(dct.items()))


def order_dicts(dict1, dict2):
    return order_one(dict1), order_one(dict2)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def make_chart(df):
    return alt.Chart(df).mark_bar().encode(
        alt.X('portion_of_citations', axis=alt.Axis(title="portion of citations", tickCount=5, format='%')),
        y='positions',
        color=alt.Color(
            "positions", 
            scale=alt.Scale(scheme="greenblue"), 
            legend=None
            )
        ).properties(
            title='total citations by author position'
        ).configure_axisX(
            labelAngle=0
        ).configure_axis(
            grid=False
        ).configure_view(
            strokeWidth=0
        )