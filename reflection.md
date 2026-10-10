# Reflection: Game Glitch Investigator

## 1. What was broken when I started?

I checked the game in Normal and Easy modes using the debug panel to see the secret. Several hints pointed in the wrong direction, and Easy accepted numbers outside its range. Blank input and abc showed errors but still used attempts. New Game also kept the previous input and won status, so the next round could not be played properly.

| Input or action | Expected behavior | Original behavior | Visible message |
|---|---|---|---|
| Normal: 45, secret 53 | Higher | Lower | Go LOWER |
| Normal: 100, secret 53 | Accept and say Lower | Accepted and said Lower | Correct visible hint; 100 is a valid endpoint |
| Easy: 99 | Reject without an attempt | Accepted and used an attempt | Go HIGHER |
| Easy: blank | Ask for input without an attempt | Used an attempt and added blank history | Enter a guess |
| Easy: 17.5, secret 17 | Reject decimal | Converted to 17 and won | Correct |
| New Game after winning | Start a playable fresh round | Old won status and input remained | You already won |

## 2. How did I use AI as a teammate?

I used ChatGPT/Codex to discuss the screenshots and then asked it to fix the code and document the results. The suggestion to keep round state in Streamlit session state and reset it through callbacks was useful; automated interface tests verified the reset. I corrected the interpretation of the 100 test because Normal mode includes both 1 and 100, and its visible Lower hint was correct for secret 53. The final tests check inclusive boundaries instead of treating 100 as invalid in Normal mode.

## 3. Debugging and testing the fixes

I used known secrets from the debug panel to compare the expected hint with the displayed hint. I asked Codex to add and run pytest tests for those examples and for invalid input, scoring, and round resets. All 64 tests passed, including Streamlit interface tests that submit guesses, change difficulty, and restart after winning or losing. The screenshots record the original bugs; I have not supplied new manual screenshots of the fixed version.

## 4. What did I learn about Streamlit and state?

Streamlit runs the script again when a player uses a widget. Session state remembers the round between these reruns, so the secret does not need to be generated again for every guess. A new round must reset all related values, including the input, history, message, attempts, score, and status. Callbacks update those values before the screen is drawn, which helps avoid old values appearing on screen.

## 5. Looking ahead: developer habits

I want to keep testing the smallest and largest allowed values, invalid text, and the New Game button. Next time, I will record the mode, secret, input, expected result, and actual result together before asking AI for a fix. I will also check an AI explanation against the code and screenshots rather than accepting it immediately. This project showed me that AI-generated code needs tests for the whole player flow as well as individual functions.
