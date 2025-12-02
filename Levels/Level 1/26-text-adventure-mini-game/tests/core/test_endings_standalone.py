#!/usr/bin/env python3
"""Standalone test helper for ending determination logic without pygame dependencies."""

from core.endings import evaluate_condition, determine_ending


class MockWorld:
    """Mock world class for testing."""

    def __init__(self):
        self.flags = {}

    def set_flag(self, name, value):
        self.flags[name] = value

    def get_flag(self, name):
        return self.flags.get(name, False)


def test_condition_evaluation():
    """Test the condition evaluator directly."""
    world = MockWorld()

    print("Testing condition evaluation...")
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


def test_ending_scenarios():
    """Test representative flag combinations to ensure correct ending selection."""
    world = MockWorld()

    test_cases = [
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

    print("\nTesting ending determination logic...")
    print("=" * 50)

    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        # Clear all flags first
        world.flags.clear()

        # Set test flags
        for flag_name, flag_value in test_case["flags"].items():
            world.set_flag(flag_name, flag_value)

        # Test ending determination directly
        actual_ending = determine_ending(world)
        expected_ending = test_case["expected"]

        status = "PASS" if actual_ending == expected_ending else "FAIL"
        print(f"Test {i}: {test_case['name']}")
        print(f"  Expected: {expected_ending}, Got: {actual_ending} [{status}]")

        if actual_ending != expected_ending:
            all_passed = False
            print(f"  Flags set: {test_case['flags']}")

    print("=" * 50)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed!")

    return all_passed


if __name__ == "__main__":
    try:
        test_condition_evaluation()
        success = test_ending_scenarios()
        exit(0 if success else 1)
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
