from rock_paper_scissors import determine_outcome, format_scoreboard, normalize_choice


def test_determine_outcome_win():
    assert determine_outcome("rock", "scissors") == "win"


def test_determine_outcome_tie():
    assert determine_outcome("paper", "paper") == "tie"


def test_normalize_choice_accepts_shortcuts():
    assert normalize_choice("R") == "rock"


def test_format_scoreboard_layout():
    scoreboard = {"player": 2, "computer": 1, "ties": 3}
    assert format_scoreboard(scoreboard) == "Player: 2 | Computer: 1 | Ties: 3"
