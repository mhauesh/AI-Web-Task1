import streamlit as st
from play import play_page
from stats import stats_page

pages = [
    st.Page(play_page, title="Play", default=True),
    st.Page(stats_page, title="Stats")
    ]

pg = st.navigation(pages)

pg.run()