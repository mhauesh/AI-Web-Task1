import streamlit as st
from country_list import countries_for_language
from geopy.distance import geodesic
import random
from openai import OpenAI

def play_page():

    # variables for current game
    countries = dict(countries_for_language('en'))

    if 'country_to_guess' not in st.session_state:
        st.session_state.country_to_guess = random.choice(list(countries.values()))
    if 'guesses_remaining' not in st.session_state:
        st.session_state.guesses_remaining = 3
    if 'questions_remaining' not in st.session_state:
        st.session_state.questions_remaining = 12

    # variables for stats
    if 'total_games' not in st.session_state:
        st.session_state.total_games = 1
    if 'games_won' not in st.session_state:
        st.session_state.games_won = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'total_guesses' not in st.session_state:
        st.session_state.total_guesses = 0
    if 'guess_quality' not in st.session_state:
        st.session_state.guess_quality = 0
    if 'guesses_per_game' not in st.session_state:
        st.session_state.guesses_per_game = []    
    if 'current_game_guesses' not in st.session_state:
        st.session_state.current_game_guesses = 0

    # function to reset stats and country and aggregate total stats
    def reset_game_state():
        if st.session_state.total_games > 0:
            st.session_state.guesses_per_game.append(st.session_state.current_game_guesses)
        st.session_state.country_to_guess = random.choice(list(countries.values()))
        st.session_state.guesses_remaining = 3
        st.session_state.questions_remaining = 12
        st.session_state.total_games += 1
        st.session_state.current_game_guesses = 0


    st.title("Guess the Country using up to 12 questions!")

    # button to reset game
    if st.button("Start New Game"):
        reset_game_state()

    st.write("Guesses Remaining:", st.session_state.guesses_remaining)
    st.write("Questions Remaining:", st.session_state.questions_remaining)

    question_input = ""
    if st.session_state.questions_remaining > 0 and st.session_state.guesses_remaining > 0:
        question_input = st.text_input("Ask a question to help you guess the country")

    # handle the questions using the LLM
    if question_input:
        st.session_state.questions_remaining -= 1
        st.session_state.total_questions += 1
        api_key = st.secrets["api_key"]
        client = OpenAI(api_key=api_key)
        model = "gpt-4"  
        question = "Answer the following question in Yes or No only. If not a valid question, answer NA. Do not reveal the country name. The question is about the country " + st.session_state.country_to_guess + ": " + question_input

        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": question},
            ],
        )
        if st.session_state.questions_remaining != 12:
            st.write(chat_completion.choices[0].message.content)

    # guessing the country after (or during) questions
    guess = ""
    if st.session_state.guesses_remaining > 0:
        guess = st.text_input("Guess the Country")

    # handle the guessing while updating  stats

    if guess:
        st.session_state.total_guesses += 1
        st.session_state.current_game_guesses += 1
        # correct guess
        if guess == st.session_state.country_to_guess:
            st.balloons()
            st.success("Congratulations! You've won!")
            st.session_state.games_won += 1
            reset_game_state()
        # incorrect guess
        else:
            st.session_state.guesses_remaining -= 1
            # guess quality is distance from goal in KM (by capital cities, which is a good enough proxy)
            if st.session_state.guesses_remaining > 0:
                question = "What is the distance in KM between the capital city of " + guess + " and the capital city of " + st.session_state.country_to_guess + "? Output just the number and nothing else. If you have no sufficient info, just output NA."
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
                if chat_completion.choices[0].message.content != "NA":
                    st.session_state.guess_quality += float(chat_completion.choices[0].message.content)
            else:
                # guesses are done, game over
                st.error(f"Game Over! The country was {st.session_state.country_to_guess}")
                st.info("Click 'Start New Game' at the top to play again!")