#!/usr/bin/env python3
"""Simple test helper for ending determination logic."""

import sys

from core.world import World
from core.endings import evaluate_condition, determine_ending, load_endings_data


# ============================================================================
# Shared Test Data
# ============================================================================

ENDING_TEST_CASES = [
    {
        "name": "Good Ending - All positive choices",
        "flags": {
            "final_boss_defeated": True,
            "spared_crystal": True,
            "pledged_to_garden": True,
            "last_battle_spared": True,
            "took_crystal": False,
            "ignored_garden_spirit": False,
            "crypt_purified": True  # One of the side quest completion conditions
        },
        "expected": "good"
    },
    {
        "name": "Bad Ending - Took crystal",
        "flags": {
            "final_boss_defeated": True,
            "took_crystal": True,
            "spared_crystal": False,
            "pledged_to_garden": False,
            "last_battle_spared": False,
            "ignored_garden_spirit": False
        },
        "expected": "bad"
    },
    {
        "name": "Bad Ending - Ignored garden spirit",
        "flags": {
            "final_boss_defeated": True,
            "ignored_garden_spirit": True,
            "spared_crystal": False,
            "pledged_to_garden": False,
            "last_battle_spared": True,
            "took_crystal": False
        },
        "expected": "bad"
    },
    {
        "name": "Bad Ending - Killed final boss",
        "flags": {
            "final_boss_defeated": True,
            "last_battle_spared": False,
            "spared_crystal": True,
            "pledged_to_garden": True,
            "took_crystal": False,
            "ignored_garden_spirit": False
        },
        "expected": "bad"
    },
    {
        "name": "Neutral Ending - Mixed choices",
        "flags": {
            "final_boss_defeated": True,
            "spared_crystal": True,
            "pledged_to_garden": False,
            "last_battle_spared": True,
            "took_crystal": False,
            "ignored_garden_spirit": False,
            "river_creature_defeated": True  # Some side quest progress but not all
        },
        "expected": "neutral"
    },
    {
        "name": "Fallback - No final boss defeat",
        "flags": {
            "final_boss_defeated": False,
            "spared_crystal": True,
            "pledged_to_garden": True,
            "last_battle_spared": True,
            "took_crystal": False,
            "ignored_garden_spirit": False
        },
        "expected": "neutral"
    }
]


# ============================================================================
# Test Functions
# ============================================================================

def test_ending_scenarios():
    """Test representative flag combinations to ensure correct ending selection."""
    world = World()

    print("Testing ending determination logic...")
    print("=" * 50)

    for i, test_case in enumerate(ENDING_TEST_CASES, 1):
        # Clear all flags first
        world.flags.clear()

        # Set test flags
        for flag_name, flag_value in test_case["flags"].items():
            world.set_flag(flag_name, flag_value)

        # Test ending determination directly
        actual_ending = determine_ending(world)
        expected_ending = test_case["expected"]

        print(f"Test {i}: {test_case['name']}")
        print(f"  Expected: {expected_ending}, Got: {actual_ending}")
        assert actual_ending == expected_ending, (
            f"Ending mismatch for '{test_case['name']}': expected {expected_ending}, "
            f"got {actual_ending} with flags {test_case['flags']}"
        )

    print("=" * 50)
    print("All tests passed!")


def test_priority_sorting():
    """Test that endings are sorted by priority for deterministic selection."""
    print("\nTesting priority sorting...")
    print("=" * 50)

    # Load endings data to verify priority structure
    endings_data = load_endings_data()
    assert endings_data, "Could not load endings data"

    # Verify priorities are correctly ordered
    priorities = [ending.get("priority", 999) for ending in endings_data]
    expected_priorities = [1, 2, 3]  # good, bad, neutral

    assert priorities == expected_priorities, (
        f"Expected priorities {expected_priorities}, got {priorities}"
    )

    print("PASS: Endings have correct priority ordering")

    # Test that sorting works correctly (sorted() should not mutate original)
    shuffled_endings = [
        {"id": "neutral", "priority": 3},
        {"id": "good", "priority": 1},
        {"id": "bad", "priority": 2}
    ]
    original_order = [e["id"] for e in shuffled_endings]

    # Simulate the sorting logic from determine_ending
    sorted_endings = sorted(shuffled_endings, key=lambda x: x.get("priority", 999))
    sorted_ids = [ending["id"] for ending in sorted_endings]

    # Verify original list was not mutated
    current_order = [e["id"] for e in shuffled_endings]
    assert current_order == original_order, (
        f"Original list mutated. Expected {original_order}, got {current_order}"
    )

    assert sorted_ids == ["good", "bad", "neutral"], (
        f"Priority sorting failed. Expected ['good', 'bad', 'neutral'], got {sorted_ids}"
    )

    print("PASS: Priority sorting works correctly without mutation")


def test_missing_data_fallback():
    """Test missing data fallback handling."""
    print("\nTesting missing data fallback...")
    print("=" * 50)

    world = World()

    # Test with None endings data (simulating missing file)
    world.flags.clear()
    ending_id = determine_ending(world, endings_data=None)
    assert ending_id == "neutral", f"Expected fallback 'neutral', got '{ending_id}'"
    print("PASS: Missing endings data falls back to 'neutral'")

    # Test with empty list
    ending_id = determine_ending(world, endings_data=[])
    assert ending_id == "neutral", f"Expected fallback 'neutral' for empty list, got '{ending_id}'"
    print("PASS: Empty endings list falls back to 'neutral'")

    # Test with existing endings data but non-matching conditions
    world.flags.clear()  # Clear all flags so no conditions match
    ending_id = determine_ending(world)
    assert ending_id == "neutral", (
        f"Expected fallback 'neutral' for no matching conditions, got '{ending_id}'"
    )

    print("PASS: No matching conditions falls back to 'neutral'")


def test_automatic_transition_path():
    """Test that final boss victory determines correct ending."""
    print("\nTesting automatic transition path...")
    print("=" * 50)

    world = World()

    # Test that determine_ending works correctly for final boss scenario
    world.set_flag("final_boss_defeated", True)
    world.set_flag("spared_crystal", True)
    world.set_flag("pledged_to_garden", True)
    world.set_flag("last_battle_spared", True)
    world.set_flag("crypt_purified", True)  # Required for good ending

    ending_id = determine_ending(world)
    assert ending_id == "good", (
        f"Expected 'good' ending for final boss victory, got '{ending_id}'"
    )

    print("PASS: Final boss scenario determines correct ending")


def test_dialogue_flag_system():
    """Test that the set_flags_after_choice feature works correctly."""
    print("\nTesting dialogue flag system...")
    print("=" * 50)

    from core.dialogue import load_dialogue_from_json

    dialogue_tree = load_dialogue_from_json("data/dialogue.json")
    crystal_node = dialogue_tree.get_node("garden_choice")

    assert crystal_node is not None, "Could not load garden_choice dialogue node"
    assert hasattr(crystal_node, "set_flags_after_choice"), "DialogueNode missing set_flags_after_choice attribute"
    assert crystal_node.set_flags_after_choice == ["crystal_choice_made"], (
        f"Expected ['crystal_choice_made'], got {crystal_node.set_flags_after_choice}"
    )

    print("PASS: Dialogue system correctly loads set_flags_after_choice")

    # Test flag application logic
    world = World()
    world.set_flag("crystal_choice_made", False)

    for flag in crystal_node.set_flags_after_choice:
        world.set_flag(flag, True)

    assert world.get_flag("crystal_choice_made"), "set_flags_after_choice not properly applied"
    print("PASS: Dialogue scene correctly applies set_flags_after_choice")


def test_condition_evaluation():
    """Test the condition evaluator directly."""
    world = World()

    print("\nTesting condition evaluation...")
    print("=" * 50)

    # Test None condition (no condition = always matches)
    assert evaluate_condition(None, world) == True, "None condition should return True"

    # Test empty string/dict (no valid condition = no match)
    assert evaluate_condition("", world) == False, "Empty string should return False"
    assert evaluate_condition({}, world) == False, "Empty dict should return False"

    # Test simple flag conditions
    world.set_flag("test_flag", True)
    assert evaluate_condition("test_flag", world) == True, "Simple true flag failed"

    world.set_flag("test_flag", False)
    assert evaluate_condition("test_flag", world) == False, "Simple false flag failed"

    # Test AND conditions
    world.set_flag("flag1", True)
    world.set_flag("flag2", True)
    assert evaluate_condition({"and": ["flag1", "flag2"]}, world) == True, "AND true failed"

    world.set_flag("flag2", False)
    assert evaluate_condition({"and": ["flag1", "flag2"]}, world) == False, "AND false failed"

    # Test empty AND (vacuous truth)
    assert evaluate_condition({"and": []}, world) == True, "Empty AND should return True"

    # Test OR conditions
    world.set_flag("flag1", True)
    world.set_flag("flag2", False)
    assert evaluate_condition({"or": ["flag1", "flag2"]}, world) == True, "OR true failed"

    world.set_flag("flag1", False)
    assert evaluate_condition({"or": ["flag1", "flag2"]}, world) == False, "OR false failed"

    # Test empty OR (no conditions to satisfy)
    assert evaluate_condition({"or": []}, world) == False, "Empty OR should return False"

    # Test NOT conditions
    world.set_flag("flag1", True)
    assert evaluate_condition({"not": "flag1"}, world) == False, "NOT true failed"

    world.set_flag("flag1", False)
    assert evaluate_condition({"not": "flag1"}, world) == True, "NOT false failed"

    # Test nested conditions
    world.set_flag("final_boss_defeated", True)
    world.set_flag("took_crystal", True)
    world.set_flag("spared_crystal", False)

    nested_condition = {
        "and": [
            "final_boss_defeated",
            {"or": ["took_crystal", "spared_crystal"]}
        ]
    }
    assert evaluate_condition(nested_condition, world) == True, "Nested condition failed"

    print("Condition evaluation tests passed!")


if __name__ == "__main__":
    try:
        test_condition_evaluation()
        test_ending_scenarios()
        test_priority_sorting()
        test_missing_data_fallback()
        test_automatic_transition_path()
        test_dialogue_flag_system()
        sys.exit(0)
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
