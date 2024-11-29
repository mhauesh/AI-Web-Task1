import streamlit as st
from country_list import countries_for_language
from geopy.distance import geodesic
import random
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

st.title("Guess the Country using up to 10 questions!")
st.write("Write the answer as Guess: + Answer")

countries = dict(countries_for_language('en'))
if 'country_to_guess' not in st.session_state:
    st.session_state.country_to_guess = random.choice(list(countries.values()))

if 'guesses_remaining' not in st.session_state:
    st.session_state.guesses_remaining = 3

if 'questions_remaining' not in st.session_state:
    st.session_state.questions_remaining = 12

st.write("Guesses Remainig :", st.session_state.guesses_remaining)
st.write("Questions Remaining :", st.session_state.questions_remaining)

question_input = st.text_input("Ask a question to help you guess the country", "")

if question_input:
    st.session_state.questions_remaining -= 1

if st.session_state.questions_remaining == 0:
    st.write("Game Over")
    st.write("The Country was", st.session_state.country_to_guess)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"
question = "Answer the following question in Yes or No only. Do not reveal the country name.The qeustion is about the country " + st.session_state.country_to_guess + ": " + question_input

chat_completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": question},
    ],
)
if st.session_state.questions_remaining != 12:
    st.title(chat_completion.choices[0].message.content)

#st.write(st.session_state.country_to_guess)
guess = st.text_input("Guess the Country", "")

if guess:
    st.session_state.guesses_remaining -= 1

if guess == st.session_state.country_to_guess:
    st.balloons()
if guess != st.session_state.country_to_guess: 
    question = "What is the distance between the guess " + guess + " and the country " + st.session_state.country_to_guess + " in KM. Output just the number and nothing else. If you have no sufficient info, just output infinity."
    chat_completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": question},
    ],
)

if st.session_state.guesses_remaining != 3:
    st.write("Try Again. Distance to Answer is Approx. ", chat_completion.choices[0].message.content, " KM")

if st.session_state.guesses_remaining == 0:
    st.write("Game Over")
    st.write("The Country was", st.session_state.country_to_guess)

