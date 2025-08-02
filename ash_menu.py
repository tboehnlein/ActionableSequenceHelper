import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
import controller

software_version = "Actionable Sequence Helper (ASH) v1.0"
console = Console()
RECIPES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes")

def load_recipe_details(recipe_files):
    """
    Loads recipe details from JSON files for menu display.

    Parameters:
        recipe_files (list of str): List of recipe JSON filenames in the recipes directory.

    Returns:
        tuple: (menu_items, recipes_data)
            menu_items (list of dict): Each dict contains filename, title, and description for a recipe.
            recipes_data (dict): Mapping of filename to loaded recipe data.
    """
    menu_items = []
    recipes_data = {}
    for i, recipe_file in enumerate(recipe_files):
        try:
            recipe_path = os.path.join(RECIPES_DIR, recipe_file)
            with open(recipe_path, 'r') as f:
                recipe = json.load(f)
                recipes_data[recipe_file] = recipe
                if recipe and isinstance(recipe, list) and len(recipe) > 0:
                    title = recipe[0].get('title', f"Recipe {i + 1}")
                    description = recipe[0].get('description', "No description available.")
                    menu_items.append({
                        "filename": recipe_file,
                        "title": title,
                        "description": description
                    })
                else:
                    menu_items.append({
                        "filename": recipe_file,
                        "title": f"{recipe_file} - No valid steps found.",
                        "description": ""
                    })
        except Exception as e:
            console.print(f"[bold red]Error reading {recipe_file}: {e}[/bold red]")
            menu_items.append({
                "filename": recipe_file,
                "title": f"{recipe_file} - Error loading",
                "description": str(e)
            })
    return menu_items, recipes_data

def format_menu_panels(menu_items_data):
    """
    Create a list of rich Panel objects for each recipe menu item.

    Parameters:
        menu_items_data (list of dict): List of recipe metadata dicts.

    Returns:
        list of Panel: Panels for display in the menu.
    """
    return [
        Panel(f"[bold]{i+1}.) {item['title']}[/bold]\n{item['description']}", expand=True)
        for i, item in enumerate(menu_items_data)
    ]

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

def display_menu():
    """
    Display the interactive recipe selection menu and handle user input.

    Parameters:
        None

    Returns:
        None
    """
    recipe_files = [f for f in os.listdir(RECIPES_DIR) if f.endswith(".json")]
    
    menu_items_data, _ = load_recipe_details(recipe_files)
    
    menu_panels = format_menu_panels(menu_items_data)
    
    # Let Rich handle the columns automatically
    menu_columns = Columns(menu_panels, expand=True)

    console.print(Panel(
        menu_columns,
        title=f"[bold blue]Welcome to {software_version}![/bold blue]",
        border_style="blue",
        subtitle="Enter Q to quit."
    ))

    while True:
        choice = console.input("[bold green]Enter recipe number, name, or Q to quit: [/bold green]").strip()

        if choice.lower() == 'q':
            console.print(f"[bold yellow]Exiting {software_version}. Goodbye![/bold yellow]")
            break
        
        selected_recipe_data, error_message = find_recipe_by_choice(choice, menu_items_data)
        if error_message:
            console.print(error_message)
            continue
        if selected_recipe_data:
            show_recipe_info(selected_recipe_data)
            module_name = os.path.splitext(selected_recipe_data['filename'])[0]
            module_path = os.path.join(RECIPES_DIR, f"{module_name}.py")
            controller.run_recipe(os.path.join(RECIPES_DIR, selected_recipe_data['filename']), module_path)
            display_menu() # Re-display the menu after running a recipe
            break

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
