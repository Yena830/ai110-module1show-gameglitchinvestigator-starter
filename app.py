import random
import streamlit as st
# FIX: Refactored core logic into logic_utils.py (GitHub Copilot Agent Mode).
# Collaborated with Copilot to extract functions and verified each moved function still works.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    load_high_scores,
    save_high_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

# FIX: Added difficulty change detection to reset game state.
# Bug: Switching difficulty mid-game kept the old secret and attempt count.
# Copilot Agent Mode generated this block; I confirmed logic was correct in diff review.
if "current_difficulty" not in st.session_state or st.session_state.current_difficulty != difficulty:
    st.session_state.current_difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE (Challenge 2): High Score display in sidebar.
# Copilot Agent Mode suggested reading the file on every rerun so scores always reflect disk state.
st.sidebar.divider()
st.sidebar.subheader("🏆 High Scores")
high_scores = load_high_scores()
if high_scores:
    for diff in ["Easy", "Normal", "Hard"]:
        if diff in high_scores:
            st.sidebar.caption(f"{diff}: {high_scores[diff]} pts")
else:
    st.sidebar.caption("No high scores yet. Win a game!")

# FEATURE (Challenge 2): Guess History visualization in sidebar.
# Copilot Agent Mode suggested using st.progress to show closeness as a bar.
# I adjusted the formula so 100% = exact match and values always stay in [0, 1].
st.sidebar.divider()
st.sidebar.subheader("📊 Guess History")
if st.session_state.get("history"):
    secret = st.session_state.secret
    range_size = high - low or 1
    for g in st.session_state.history:
        if isinstance(g, int):
            closeness = max(0.0, 1.0 - abs(g - secret) / range_size)
            st.sidebar.caption(f"Guess: {g}")
            st.sidebar.progress(closeness)
        else:
            st.sidebar.caption(f"Invalid input: {g}")
else:
    st.sidebar.caption("No guesses yet.")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: Changed attempts initial value from 1 to 0.
# Bug: Starting at 1 caused attempt count to be off by one throughout the game.
# Fixed using Copilot inline suggestion, verified by running the game manually.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_hint" not in st.session_state:
    st.session_state.last_hint = None

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.last_hint = None
    st.success("New game started.")
    st.rerun()

if st.session_state.get("last_hint"):
    st.warning(st.session_state.last_hint)

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: Removed alternating str/int casting of secret.
        # Bug: secret was cast to str on even attempts, causing comparison failures.
        # I spotted this in the diff review; Copilot had introduced the alternating logic incorrectly.
        secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        st.session_state.last_hint = message if show_hint else None

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            save_high_score(difficulty, st.session_state.score)
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
            st.rerun()
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )
            st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
