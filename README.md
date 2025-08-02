# Actionable Sequence Helper (ASH)

ASH is a flexible, command-line tool designed to guide users through a series of steps defined in "recipes." It's perfect for standardizing complex workflows, creating interactive checklists, or automating multi-step processes that require user input or actions at specific points.

## Features

*   **Recipe-Driven Workflow**: Define a sequence of steps in simple JSON files.
*   **Interactive Steps**: Recipes can be simple checklists or can execute custom Python code.
*   **Dynamic Code Loading**: Automatically loads and runs functions from a Python file associated with your recipe.
*   **User-Friendly Interface**: Built with `rich` for a clean, modern terminal experience.
*   **GUI Integration**: Provides a safe, built-in helper to launch GUI dialogs (like file pickers) from your recipes.
*   **Private Recipe Management**: Designed to keep your personal recipes separate from the main application repository.

## Getting Started

To run the application, simply execute the `ash_menu.py` script from your terminal:

```bash
python ash_menu.py
```

This will display a menu of all available recipes found in the `recipes/` directory.

## How It Works: The Recipe System

ASH is built around the concept of **recipes**. A recipe consists of two parts:

1.  **A JSON file (`.json`)**: This is the core of the recipe. It defines the sequence of steps, including the instructions to show the user and (optionally) the name of a Python function to run.
2.  **A Python file (`.py`)**: This file is **optional**. It contains the actual Python functions that are called by the recipe steps. If a recipe is just a simple checklist, you don't need a `.py` file.

When you select a recipe from the menu, the controller reads the JSON file and proceeds step-by-step, displaying the instructions and executing any associated code.

## Creating Your Own Recipes

To create a new recipe, you'll typically create two files in the `recipes/` directory: `my_recipe.json` and `my_recipe.py`.

### The Recipe JSON File (`my_recipe.json`)

The JSON file is a list of steps. The first item in the list is special; it contains the `title` and `description` for the menu. Subsequent items are the steps themselves.

**Key fields for a step:**
*   `statement`: The instruction or information to display to the user for this step.
*   `function_name` (optional): The name of the function to run from the corresponding `.py` file.
*   `prompt_for` (optional): A dictionary to prompt the user for input. The key is the function parameter name, and the value is the prompt text.

**Example: `crash.json`**
```json
[
    {
        "title": "Crash Course Recipe",
        "description": "A simple recipe to test file selection."
    },
    {
        "statement": "This step will open a file dialog. Please provide a title for the window.",
        "function_name": "OpenFileWindow",
        "prompt_for": {
            "title": "Enter the title for the file window"
        }
    },
    {
        "statement": "Recipe complete! You can add more steps here.",
        "function_name": null
    }
]
```

### The Recipe Code File (`crash.py`)

This file contains the functions your recipe will execute.

**Example: `crash.py`**
```python
from tkinter import filedialog
from rich.console import Console

def OpenFileWindow(title: str, console: Console, run_tk_dialog):
    """
    Opens a file dialog window using the injected utility.
    """
    # Use the injected helper to run the dialog
    file_path = run_tk_dialog(filedialog.askopenfilename, title=title)
    
    if file_path:
        console.print(f"[bold green]Selected file:[/] [italic white]{file_path}[/italic white]")
        return True  # Returning True signals success
    else:
        console.print("[bold red]No file selected.[/bold red]")
        return False # Returning False signals failure
```

### Injected Dependencies

To make recipe creation easier and safer, the controller can automatically "inject" helpful utilities into your functions if they are listed as parameters:

*   `console`: The application's `rich.console.Console` object for consistent, styled output.
*   `run_tk_dialog`: A safe wrapper for running `tkinter` dialogs. It handles creating and destroying the `tkinter` root window and ensures the dialog appears on top of other windows.

## Managing Your Recipes Privately

The main ASH repository is designed to be public, but your recipes might be private. The project is set up to support this workflow easily.

The root `.gitignore` file is configured to ignore the entire `/recipes/` directory. This allows you to create a completely separate, private Git repository inside the `recipes` folder.

1.  **Ignore `/recipes/`**: The main repo's `.gitignore` already does this.
2.  **Create a private repo**: Create a new private repository on GitHub (e.g., `my-ash-recipes`).
3.  **Initialize Git in `recipes/`**:
    ```bash
    cd recipes
    git init
    git remote add origin <your_private_repo_url>
    git add .
    git commit -m "Initial commit"
    git push -u origin main
    ```

Now you can manage your application code and your private recipes in two different repositories, even though they live in the same project folder on your local machine.