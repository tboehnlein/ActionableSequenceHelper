"""
Actionable Sequence Helper (ASH) Menu System

This module provides an interactive menu system for executing step-by-step recipes.
Recipes are defined in JSON files and can optionally have associated Python modules
for custom functionality.

USAGE:
    python ash_menu.py

    The program will scan the 'recipes' directory for .json files and display them
    in an interactive menu. Users can select recipes by number or name.

RECIPE FORMAT:
    v1.0 (Legacy - array format):
    [
        {"title": "Recipe Name", "description": "What it does"},
        {"statement": "First step - just text"},
        {
            "statement": "Second step - calls a function",
            "function_name": "my_function",
            "prompt_for": {"param": "Enter value for param"}
        }
    ]
    
    v1.1 (Current - flat object format):
    {
        "version": "1.1",
        "title": "Recipe Name",
        "description": "What it does",
        "color": "blue",          // Optional: for solid color, or "rainbow"
        "color_end": "green",     // Optional: for gradient effect with "color"
        "step1": {"statement": "First step - just text"},
        "step2": {
            "statement": "Second step - calls a function",
            "function_name": "my_function",
            "prompt_for": {"param": "Enter value for param"}
        }
    }

PYTHON MODULES:
    Optional Python files (same name as JSON) can provide custom functions:
    - Functions are called based on "function_name" in recipe steps
    - Parameters can be prompted from user via "prompt_for"
    - Special dependencies are auto-injected: 'console', 'run_tk_dialog', 'recipe_context'

MENU FEATURES:
    - Q: Quit the application
    - R: Refresh menu (useful after fixing recipe errors)
    - Number selection: Choose recipe by menu number
    - Name selection: Choose recipe by exact or partial name match
    - Error display: Shows LOAD ERROR for broken recipes before selection

DIRECTORY STRUCTURE:
    project/
    ├── ash_menu.py          # This file
    ├── execute_recipe.py    # Recipe execution engine
    └── recipes/             # Recipe directory
        ├── recipe1.json     # Recipe definition
        ├── recipe1.py       # Optional Python functions
        └── recipe2.json     # Another recipe
"""

import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.box import HEAVY, ROUNDED, HEAVY_HEAD
from rich.color import Color, ColorParseError
from rich.text import Text
import execute_recipe
import importlib.util
import inspect
import random
import time
from __version__ import __version__
import recipe_version
from extensions import rainbow_text, get_color_from_hue, gradient_text
from load_recipe import load_recipe_details, RECIPES_DIR

software_version = f"Actionable Sequence Helper (ASH) v{__version__}"
console = Console()

def format_menu_panels(menu_items_data):
    """
    Create a list of rich Panel objects for each recipe menu item, showing version info and LOAD ERROR if present.
    Applies recipe-defined color to the panel and title if specified.
    """
    panels = []
    for i, item in enumerate(menu_items_data):
        # Version info display - only show if not latest version or if there are errors
        version_info = item.get('version_info', 'unknown')
        version_display = ""
        if version_info != 'v1.1' or item.get('was_upgraded', False):
            version_display = f"\n[dim]{version_info}[/dim]"
            if item.get('was_upgraded', False):
                version_display += " [green]✓ Upgraded[/green]"

        # Error display
        error_text = f"\n[bold red]LOAD ERROR:\n{item['load_error']}[/bold red]" if 'load_error' in item else ""

        # Get color from recipe, default to white if not specified or invalid
        color_str = item.get("color", "white")
        color_end_str = item.get("color_end")
        
        if color_end_str:
            try:
                # Validate both colors before creating gradient
                Color.parse(color_str)
                Color.parse(color_end_str)
                title_text = gradient_text(f"{i+1}.) {item['title']}", start_color=color_str, end_color=color_end_str)
                title_text.stylize("bold")
                border_color = color_str
                panel_content = Text.assemble(
                    title_text,
                    f"\n{item['description']}{version_display}{error_text}"
                )
                panels.append(Panel(panel_content, expand=True, border_style=border_color))
            except ColorParseError:
                # Fallback for invalid gradient colors to solid white
                panel_content = (
                    f"[bold white]{i+1}.) {item['title']}[/bold white]\n"
                    f"{item['description']}{version_display}{error_text}"
                )
                panels.append(Panel(panel_content, expand=True, border_style="white"))
        elif color_str.lower() == "rainbow":
            # Each rainbow recipe gets a unique, random starting color for its gradient.
            start_hue = random.random()
            time.sleep(0.05) # Add a small pause to ensure random.random() gets a different seed if called rapidly            
            title_text = rainbow_text(f"{i+1}.) {item['title']}", start_hue=start_hue)
            title_text.stylize("bold")

            # The border color will be the starting color of the rainbow gradient.
            border_color = get_color_from_hue(start_hue)

            panel_content = Text.assemble(
                title_text,
                f"\n{item['description']}{version_display}{error_text}"
            )
            panels.append(Panel(panel_content, expand=True, border_style=border_color))
        else:
            valid_color = "white"
            if isinstance(color_str, str):
                try:
                    # Use rich's own parser to validate the color.
                    # This supports names, hex, rgb, etc.
                    Color.parse(color_str)
                    valid_color = color_str
                except ColorParseError:
                    pass  # valid_color is already "white"
            
            panel_content = (
                f"[bold {valid_color}]{i+1}.) {item['title']}[/bold {valid_color}]\n"
                f"{item['description']}{version_display}{error_text}"
            )
            panels.append(Panel(panel_content, expand=True, border_style=valid_color))
    return panels



def find_recipe_by_choice(choice, menu_items_data):
    """
    Find a recipe by user input (number, exact name, or partial match).

    Parameters:
        choice (str): User input from the menu prompt.
        menu_items_data (list of dict): List of recipe metadata dicts.

    Returns:
        tuple: (selected_recipe_data, error_message)
            selected_recipe_data (dict or None): The matched recipe dict, or None if not found.
            error_message (str or None): Error message to display, or None if no error.
    """
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(menu_items_data):
            return menu_items_data[idx], None
        else:
            return None, "[bold red]Invalid number. Please try again.[/bold red]"
    # Exact match (case-insensitive)
    found_matches = [item for item in menu_items_data if choice.lower() == item['title'].lower()]
    if len(found_matches) == 1:
        return found_matches[0], None
    # Partial match (case-insensitive)
    found_matches = [item for item in menu_items_data if choice.lower() in item['title'].lower()]
    if len(found_matches) == 1:
        return found_matches[0], None
    elif len(found_matches) > 1:
        msg = "[bold yellow]Multiple matches found. Please be more specific:[/bold yellow]\n" + "\n".join(f"- {match['title']}" for match in found_matches)
        return None, msg
    else:
        return None, "[bold red]Recipe not found. Please try again.[/bold red]"

def show_recipe_info(selected_recipe_data):
    """
    Print the selected recipe's title and description.

    Parameters:
        selected_recipe_data (dict): The selected recipe metadata dict.
    """
    console.print(f"[bold green]Selected recipe:[/bold green] [cyan]{selected_recipe_data['title']}[/cyan]")
    console.print(f"[bold green]Description:[/bold green] [cyan]{selected_recipe_data.get('description', 'No description available.')}[/cyan]")

def show_menu_display(menu_items_data):
    """Display the formatted recipe menu."""
    menu_panels = format_menu_panels(menu_items_data)
    menu_columns = Columns(menu_panels, expand=True)
    console.print(Panel(
        menu_columns,
        title=f"[bold blue]Welcome to {software_version}![/bold blue]",
        border_style="blue",
        box=HEAVY,
        subtitle="Enter Q to quit, R to refresh, or V for version info."
    ))

def get_user_choice():
    """Get and return user input from the menu prompt."""
    return console.input("[bold green]Enter recipe number, name, R to refresh, V for version info, or Q to quit: [/bold green]").strip()

def handle_recipe_selection(selected_recipe_data, recipes_data):
    """Execute the selected recipe and handle any errors."""
    show_recipe_info(selected_recipe_data)
    module_name = os.path.splitext(selected_recipe_data['filename'])[0]
    module_path = os.path.join(RECIPES_DIR, f"{module_name}.py")
    recipe_filename = selected_recipe_data['filename']
    
    # Get the execution-ready recipe data
    execution_recipe = recipes_data.get(recipe_filename)
    if not execution_recipe:
        console.print("[bold red]Error: Recipe data not found[/bold red]")
        return True
    
    try:
        # Use the execution engine with the normalized recipe data
        execute_recipe.run_recipe_from_data(execution_recipe, module_path)
    except SystemExit:
        return False  # Exit the menu
    except Exception as e:
        console.print(f"[bold red]Fatal error running recipe: {e}[/bold red]")
        return False  # Exit the menu
    return True  # Continue menu loop

def display_menu():
    """Display the interactive recipe selection menu and handle user input."""
    while True:
        # Load and display menu
        recipe_files = [f for f in os.listdir(RECIPES_DIR) if f.endswith(".json")]
        menu_items_data, recipes_data = load_recipe_details(recipe_files, console)
        show_menu_display(menu_items_data)
        
        # Get user input
        choice = get_user_choice()
        
        # Handle special commands
        if choice.lower() == 'q':
            console.print(f"[bold yellow]Exiting {software_version}. Goodbye![/bold yellow]")
            break
        if choice.lower() == 'r':
            continue  # Refresh menu
        if choice.lower() == 'v':
            recipe_version.show_version_info()
            console.input("\n[dim]Press Enter to return to menu...[/dim]")
            continue
        
        # Handle recipe selection
        selected_recipe_data, error_message = find_recipe_by_choice(choice, menu_items_data)
        if error_message:
            console.print(error_message)
            continue
            
        if selected_recipe_data:
            if 'load_error' in selected_recipe_data:
                console.print("[bold red]Cannot run recipe with load errors:[/bold red]")
                console.print(f"[red]{selected_recipe_data['load_error']}[/red]")
                console.input("\n[dim]Press Enter to return to menu...[/dim]")
                continue

            if not handle_recipe_selection(selected_recipe_data, recipes_data):
                break  # Exit if recipe execution requests it

def main():
    """
    Entry point for the ASH menu application.

    Parameters:
        None

    Returns:
        None
    """
    display_menu()

if __name__ == "__main__":
    main()
