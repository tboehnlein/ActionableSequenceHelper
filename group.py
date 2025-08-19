"""
Group History Management for ASH

This module provides functions to manage the most-recently-used (MRU)
history for recipe groups. The history is stored in a JSON file and is
used by the main menu to display a preview of the most relevant recipes
for each group.

Functions:
    - read_group_history: Loads the MRU history from the JSON file.
    - write_group_history: Saves the MRU history to the JSON file.
    - update_group_history: Updates the MRU list for a specific group
      after a recipe is executed.
"""
import os
import json
from ash_consts import RECIPES_DIR, console

HISTORY_FILE = os.path.join(RECIPES_DIR, "group_history.json")
HISTORY_LIMIT = 5

def read_group_history() -> dict:
    """
    Reads the group history from group_history.json.

    Returns:
        dict: A dictionary containing the history data. Returns an empty
              dictionary if the file doesn't exist or is invalid.
    """
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        console.print(f"[yellow]Warning: Could not read or parse {os.path.basename(HISTORY_FILE)}. A new one will be created.[/yellow]")
        return {}

def write_group_history(history_data: dict):
    """Writes the provided history data to the group_history.json file."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2)
    except IOError as e:
        console.print(f"[bold red]Error writing to {os.path.basename(HISTORY_FILE)}: {e}[/bold red]")

def update_group_history(group_name: str, recipe_filename: str):
    """
    Updates the MRU list for a group, moving the recipe to the front.
    """
    if not group_name:
        return  # Cannot update history for an ungrouped recipe
    history = read_group_history()
    group_list = history.get(group_name, [])
    if recipe_filename in group_list:
        group_list.remove(recipe_filename)
    group_list.insert(0, recipe_filename)
    history[group_name] = group_list[:HISTORY_LIMIT]
    write_group_history(history)