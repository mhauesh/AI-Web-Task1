import streamlit as st
from country_list import countries_for_language
from geopy.distance import geodesic
import random
from openai import OpenAI

# variables for current game
countries = dict(countries_for_language('en'))

if 'country_to_guess' not in st.session_state:
    st.session_state.country_to_guess = random.choice(list(countries.values()))
if 'guesses_remaining' not in st.session_state:
    st.session_state.guesses_remaining = 3
if 'questions_remaining' not in st.session_state:
    st.session_state.questions_remaining = 12

def reset_game_state():
    st.session_state.country_to_guess = random.choice(list(countries.values()))
    st.session_state.guesses_remaining = 3
    st.session_state.questions_remaining = 12

st.title("Guess the Country using up to 12 questions!")

# Add New Game button at the top
if st.button("Start New Game"):
    reset_game_state()

st.write("Guesses Remaining:", st.session_state.guesses_remaining)
st.write("Questions Remaining:", st.session_state.questions_remaining)

# Only allow questions if there are questions remaining and guesses remaining
question_input = ""
if st.session_state.questions_remaining > 0 and st.session_state.guesses_remaining > 0:
    question_input = st.text_input("Ask a question to help you guess the country")

if question_input:
    st.session_state.questions_remaining -= 1
    
    api_key = st.secrets["api_key"]
    client = OpenAI(api_key=api_key)
    model = "gpt-4"  # or "gpt-3.5-turbo" if you prefer
    question = "Answer the following question in Yes or No only. If not a valid question, answer NA. Do not reveal the country name. The question is about the country " + st.session_state.country_to_guess + ": " + question_input

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": question},
        ],
    )
    if st.session_state.questions_remaining != 12:
        st.write(chat_completion.choices[0].message.content)


if st.session_state.guesses_remaining > 0:
    st.write(st.session_state.country_to_guess)

guess = ""
if st.session_state.guesses_remaining > 0:
    guess = st.text_input("Guess the Country")

if guess:
    if guess == st.session_state.country_to_guess:
        st.balloons()
        st.success("Congratulations! You've won!")
        reset_game_state()
    else:
        st.session_state.guesses_remaining -= 1
        if st.session_state.guesses_remaining > 0:
            question = "What is the distance in KM between the capital city of " + guess + " and the capital city of " + st.session_state.country_to_guess + "? Output just the number and nothing else. If you have no sufficient info, just output infinity."
            api_key = st.secrets["api_key"]
            client = OpenAI(api_key=api_key)
            model = "gpt-4"
            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": question},
                ],
            )
            st.write("Try Again. Distance to Answer is Approx. ", chat_completion.choices[0].message.content, " KM")
        else:
            st.error(f"Game Over! The country was {st.session_state.country_to_guess}")
            st.info("Click 'Start New Game' at the top to play again!")

if st.session_state.guesses_remaining == 0:
    st.warning("Game Over! Click 'Start New Game' to play again.")