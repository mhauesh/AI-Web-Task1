import streamlit as st
from country_list import countries_for_language
from geopy.distance import geodesic
import random
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# variables for stats
if 'total_games' not in st.session_state:
    st.session_state.total_games = 0
if 'games_won' not in st.session_state:
    st.session_state.games_won = 0
if 'avg_questions_used' not in st.session_state:
    st.session_state.avg_questions_used = 0
if 'questions_history' not in st.session_state:
    st.session_state.questions_history = []
if 'current_game_questions' not in st.session_state:
    st.session_state.current_game_questions = 0

# variables for current game

countries = dict(countries_for_language('en'))

if 'country_to_guess' not in st.session_state:
    st.session_state.country_to_guess = random.choice(list(countries.values()))
if 'guesses_remaining' not in st.session_state:
    st.session_state.guesses_remaining = 3
if 'questions_remaining' not in st.session_state:
    st.session_state.questions_remaining = 12

# 2 pages for games and stats
tab1, tab2 = st.tabs(["Game", "Stats"])

def update_stats_and_reset():
    st.session_state.total_games += 1
    st.session_state.games_won += 1
    st.session_state.questions_history.append(st.session_state.current_game_questions)
    st.session_state.avg_questions_used = sum(st.session_state.questions_history) / len(st.session_state.questions_history)
    st.success("Good Job! Head over to the stats page to see your stats!")
    st.session_state.country_to_guess = random.choice(list(countries.values()))
    st.session_state.guesses_remaining = 3
    st.session_state.questions_remaining = 12
    st.session_state.current_game_questions = 0

def reset_game_state():
    st.session_state.country_to_guess = random.choice(list(countries.values()))
    st.session_state.guesses_remaining = 3
    st.session_state.questions_remaining = 12
    st.session_state.current_game_questions = 0

with tab1:
    st.title("Guess the Country using up to 12 questions!")
    
    # Add New Game button at the top
    if st.button("Start New Game"):
        reset_game_state()
    
    st.write("Guesses Remaining:", st.session_state.guesses_remaining)
    st.write("Questions Remaining:", st.session_state.questions_remaining)

    # Only allow questions if there are questions remaining and guesses remaining
    question_input = ""
    if st.session_state.questions_remaining > 0 and st.session_state.guesses_remaining > 0:
        question_input = st.text_input("Ask a question to help you guess the country", key=f"question_{st.session_state.total_games}")

    if question_input:
        st.session_state.questions_remaining -= 1
        st.session_state.current_game_questions += 1
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please check your .env file.")
        else:
            try:
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
            except Exception as e:
                st.error(f"Error calling OpenAI API: {str(e)}")

    # Only show the country to guess for debugging
    if st.session_state.guesses_remaining > 0:
        st.write(st.session_state.country_to_guess)

    # Only allow guesses if there are guesses remaining
    guess = ""
    if st.session_state.guesses_remaining > 0:
        guess = st.text_input("Guess the Country", key=f"guess_{st.session_state.total_games}")

    if guess:
        if guess == st.session_state.country_to_guess:
            st.balloons()
            update_stats_and_reset()
        else:
            st.session_state.guesses_remaining -= 1
            if st.session_state.guesses_remaining > 0:
                question = "What is the distance in KM between the capital city of " + guess + " and the capital city of " + st.session_state.country_to_guess + "? Output just the number and nothing else. If you have no sufficient info, just output infinity."
                api_key = os.getenv("OPENAI_API_KEY")
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
                st.session_state.total_games += 1
                st.session_state.questions_history.append(st.session_state.current_game_questions)
                st.session_state.avg_questions_used = sum(st.session_state.questions_history) / len(st.session_state.questions_history)
                st.info("Click 'Start New Game' at the top to play again!")

    # Show game over message if no guesses remaining
    if st.session_state.guesses_remaining == 0:
        st.warning("Game Over! Click 'Start New Game' to play again.")

with tab2:
    st.title("Game Statistics")
    
    # Display stats in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Games Played", st.session_state.total_games)
    
    with col2:
        win_rate = (st.session_state.games_won / st.session_state.total_games * 100) if st.session_state.total_games > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col3:
        st.metric("Avg Questions Used", f"{st.session_state.avg_questions_used:.1f}")
    
    # Show questions history chart
    if st.session_state.questions_history:
        st.subheader("Questions Used Per Game")
        st.line_chart(st.session_state.questions_history)