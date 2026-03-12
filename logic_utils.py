import json
import os
from typing import Optional, Tuple, Union

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")


# FIX: Refactored from app.py into logic_utils.py (GitHub Copilot Agent Mode).
# Extracted core game logic for testability and code separation.
def get_range_for_difficulty(difficulty: str) -> Tuple[int, int]:
    """Return the inclusive (low, high) number range for a given difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.
            Any unrecognised value falls back to the Normal range.

    Returns:
        A tuple ``(low, high)`` representing the inclusive bounds of the
        secret number for the chosen difficulty.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 50)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


# FIX: Refactored from app.py into logic_utils.py (GitHub Copilot Agent Mode).
# Extracted core parsing logic for better testability and reusability.
def parse_guess(raw: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """Parse raw user input into an integer guess.

    Decimal strings (e.g. ``"3.9"``) are accepted and truncated toward zero
    rather than rounded, so ``"3.9"`` becomes ``3``.

    Args:
        raw: The raw string entered by the player.  May be ``None`` or empty.

    Returns:
        A three-element tuple ``(ok, guess_int, error_message)`` where:

        * ``ok`` is ``True`` when parsing succeeded.
        * ``guess_int`` is the parsed integer, or ``None`` on failure.
        * ``error_message`` is a human-readable error string, or ``None`` on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
        >>> parse_guess("3.9")
        (True, 3, None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: Refactored from app.py, with corrected logic (GitHub Copilot Agent Mode).
# Bug: Original had reversed high/low hints. AI identified both branches needed fixing.
# I verified the logic by running the game and checking the hints are now correct.
def check_guess(
    guess: Union[int, str], secret: Union[int, str]
) -> Tuple[str, str]:
    """Compare a player's guess against the secret number.

    Handles mixed int/str types gracefully via a ``TypeError`` fallback so
    that legacy callers passing a string secret do not crash.

    Args:
        guess: The player's guess, normally an ``int`` produced by
            :func:`parse_guess`.
        secret: The secret number stored in session state, normally an ``int``.

    Returns:
        A tuple ``(outcome, message)`` where ``outcome`` is one of:

        * ``"Win"`` — guess equals the secret.
        * ``"Too High"`` — guess is above the secret.
        * ``"Too Low"`` — guess is below the secret.

        ``message`` is a human-readable emoji string suitable for display.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(40, 50)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


# FEATURE (Challenge 2): High Score tracker — planned and scaffolded with Copilot Agent Mode.
# Agent suggested using JSON for persistence and returning the updated table so app.py stays stateless.
# I reviewed the file-write logic and added the os.path check to avoid crashes on first run.
def load_high_scores() -> dict:
    """Load the persisted high-score table from disk.

    Reads :data:`HIGHSCORE_FILE` and returns its contents as a plain ``dict``.
    If the file does not exist yet, or if it contains invalid JSON, an empty
    dict is returned so the caller never has to handle ``FileNotFoundError``
    or ``JSONDecodeError``.

    Returns:
        A dict mapping difficulty name (``str``) to best score (``int``),
        e.g. ``{"Easy": 80, "Normal": 60}``.  Empty dict if no scores saved.
    """
    if not os.path.exists(HIGHSCORE_FILE):
        return {}
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_high_score(difficulty: str, score: int) -> dict:
    """Persist a score if it beats the current high score for that difficulty.

    Reads the existing high-score table, updates the entry for *difficulty*
    only when *score* exceeds the stored value, then writes the table back to
    :data:`HIGHSCORE_FILE`.

    Args:
        difficulty: The difficulty level the score was achieved on
            (e.g. ``"Easy"``, ``"Normal"``, ``"Hard"``).
        score: The score to compare against the stored high score.

    Returns:
        The updated high-score dict (whether or not a new record was set).
    """
    scores = load_high_scores()
    if score > scores.get(difficulty, 0):
        scores[difficulty] = score
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(scores, f)
    return scores


# FIX: Refactored from app.py into logic_utils.py (GitHub Copilot Agent Mode).
# Extracted score calculation logic for cleaner app.py and testability.
def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate the new cumulative score after a single guess.

    Scoring rules:

    * **Win**: awards ``max(10, 100 - 10 * (attempt_number + 1))`` points,
      so earlier wins score higher.
    * **Too High**: awards ``+5`` on even-numbered attempts, ``-5`` on odd.
    * **Too Low**: deducts ``5`` points.
    * Any other outcome leaves the score unchanged.

    Args:
        current_score: The player's score before this guess.
        outcome: The outcome string returned by :func:`check_guess`
            (``"Win"``, ``"Too High"``, or ``"Too Low"``).
        attempt_number: The 1-based index of the current attempt.

    Returns:
        The updated cumulative score as an ``int``.

    Examples:
        >>> update_score(0, "Win", 1)
        70
        >>> update_score(0, "Too Low", 1)
        -5
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
