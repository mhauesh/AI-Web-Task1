import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def stats_page():

    # display stats
    
    st.header("Stats Page")
    st.write("Number of games played:", st.session_state.total_games)
    st.write("Number of games won:", st.session_state.games_won)
    st.write("Total questions asked:", st.session_state.total_questions)
    if st.session_state.total_guesses != 0:
        st.write("Your guesses are on average", int(st.session_state.guess_quality/st.session_state.total_guesses), " KM distance from the goal!")

    # used plotly because the st.barchart is not working properly

    if len(st.session_state.guesses_per_game) > 0:
        st.subheader("Guesses per Game")
        df = pd.DataFrame({
            'Game': range(1, len(st.session_state.guesses_per_game) + 1),
            'Guesses': st.session_state.guesses_per_game
        })
        fig = px.bar(df, x='Game', y='Guesses', title='Number of Guesses per Game')
        st.plotly_chart(fig)
