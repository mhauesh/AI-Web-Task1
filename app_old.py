import streamlit as st
from country_list import countries_for_language
import random


st.title("Guess the country!")

countries = dict(countries_for_language('en'))
country_to_guess = random.choice(list(countries.values()))

guess = st.text_input("Guess the country", "")

if guess == country_to_guess:
    st.write("Correct")
else:
    st.write("Incorrect")

st.write(country_to_guess)
