"""
Actionable Sequence Helper (ASH) Recipe Controller

This module handles the execution of recipe files, managing the step-by-step process
of running recipes with optional Python function integration.

CORE FUNCTIONALITY:
    - Loads and parses JSON recipe files
    - Dynamically imports and executes Python functions
    - Handles user input prompting for function parameters
    - Provides dependency injection for common utilities
    - Manages step execution flow with retry logic

RECIPE EXECUTION FLOW:
    1. Load recipe JSON and optional Python module
    2. Display recipe title and initialize
    3. For each step:
       - Display step statement in formatted panel
       - Execute any associated function with parameter prompting
       - Handle success/failure/retry logic
       - Wait for user confirmation before next step

FUNCTION INTEGRATION:
    Recipe functions can receive injected dependencies:
    - 'console': Rich console object for formatted output
    - 'run_tk_dialog': Helper for tkinter file dialogs with proper focus
    
    Functions should return True for success, False for failure.
    Returning False allows the user to retry the step.

PARAMETER HANDLING:
    Functions can prompt for user input via recipe "prompt_for" fields:
    {
        "function_name": "my_function",
        "prompt_for": {
            "filename": "Enter the filename",
            "option": "Choose an option"
        }
    }
    
    Parameters are validated against the function signature before calling.

ERROR HANDLING:
    - Missing functions: Fatal error, aborts recipe
    - Function exceptions: Displays error, allows retry
    - Missing modules: Shows configuration error
    - Invalid JSON: Reports parsing errors

USAGE:
    This module is typically imported by ash_menu.py, but can be used directly:
    
    from execute_recipe import run_recipe
    run_recipe("path/to/recipe.json", "path/to/recipe.py")
"""

import json
import importlib.util
import os
import inspect
import tkinter as tk
from tkinter import filedialog
from rich.console import Console
from rich.panel import Panel
from __version__ import __version__

# console object for rich text output
console = Console()

def run_tk_dialog(dialog_func, *args, **kwargs):
    """
    Helper for recipe functions to run tkinter dialogs (like file choosers) 
    with proper window focus and cleanup.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # The dialog function (e.g., filedialog.askopenfilename) is called here
    result = dialog_func(*args, **kwargs)
    
    root.attributes('-topmost', False)
    root.destroy()
    
    return result

def load_recipe_json(recipe_path):
    """
    Load and parse the recipe JSON file.

    Parameters:
        recipe_path (str): Path to the recipe JSON file.

    Returns:
        list or None: Parsed recipe steps as a list, or None if loading fails.
    """
    try:
        with open(recipe_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Recipe file not found at [cyan]'{recipe_path}'[/cyan]")
        return None
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/] Could not decode JSON from [cyan]'{recipe_path}'[/cyan]")
        return None

def load_recipe_module(module_path):
    """
    Load the Python module associated with the recipe, if it exists.

    Parameters:
        module_path (str): Path to the Python module file.

    Returns:
        module or None: Loaded Python module, or None if not found or loading fails.
    """
    if os.path.exists(module_path):
        try:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                recipe_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(recipe_module)
                return recipe_module
            else:
                console.print(f"[bold yellow]Warning:[/] Could not create module spec for [cyan]'{module_path}'[/cyan].")
        except Exception as e:
            console.print(f"[bold yellow]Warning:[/] Failed to load module from [cyan]'{module_path}'[/cyan]: {e}")
    return None

def prompt_for_parameters(step, func_params):
    """
    Prompt the user for parameters specified in the step's 'prompt_for' dict.

    Parameters:
        step (dict): The current recipe step.
        func_params (OrderedDict): Parameters of the function to be called.

    Returns:
        dict or None: Dictionary of parameter values entered by the user, or None if configuration error.
    """
    call_args = {}
    if 'prompt_for' in step and isinstance(step['prompt_for'], dict):
        for param_name, prompt_text in step['prompt_for'].items():
            if param_name not in func_params:
                console.print(f"[bold red]Configuration Error:[/] Recipe wants to prompt for '{param_name}', but function has no such parameter.")
                return None
            while True:
                user_input = console.input(f"[cyan]{prompt_text}[/cyan]: ").strip()
                if user_input:
                    call_args[param_name] = user_input
                    break
                else:
                    console.print("[bold red]Input cannot be empty. Please try again.[/bold red]")
    return call_args

def inject_dependencies(call_args, func_params):
    """Inject standard dependencies into function call arguments."""
    if 'console' in func_params:
        call_args['console'] = console
    if 'run_tk_dialog' in func_params:
        call_args['run_tk_dialog'] = run_tk_dialog

def add_json_parameters(step, call_args, func_params):
    """Add any parameters from the JSON step that match function parameters."""
    for param_name, param_value in step.items():
        if param_name in func_params and param_name not in call_args:
            call_args[param_name] = param_value

def execute_step(step, recipe_module):
    """Execute a single step in the recipe, handling function calls and user prompts."""
    # Text-only steps are automatically successful
    if not step.get('function_name'):
        return True
    
    # Check if we have the required module
    if not recipe_module:
        console.print(f"\n[bold red]Configuration Error:[/] Step requires function '{step['function_name']}', but no code file was found.\n")
        return None
    
    try:
        func = getattr(recipe_module, step['function_name'])
        func_params = inspect.signature(func).parameters
        call_args = {}
        
        # Build function arguments
        inject_dependencies(call_args, func_params)
        
        prompt_args = prompt_for_parameters(step, func_params)
        if prompt_args is None:
            return False
        call_args.update(prompt_args)
        
        add_json_parameters(step, call_args, func_params)
        
        # Execute the function
        if func(**call_args):
            return True
        else:
            console.print("[bold yellow]The step failed. Please review the output and try again.[/bold yellow]\n")
            return False
            
    except AttributeError:
        console.print(f"\n[bold red]FATAL ERROR:[/] Function [yellow]'{step['function_name']}'[/yellow] not found in the module! Cannot proceed.\n")
        return None
    except Exception as e:
        console.print(f"\n[bold red]ERROR:[/] An unexpected error occurred in function '{step['function_name']}': {e}\n")
        return False

def show_recipe_header(title):
    """Display the recipe start banner."""
    console.print(f"[bold green]--- Starting Recipe [bold white]{title}[/bold white] ---[/bold green]")
    console.print("-" * 25)

def show_step(step_index, step):
    """Display a recipe step in a formatted panel."""
    console.print(Panel(
        f"{step.get('statement', '')}",
        title=f"[yellow bold]Step {step_index}[/yellow bold]",
        border_style="blue"
    ))

def run_single_step(step, recipe_module, step_index):
    """Run a single step with retry logic. Returns True if should continue recipe."""
    while True:
        result = execute_step(step, recipe_module)
        
        if result is None:  # Fatal error
            console.print("[bold red]Recipe execution aborted due to fatal error.[/bold red]")
            return False
        elif result:  # Success
            if step.get('prompt_for'):
                console.print(f"[bold green]Step {step_index} completed successfully![/bold green]")
            return True
        else:  # Failure, retry
            console.print("[bold yellow]Retrying step...[/bold yellow]")

def run_recipe(recipe_path: str, module_path: str):
    """Execute a recipe file step-by-step with user guidance."""
    recipe = load_recipe_json(recipe_path)
    if recipe is None:
        return
    
    recipe_module = load_recipe_module(module_path)
    title = recipe[0].get('title', 'Untitled Recipe')
    show_recipe_header(title)
    
    for step_index in range(1, len(recipe)):
        step = recipe[step_index]
        show_step(step_index, step)
        
        if not run_single_step(step, recipe_module, step_index):
            return  # Fatal error occurred
        
        if step_index < len(recipe) - 1:  # Not the last step
            console.input("\n[dim]Press Enter to continue...[/dim]")
    
    console.print("\n[bold green]--- Recipe Complete ---")

if __name__ == "__main__":
    # Example of how to run it directly (for testing)
    # You would need a recipe.json and a recipe.py in the same directory
    # run_recipe("recipe.json", "recipe.py")
    pass
