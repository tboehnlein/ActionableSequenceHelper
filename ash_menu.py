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
    """Loads recipe details from files for menu display."""
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

def display_menu():
    recipe_files = [f for f in os.listdir(RECIPES_DIR) if f.endswith(".json")]
    
    menu_items_data, _ = load_recipe_details(recipe_files)
    
    menu_panels = [
        Panel(f"[bold]{i+1}.) {item['title']}[/bold]\n{item['description']}", expand=True)
        for i, item in enumerate(menu_items_data)
    ]
    
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
        
        selected_recipe_path = None
        selected_recipe_data = None

        # Try to match by number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(menu_items_data):
                selected_recipe_data = menu_items_data[idx]
                selected_recipe_path = os.path.join(RECIPES_DIR, selected_recipe_data['filename'])
            else:
                console.print("[bold red]Invalid number. Please try again.[/bold red]")
                continue
        # Try to match by name
        else:
            # Check for exact match first (case-insensitive on title)
            found_matches = [item for item in menu_items_data if choice.lower() == item['title'].lower()]
            if len(found_matches) == 1:
                 selected_recipe_data = found_matches[0]
                 selected_recipe_path = os.path.join(RECIPES_DIR, selected_recipe_data['filename'])
            else:
                # Check for partial match (case-insensitive on title)
                found_matches = [item for item in menu_items_data if choice.lower() in item['title'].lower()]
                if len(found_matches) == 1:
                    selected_recipe_data = found_matches[0]
                    selected_recipe_path = os.path.join(RECIPES_DIR, selected_recipe_data['filename'])
                elif len(found_matches) > 1:
                    console.print("[bold yellow]Multiple matches found. Please be more specific:[/bold yellow]")
                    for match in found_matches:
                        console.print(f"- {match['title']}")
                    continue
                else:
                    console.print("[bold red]Recipe not found. Please try again.[/bold red]")
                    continue

        if selected_recipe_path:
            console.print(f"[bold green]Selected recipe:[/bold green] [cyan]{selected_recipe_data['title']}[/cyan]")
            console.print(f"[bold green]Description:[/bold green] [cyan]{selected_recipe_data.get('description', 'No description available.')}[/cyan]")
            
            # Construct the path to the corresponding Python module
            module_name = os.path.splitext(selected_recipe_data['filename'])[0]
            module_path = os.path.join(RECIPES_DIR, f"{module_name}.py")
            
            controller.run_recipe(selected_recipe_path, module_path)
            # After running a recipe, display the menu again
            display_menu() # This will re-display the menu and prompt for input again
            break # Exit the current loop to prevent re-prompting after a recipe runs

def main():
    display_menu()

if __name__ == "__main__":
    main()
