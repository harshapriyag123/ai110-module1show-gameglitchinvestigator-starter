# 🎮 Game Glitch Investigator

## Game purpose

This is a number guessing game. The game chooses a secret whole number, and the player tries to find it before the attempts run out. Each valid guess gives a Higher or Lower hint. A correct guess wins the round.

| Mode | Allowed numbers, including both endpoints | Attempts |
|---|---|---|
| Easy | 1 to 20 | 6 |
| Normal | 1 to 100 | 8 |
| Hard | 1 to 50 | 5 |

**Yes, 100 is valid in Normal mode.** It is outside the range in Easy and Hard modes. Both 1 and each mode's upper limit are included.

## Issues found and fixes

| Issue | Simple explanation | Fix applied |
|---|---|---|
| Wrong Higher/Lower hints | A smaller guess could say Lower, and a larger guess could say Higher. | Smaller guesses now say Higher; larger guesses say Lower. |
| Numbers compared as text | Comparing text gives the wrong order for numbers such as 4 and 53. | Validate the input and compare integers. |
| Wrong range on screen | Easy mode still asked for a number from 1 to 100. | The prompt now shows the selected mode's range. |
| Secret outside the selected range | Easy mode could keep a Normal secret such as 53 or 64. | Changing difficulty starts a fresh round with a secret inside the correct range. |
| Missing range validation | Easy accepted 0 and 99. | Reject numbers outside the selected range, while accepting both endpoints. |
| Decimal accepted as a winning number | Entering 17.5 could become 17 and win when the secret was 17. | Accept only whole numbers; reject decimals without changing game progress. |
| Attempts counted incorrectly | A fresh game started with an attempt already used. Blank text and abc also used attempts. | Start at zero attempts. Count only valid guesses, and allow the full attempt limit. |
| Invalid input added to history | Blank text and invalid entries appeared in the guess history. | Record only accepted whole-number guesses. |
| New Game did not fully reset | The old input, score, history, win status, and alert could remain. A new round could still say “already won.” | Reset the whole round and clear the input and message. |
| Display showed old values | Debug information and attempts left could lag behind the submitted guess. | Button callbacks update state before the screen is drawn. |
| Inconsistent scoring | Wrong guesses did not always receive the same penalty. | Every wrong valid guess loses 5 points. Invalid input changes no score. |
| Logic and test mismatch | Game rules were mixed with the interface, and the comparison result did not match the starter tests. | Put the rules in logic_utils.py and keep app.py for the interface. |

### What happened to the secret number?

The inspected starter already stored the secret in Streamlit session state, so it did not generate a new secret on every Submit click. The state problem was keeping the wrong secret after a difficulty change and not fully resetting a round. The fixed game generates a secret when a round starts and keeps it unchanged during that round. A new random secret can happen to equal the previous one; that is allowed.

### Inputs checked in the original screenshots

These are observations from the original game, before the fixes. For Normal mode with secret **53**, all seven requested inputs are included:

| Guess | Expected hint | Original hint | Result |
|---|---|---|---|
| 45 | Higher | Lower | Wrong hint |
| 54 | Lower | Higher | Wrong hint |
| 99 | Lower | Higher | Wrong hint |
| 1 | Higher | Lower | Valid lower endpoint, wrong hint |
| 100 | Lower | Lower | Valid upper endpoint, correct visible hint |
| 77 | Lower | Higher | Wrong hint |
| 4 | Higher | Lower | Wrong hint |

The original hint for 100 happened to be correct. This does not make 100 invalid, and it does not prove the old comparison logic was correct.

Additional Easy-mode checks:

| Check | Original behavior | Fixed behavior |
|---|---|---|
| 2, secret 19 | Higher | Higher |
| 17, secret 19 | Lower | Higher |
| 20, secret 19 | Higher | Lower; 20 is valid |
| 19, secret 19 | Win | Win |
| 99 or 0 | Accepted and used an attempt | Reject; no attempt or score change |
| 1 | Accepted, but showed a wrong Lower hint against secret 64 | Accept as the lower endpoint; use a secret inside Easy's range |
| Blank or abc | Error shown, but attempt and history changed | Error shown; game progress stays unchanged |
| 17.5, secret 17 | Converted to 17 and won | Reject as a decimal |
| New Game after winning | Old input and won status remained | Clear input, messages, history, score, and status |

Hard-mode bounds and full attempt limits were checked by automated tests. No manual Hard-mode screenshot result is claimed here.

## Run the game

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use Python 3.10 or newer. A virtual environment is recommended.

## Presentation

[View the Game Glitch Investigator presentation](https://docs.google.com/presentation/d/e/2PACX-1vTbQQbH6i43hulSoYerhiv_euZEdlUG9NhHCTl1N8MIvSnDNJdwsh1zSqIsRbPgl5v6u0maP5XDCVM2/pub?start=true&loop=true&delayms=3000)

## Demo walkthrough

1. Run the app and choose **Normal**. It starts with eight attempts and accepts numbers from 1 to 100, inclusive.
2. Open **Developer Debug Info** to see the secret while testing. For example, if the secret is 53, enter **45** and click Submit: the hint should say **Higher**.
3. In that same example, enter **77**: the hint should say **Lower**. The secret stays 53, and the attempt count, history, and score update immediately.
4. Try abc, a blank entry, 17.5, or 101. Each is rejected without using an attempt. Enter the actual secret to win; 53 wins in this example.
5. Click **New Game**. The old input and message disappear, score returns to zero, history clears, and all attempts return. Change to Easy to check its inclusive 1–20 range and six attempts.

## Scoring

- Each wrong valid guess: **−5 points**.
- A win adds **100 points on attempt 1**, 90 on attempt 2, and so on, with a minimum reward of 10.
- Invalid input changes neither attempts nor score.
- New Game and difficulty changes reset the score to zero. Scores can be negative.

## Test results

Run the tests with:

```bash
python -m pytest tests/ -q
```

```text
$ python -m pytest tests/ -q
................................................................         [100%]
64 passed in 1.87s
```

The actual console output is also saved in [test_results.txt](test_results.txt). All 64 tests passed, covering the original starter tests, numeric hints, inclusive boundaries, invalid input, scoring, full attempt limits, secret persistence, and the Streamlit interface.

The interface tests click Submit and New Game and change difficulty. They check that a finished round can restart and that the screen shows current values. These are automated checks; the fixed app still needs a fresh screenshot if one is required for submission.

## Stretch features

The core game fixes are complete. A visible score and clear mode-specific instructions were added. No separate Enhanced UI challenge or model-comparison exercise is claimed.
