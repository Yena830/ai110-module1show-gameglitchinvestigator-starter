# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
![first time running screenshot](screenshots/first.png)!
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

1. When I first loaded the game the "Attempts left" counter read 7 even before I’d guessed—this happened for every difficulty level.
![attempts display error](screenshots/attemptnum.png)
2. Starting a new game didn’t clear out the previous game’s information; the old score, history, and secret remained visible.
3. The feedback hints were inverted: a guess below the secret prompted "go lower" and a guess above prompted "go higher". In particular, guessing 100 always produced "go lower".
![should go lower](screenshots/go_lower.png)
![should go higher](screenshots/go_higher.png)
![guessing 100](screenshots/100.png)
4. After submitting a guess, the "Attempts left" counter didn't update immediately, requiring input of the next number to trigger the update. This caused issues like showing "Attempts left: 1" even when the game should have ended on the last attempt.
5. Pressing the "New Game" button in the middle of a game instantly changed the secret number.
6. Changing the difficulty slider didn’t alter the secret number’s range—the secret stayed between 1 and 100 no matter which difficulty I chose.
![difficulty range bug](screenshots/difficuty_bug.png)
7. On even-numbered guesses, the secret number was converted to a string, which caused string comparison instead of numeric comparison. This made certain guesses (like 100) always return "go lower" due to lexicographic ordering (e.g., "100" < "50" as strings), even when numerically incorrect.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I used **GitHub Copilot Agent Mode** throughout this project. It helped me identify bugs, generate fixes, and refactor code.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

**Correctly Fixed: Reversed High/Low Hints**
- **What Copilot suggested**: When checking if `guess > secret`, return "Too High" with message "Go LOWER!" (not "Go HIGHER!"). It identified that BOTH the True and False branches needed fixing because the original code had the logic backwards.
- **How I verified**: I ran the game and tested guessing 100 when the secret was 50. The hint correctly said "Go LOWER!" instead of the original broken "Go HIGHER!". I also ran pytest and verified all 10 tests pass, including the targeted tests I created for this bug.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

**Incorrectly Suggested: Alternating str/int Casting of Secret**
- **What Copilot suggested**: On even-numbered attempts, convert the secret to a string for comparison. This was introduced during an earlier code generation attempt.
- **Why it was wrong**: String comparison of numbers fails lexicographically—"100" < "50" as strings, causing incorrect game behavior. This caused guesses like 100 to always return "go lower" even when wrong.
- **How I verified it was wrong**: I manually tested the game and noticed guesses above the secret still gave the wrong hint. When I reviewed the code diff, I spotted the alternating `if attempt_number % 2 == 0: secret = str(secret)` logic. I removed it and re-tested, and the hints became correct.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

I used three verification methods: (1) Manual gameplay testing—playing several rounds and checking if the hint messages, attempt counter, and score all behaved correctly; (2) Pytest unit tests—running `python3 -m pytest tests/test_game_logic.py -v` to ensure all assertion pass; (3) Code review—inspecting the diff between the broken and fixed versions to confirm the logic change matched the bug description.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

**Pytest Test: `test_high_guess_returns_lower_hint`**
- **What it tests**: When `guess > secret`, the function should return "Too High" outcome with a message containing "LOWER".
- **What it showed**: This test initially failed with the reversed logic (returning "Go HIGHER!" incorrectly). After applying the fix, the test passed, confirming the hint was now correct. I created 10 targeted tests total to prevent regression of both the high/low bug and the string casting bug.

- Did AI help you design or understand any tests? How?

Yes. I asked Copilot to help me create comprehensive test cases that would catch the specific bugs I fixed. Copilot suggested testing boundary conditions (guesses at 1, 100, off-by-one), mixed-type comparisons (when secret is a string), and the core high/low hint logic. This helped me design tests that would fail with the original buggy code and pass after my fixes.

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

Every time the user clicked a button or typed something, 
Streamlit re-ran the entire app.py file from top to bottom. 
The original code had `random.randint(1, 100)` running at the 
top level with no protection, so every rerun generated a brand 
new secret number. This made the game impossible to play because 
the target kept changing after every guess.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Imagine every time you click a button on a website, the whole 
page refreshes and forgets everything — like clearing your 
browser history after every click. That's what Streamlit does 
by default. Session state is like a small notebook that Streamlit 
keeps on the side. Anything you write in that notebook survives 
the refresh. So instead of generating a new secret number every 
rerun, we store it in st.session_state.secret and it stays the 
same until we deliberately change it.

- What change did you make that finally gave the game a stable secret number?

The original code generated the secret with a bare random.randint() call at the top of the script. Since Streamlit reruns the entire script on every button click, the secret changed on every guess. The fix was to store it in st.session_state.secret so it persists across reruns, and only regenerate it when the difficulty changes or the player starts a new game.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

I want to keep using the habit of opening a new Chat session 
for each individual bug. Keeping each conversation focused on 
one problem stopped the AI from getting confused by unrelated 
context, and made it much easier to trace which fix came from 
which conversation.

- What is one thing you would do differently next time you work with AI on a coding task?

Next time I would add FIXME comments before asking the AI for 
  help, instead of just describing the bug in words. Pointing the 
  AI directly at the exact line made its suggestions much more 
  accurate, and I did not always do this at the start of the 
  project.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

I used to assume that if the AI sounded confident, the code was 
  probably correct. This project taught me that AI can produce 
  plausible-looking code that is subtly wrong, so reviewing every 
  diff carefully and running tests is not optional — it is the 
  most important part of working with AI.
