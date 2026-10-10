from copy import deepcopy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def start(difficulty="Easy"):
    app = AppTest.from_file(str(APP)).run()
    app.selectbox(key="difficulty").select(difficulty).run()
    assert not app.exception
    return app


def submit(app, value):
    app.text_input(key="guess_input").set_value(value)
    app.button(key="submit").click().run()
    assert not app.exception
    return app.session_state["game"]


@pytest.mark.parametrize("difficulty,high,limit", [
    ("Easy", 20, 6), ("Normal", 100, 8), ("Hard", 50, 5),
])
def test_initial_settings_and_secret_survive_reruns(difficulty, high, limit):
    app = start(difficulty)
    game = app.session_state["game"]
    assert 1 <= game["secret"] <= high
    assert game["attempts"] == 0
    assert f"from 1 to {high}" in app.info[0].value
    assert f"Attempts left: {limit}" in app.info[0].value
    app.checkbox(key="show_hint").uncheck().run()
    assert app.session_state["game"] == game


@pytest.mark.parametrize("raw", ["", "abc", "17.5", "0", "21", "99"])
def test_invalid_submission_has_current_error_and_preserves_state(raw):
    app = start()
    before = deepcopy(app.session_state["game"])
    assert submit(app, raw) == before
    assert app.error
    assert app.metric[0].value == "0"
    app.checkbox(key="show_hint").uncheck().run()
    assert app.error
    assert app.session_state["game"] == before


def test_numeric_hints_history_and_score_update_immediately():
    app = start()
    app.session_state["game"]["secret"] = 19
    game = submit(app, "2")
    assert "HIGHER" in app.warning[0].value
    assert game["history"] == [2]
    assert game["attempts"] == 1
    assert app.metric[0].value == "-5"
    assert "Attempts left: 5" in app.info[0].value
    game = submit(app, "20")
    assert "LOWER" in app.warning[0].value
    assert game["history"] == [2, 20]
    assert app.metric[0].value == "-10"


@pytest.mark.parametrize("finish", ["won", "lost"])
def test_restart_after_win_or_loss_resets_everything(finish):
    app = start()
    app.session_state["game"]["secret"] = 19
    if finish == "won":
        game = submit(app, "19")
        assert "You won!" in app.success[0].value
    else:
        for _ in range(6):
            game = submit(app, "1")
        assert "Out of attempts!" in app.error[0].value
    assert game["status"] == finish
    assert app.button(key="submit").disabled
    app.button(key="new_game").click().run()
    game = app.session_state["game"]
    assert not app.exception
    assert game["status"] == "playing"
    assert game["history"] == []
    assert game["score"] == game["attempts"] == 0
    assert 1 <= game["secret"] <= 20
    assert app.text_input(key="guess_input").value == ""
    assert not app.button(key="submit").disabled
    assert not app.success and not app.warning and not app.error
    assert "Attempts left: 6" in app.info[0].value
    submit(app, "1")
    assert app.session_state["game"]["attempts"] == 1


def test_difficulty_change_resets_out_of_range_secret_and_finished_status():
    app = start("Normal")
    app.session_state["game"]["secret"] = 64
    submit(app, "64")
    for difficulty, high, limit in [("Easy", 20, 6), ("Hard", 50, 5), ("Normal", 100, 8)]:
        app.selectbox(key="difficulty").select(difficulty).run()
        assert not app.exception
        game = app.session_state["game"]
        assert game["difficulty"] == difficulty
        assert 1 <= game["secret"] <= high
        assert game["status"] == "playing"
        assert game["history"] == []
        assert game["attempts"] == game["score"] == 0
        assert app.text_input(key="guess_input").value == ""
        assert f"from 1 to {high}" in app.info[0].value
        assert f"Attempts left: {limit}" in app.info[0].value
        assert not app.success and not app.error
