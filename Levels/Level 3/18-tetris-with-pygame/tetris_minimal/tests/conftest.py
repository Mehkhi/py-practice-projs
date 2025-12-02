"""
Pytest configuration for headless testing.

Sets SDL_VIDEODRIVER=dummy before pygame initialization to enable
tests to run without a display device.
"""
import os

# Set dummy video driver before any pygame imports
os.environ['SDL_VIDEODRIVER'] = 'dummy'
