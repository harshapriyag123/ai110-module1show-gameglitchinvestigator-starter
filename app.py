import streamlit as st

from logic_utils import (
    create_game,
    get_attempt_limit,
    get_hint,
    get_range_for_difficulty,
    submit_guess,
)

st.set_page_config(page_title="Number Guesser", page_icon="🎮")


def start_new_game():
    """Callbacks run before rendering, so resetting widget state is safe here."""
    st.session_state.game = create_game(st.session_state.difficulty)
    st.session_state.guess_input = ""
    st.session_state.error = None


def handle_submit():
    game, error = submit_guess(st.session_state.game, st.session_state.guess_input)
    st.session_state.game = game
    st.session_state.error = error


st.title("🎮 Game Glitch Investigator")
st.caption("Find the secret number using Higher and Lower hints.")
st.sidebar.header("Settings")
difficulty = st.sidebar.selectbox(
    "Difficulty", ["Easy", "Normal", "Hard"], index=1,
    key="difficulty", on_change=start_new_game,
)
if "game" not in st.session_state:
    start_new_game()

game = st.session_state.game
low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)
st.sidebar.caption(f"Range: {low} to {high} (inclusive)")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
st.subheader("Make a guess")
st.info(
    f"Guess a whole number from {low} to {high}, including both endpoints. "
    f"Attempts left: {attempt_limit - game['attempts']}"
)

with st.expander("Developer Debug Info"):
    st.caption("For testing only: this panel reveals the secret.")
    st.write("Secret:", game["secret"])
    st.write("Attempts:", game["attempts"])
    st.write("Score:", game["score"])
    st.write("Difficulty:", difficulty)
    st.write("History:", game["history"])

finished = game["status"] != "playing"
st.text_input("Enter your guess:", key="guess_input", disabled=finished)
col1, col2, col3 = st.columns(3)
with col1:
    st.button("Submit Guess 🚀", key="submit", on_click=handle_submit, disabled=finished)
with col2:
    st.button("New Game 🔁", key="new_game", on_click=start_new_game)
with col3:
    show_hint = st.checkbox("Show hint", value=True, key="show_hint")

st.metric("Score", game["score"])
if st.session_state.error:
    st.error(st.session_state.error)
elif game["status"] == "won":
    st.success(
        f"🎉 Correct! You won! The secret was {game['secret']}. "
        f"Final score: {game['score']}"
    )
elif game["status"] == "lost":
    st.error(
        f"Out of attempts! The secret was {game['secret']}. Score: {game['score']}"
    )
elif show_hint and game["last_outcome"]:
    st.warning(get_hint(game["last_outcome"]))

st.divider()
st.caption("Only valid guesses use attempts. New Game and difficulty changes start a fresh round.")
