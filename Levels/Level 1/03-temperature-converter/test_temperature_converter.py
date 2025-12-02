#!/usr/bin/env python3
"""
Unit tests for Temperature Converter
"""

from temperature_converter import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    celsius_to_kelvin,
    kelvin_to_celsius,
    fahrenheit_to_kelvin,
    kelvin_to_fahrenheit,
    format_temperature,
)


def test_celsius_to_fahrenheit():
    """Test Celsius to Fahrenheit conversion."""
    # Test freezing point
    assert celsius_to_fahrenheit(0) == 32.0

    # Test boiling point
    assert celsius_to_fahrenheit(100) == 212.0

    # Test room temperature
    assert celsius_to_fahrenheit(20) == 68.0


def test_fahrenheit_to_celsius():
    """Test Fahrenheit to Celsius conversion."""
    # Test freezing point
    assert fahrenheit_to_celsius(32) == 0.0

    # Test boiling point
    assert fahrenheit_to_celsius(212) == 100.0

    # Test room temperature
    assert fahrenheit_to_celsius(68) == 20.0


def test_celsius_to_kelvin():
    """Test Celsius to Kelvin conversion."""
    # Test absolute zero
    assert celsius_to_kelvin(-273.15) == 0.0

    # Test freezing point
    assert celsius_to_kelvin(0) == 273.15

    # Test room temperature
    assert celsius_to_kelvin(20) == 293.15


def test_kelvin_to_celsius():
    """Test Kelvin to Celsius conversion."""
    # Test absolute zero
    assert kelvin_to_celsius(0) == -273.15

    # Test freezing point
    assert kelvin_to_celsius(273.15) == 0.0

    # Test room temperature
    assert kelvin_to_celsius(293.15) == 20.0


def test_fahrenheit_to_kelvin():
    """Test Fahrenheit to Kelvin conversion."""
    # Test absolute zero
    assert abs(fahrenheit_to_kelvin(-459.67) - 0.0) < 0.01

    # Test freezing point
    assert abs(fahrenheit_to_kelvin(32) - 273.15) < 0.01


def test_kelvin_to_fahrenheit():
    """Test Kelvin to Fahrenheit conversion."""
    # Test absolute zero
    assert abs(kelvin_to_fahrenheit(0) - (-459.67)) < 0.01

    # Test freezing point
    assert abs(kelvin_to_fahrenheit(273.15) - 32.0) < 0.01


def test_format_temperature():
    """Test temperature formatting."""
    assert format_temperature(25.5, "C") == "25.50°C"
    assert format_temperature(77.0, "F") == "77.00°F"
    assert format_temperature(298.15, "K") == "298.15°K"


def test_round_trip_conversions():
    """Test that conversions are reversible."""
    # Test Celsius <-> Fahrenheit
    original_c = 25.0
    converted_f = celsius_to_fahrenheit(original_c)
    back_to_c = fahrenheit_to_celsius(converted_f)
    assert abs(original_c - back_to_c) < 0.01

    # Test Celsius <-> Kelvin
    original_c = 25.0
    converted_k = celsius_to_kelvin(original_c)
    back_to_c = kelvin_to_celsius(converted_k)
    assert abs(original_c - back_to_c) < 0.01

    # Test Fahrenheit <-> Kelvin
    original_f = 77.0
    converted_k = fahrenheit_to_kelvin(original_f)
    back_to_f = kelvin_to_fahrenheit(converted_k)
    assert abs(original_f - back_to_f) < 0.01


if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running basic tests...")

    try:
        test_celsius_to_fahrenheit()
        print("[PASS] Celsius to Fahrenheit conversion test passed")

        test_fahrenheit_to_celsius()
        print("[PASS] Fahrenheit to Celsius conversion test passed")

        test_celsius_to_kelvin()
        print("[PASS] Celsius to Kelvin conversion test passed")

        test_kelvin_to_celsius()
        print("[PASS] Kelvin to Celsius conversion test passed")

        test_fahrenheit_to_kelvin()
        print("[PASS] Fahrenheit to Kelvin conversion test passed")

        test_kelvin_to_fahrenheit()
        print("[PASS] Kelvin to Fahrenheit conversion test passed")

        test_format_temperature()
        print("[PASS] Temperature formatting test passed")

        test_round_trip_conversions()
        print("[PASS] Round-trip conversion tests passed")

        print("\nAll tests passed!")

    except AssertionError as e:
        print(f"[FAIL] Test failed: {e}")
    except Exception as e:
        print(f"[FAIL] Error running tests: {e}")
