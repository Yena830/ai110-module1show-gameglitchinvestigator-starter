from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == ("Win", "🎉 Correct!")

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == ("Too High", "📉 Go LOWER!")

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == ("Too Low", "📈 Go HIGHER!")

# Bug fix: FIX - Corrected reversed high/low hint logic
# These tests ensure the bug where hints were reversed doesn't regress
def test_high_guess_returns_lower_hint():
    """When guess > secret, should return 'Go LOWER!' not 'Go HIGHER!'"""
    outcome, message = check_guess(100, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_low_guess_returns_higher_hint():
    """When guess < secret, should return 'Go HIGHER!' not 'Go LOWER!'"""
    outcome, message = check_guess(10, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

# Bug fix: FIX - Removed alternating str/int casting of secret
# This test ensures type comparison works correctly when secret is a different type
def test_check_guess_with_string_secret():
    """Ensure check_guess handles string secret correctly (no alternating type casting)"""
    # When secret is a string
    outcome, message = check_guess(50, "50")
    assert outcome == "Win"

# Edge cases for boundary conditions
def test_guess_at_lower_boundary():
    """Test guess at the lower bound (1)"""
    outcome, message = check_guess(1, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_guess_at_upper_boundary():
    """Test guess at a high boundary"""
    outcome, message = check_guess(100, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_off_by_one_low():
    """Test guess one below target"""
    outcome, message = check_guess(49, 50)
    assert outcome == "Too Low"

def test_off_by_one_high():
    """Test guess one above target"""
    outcome, message = check_guess(51, 50)
    assert outcome == "Too High"
