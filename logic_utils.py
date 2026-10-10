"""Number guessing rules, independent of Streamlit."""

import random
import re

DIFFICULTIES = {
    "Easy": (1, 20, 6),
    "Normal": (1, 100, 8),
    "Hard": (1, 50, 5),
}


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive lower and upper bounds."""
    low, high, _ = DIFFICULTIES[difficulty]
    return low, high


def get_attempt_limit(difficulty: str):
    return DIFFICULTIES[difficulty][2]


def parse_guess(raw: str, low: int = 1, high: int = 100):
    """Accept whole-number text within the inclusive selected range."""
    if raw is None or not raw.strip():
        return False, None, "Enter a guess."
    text = raw.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", text):
        if re.search(r"[0-9]", text):
            return False, None, "Enter a whole number."
        return False, None, "That is not a number."
    try:
        value = int(text)
    except ValueError:
        return False, None, "Enter a whole number."
    if not low <= value <= high:
        return False, None, f"Enter a whole number from {low} to {high}, including both endpoints."
    return True, value, None


def check_guess(guess: int, secret: int):
    """Return the outcome string expected by the starter tests."""
    if type(guess) is not int or type(secret) is not int:
        raise TypeError("Guess and secret must be integers.")
    if guess == secret:
        return "Win"
    return "Too High" if guess > secret else "Too Low"


def get_hint(outcome: str):
    return {
        "Win": "🎉 Correct!",
        "Too High": "📉 Go LOWER!",
        "Too Low": "📈 Go HIGHER!",
    }[outcome]


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Wrong valid guesses lose 5; wins earn 100, 90, ... (minimum 10)."""
    if attempt_number < 1:
        raise ValueError("Attempt numbers start at 1.")
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    if outcome in ("Too High", "Too Low"):
        return current_score - 5
    raise ValueError(f"Unknown outcome: {outcome}")


def create_game(difficulty: str):
    """Create a fresh round; generate a secret only at the start of a round."""
    low, high = get_range_for_difficulty(difficulty)
    return {
        "difficulty": difficulty,
        "secret": random.randint(low, high),
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
        "last_outcome": None,
    }


def submit_guess(game: dict, raw: str):
    """Return (updated_game, error); invalid or finished submissions change nothing."""
    if game["status"] != "playing":
        return game, "Game finished. Start a new game to play again."
    low, high = get_range_for_difficulty(game["difficulty"])
    ok, guess, error = parse_guess(raw, low, high)
    if not ok:
        return game, error
    attempts = game["attempts"] + 1
    outcome = check_guess(guess, game["secret"])
    status = "playing"
    if outcome == "Win":
        status = "won"
    elif attempts >= get_attempt_limit(game["difficulty"]):
        status = "lost"
    return {
        **game,
        "attempts": attempts,
        "score": update_score(game["score"], outcome, attempts),
        "status": status,
        "history": [*game["history"], guess],
        "last_outcome": outcome,
    }, None
