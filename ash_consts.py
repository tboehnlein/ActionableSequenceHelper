"""
Actionable Sequence Helper (ASH) Constants

This module defines shared constants used across the application to ensure
consistency and ease of maintenance.
"""
import os
from rich.console import Console

# The absolute path to the 'recipes' directory.
RECIPES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes")

# The current version of the recipe format.
CURRENT_RECIPE_VERSION = "1.1"

# A shared console object for consistent output across the application.
console = Console()
