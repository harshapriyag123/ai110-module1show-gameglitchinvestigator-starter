from copy import deepcopy

import pytest

from logic_utils import (
    create_game, get_attempt_limit, get_hint, get_range_for_difficulty,
    parse_guess, submit_guess, update_score, check_guess,
)


@pytest.mark.parametrize("difficulty,low,high,limit", [
    ("Easy", 1, 20, 6), ("Normal", 1, 100, 8), ("Hard", 1, 50, 5),
])
def test_difficulty_boundaries(difficulty, low, high, limit, monkeypatch):
    assert get_range_for_difficulty(difficulty) == (low, high)
    assert get_attempt_limit(difficulty) == limit
    for endpoint in (low, high):
        monkeypatch.setattr("logic_utils.random.randint", lambda a, b: endpoint)
        assert create_game(difficulty)["secret"] == endpoint
        assert parse_guess(str(endpoint), low, high) == (True, endpoint, None)
    for invalid in (low - 1, high + 1):
        assert not parse_guess(str(invalid), low, high)[0]


@pytest.mark.parametrize("raw", [None, "", "   ", "abc", "17.5", "17.0", "1e1", "NaN", "inf", "0", "-1", "21", "99", "100", "9" * 5000])
def test_invalid_input_does_not_change_round(raw):
    game = create_game("Easy")
    before = deepcopy(game)
    updated, error = submit_guess(game, raw)
    assert error
    assert updated == before
    assert game == before


@pytest.mark.parametrize("guess,secret,outcome,hint", [
    (45, 53, "Too Low", "HIGHER"), (54, 53, "Too High", "LOWER"),
    (99, 53, "Too High", "LOWER"), (1, 53, "Too Low", "HIGHER"),
    (100, 53, "Too High", "LOWER"), (77, 53, "Too High", "LOWER"),
    (4, 53, "Too Low", "HIGHER"), (2, 19, "Too Low", "HIGHER"),
    (17, 19, "Too Low", "HIGHER"), (20, 19, "Too High", "LOWER"),
    (19, 19, "Win", "Correct"),
])
def test_screenshot_numeric_comparisons(guess, secret, outcome, hint):
    assert check_guess(guess, secret) == outcome
    assert hint in get_hint(outcome)


@pytest.mark.parametrize("guess,secret", [("100", 53), (100, "53"), (True, 1)])
def test_comparison_requires_integers(guess, secret):
    with pytest.raises(TypeError):
        check_guess(guess, secret)


@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
@pytest.mark.parametrize("attempt", [1, 2, 3, 4])
def test_wrong_guesses_always_lose_five(outcome, attempt):
    assert update_score(0, outcome, attempt) == -5


@pytest.mark.parametrize("attempt,bonus", [(1, 100), (2, 90), (6, 50), (20, 10)])
def test_winning_score(attempt, bonus):
    assert update_score(-5, "Win", attempt) == bonus - 5


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_full_attempt_limit_and_frozen_finished_game(difficulty):
    game = create_game(difficulty)
    game["secret"] = 2
    limit = get_attempt_limit(difficulty)
    for attempt in range(1, limit + 1):
        game, error = submit_guess(game, "1")
        assert error is None
        assert game["secret"] == 2
        assert game["attempts"] == attempt
        assert game["status"] == ("lost" if attempt == limit else "playing")
    before = deepcopy(game)
    game, error = submit_guess(game, "2")
    assert error
    assert game == before


def test_win_on_last_allowed_attempt():
    game = create_game("Easy")
    game["secret"] = 19
    for _ in range(5):
        game, _ = submit_guess(game, "1")
    game, error = submit_guess(game, "19")
    assert error is None
    assert game["status"] == "won"
    assert game["attempts"] == 6
    assert game["history"][-1] == 19
    assert game["score"] == 25
