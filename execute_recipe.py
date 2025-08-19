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
    - 'recipe_context': Shared dictionary for storing data between steps
    
    Functions should return True for success, False for failure.
    Returning False allows the user to retry the step.

RECIPE CONTEXT:
    The recipe_context parameter provides a shared dictionary that persists
    throughout recipe execution. Functions can store and retrieve any data:
    
    def my_function(name, recipe_context, console):
        # Store data for later steps
        recipe_context['variables']['user_name'] = name
        recipe_context['files']['config_path'] = '/path/to/config'
        
        # Access data from previous steps
        if 'user_email' in recipe_context['variables']:
            email = recipe_context['variables']['user_email']
        
        return True

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
import traceback
from tkinter import filedialog
from rich.panel import Panel
from ash_consts import console

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

def inject_dependencies(call_args, func_params, recipe_context):
    """Inject standard dependencies into function call arguments."""
    if 'console' in func_params:
        call_args['console'] = console
    if 'run_tk_dialog' in func_params:
        call_args['run_tk_dialog'] = run_tk_dialog
    if 'recipe_context' in func_params:
        call_args['recipe_context'] = recipe_context

def add_json_parameters(step, call_args, func_params):
    """Add any parameters from the JSON step that match function parameters."""
    for param_name, param_value in step.items():
        # Skip internal properties that start with underscore
        if param_name.startswith('_'):
            continue
        if param_name in func_params and param_name not in call_args:
            call_args[param_name] = param_value

def execute_step(step, recipe_module, recipe_context=None):
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
        inject_dependencies(call_args, func_params, recipe_context)
        
        prompt_args = prompt_for_parameters(step, func_params)
        if prompt_args is None:
            return False
        call_args.update(prompt_args)
        
        add_json_parameters(step, call_args, func_params)
        
        # Execute the function
        result = func(**call_args)
        if result:
            return True
        else:
            console.print("[bold yellow]The step failed. Please review the output and try again.[/bold yellow]\n")
            return False
            
    except AttributeError:
        console.print(f"\n[bold red]FATAL ERROR:[/] Function [yellow]'{step['function_name']}'[/yellow] not found in the module! Cannot proceed.\n")
        return None
    except Exception as e:
        # Get traceback information for debugging
        tb = traceback.extract_tb(e.__traceback__)
        # Find the frame from the recipe module (not from execute_recipe.py)
        recipe_frame = None
        for frame in tb:
            if not frame.filename.endswith('execute_recipe.py'):
                recipe_frame = frame
                break
        
        error_msg = f"\n[bold red]FATAL ERROR:[/] An unexpected error occurred in function '{step['function_name']}':\n"
        error_msg += f"[red]{type(e).__name__}: {e}[/red]"
        
        if recipe_frame:
            filename = os.path.basename(recipe_frame.filename)
            error_msg += f"\n[yellow]File: {filename}, Line: {recipe_frame.lineno}[/yellow]"
            if recipe_frame.line:
                error_msg += f"\n[dim]Code: {recipe_frame.line.strip()}[/dim]"
        
        error_msg += "\n"
        console.print(error_msg)
        console.print("[bold red]Recipe execution will be aborted due to unhandled exception.[/bold red]\n")
        return None

def show_recipe_header(title):
    """Display the recipe start banner."""
    console.print(f"[bold green]--- Starting Recipe [bold white]{title}[/bold white] ---[/bold green]")
    console.print("-" * 25)

def show_step(step_index, step):
    """Display a recipe step in a formatted panel."""
    # Use the original step name if available, otherwise fall back to step number
    step_name = step.get('_step_name', f"Step {step_index}")
    
    console.print(Panel(
        f"{step.get('statement', '')}",
        title=f"[yellow bold]{step_name}[/yellow bold]",
        border_style="blue"
    ))

def run_single_step(step, recipe_module, step_index, recipe_context):
    """Run a single step with retry logic. Returns True if should continue recipe."""
    max_retries = 3
    retry_count = 0
    
    while retry_count <= max_retries:
        result = execute_step(step, recipe_module, recipe_context)
        
        if result is None:  # Fatal error
            console.print("[bold red]Recipe execution aborted due to fatal error.[/bold red]")
            console.input("\n[dim]Press Enter to return to the main menu...[/dim]")
            return False
        elif result:  # Success
            if step.get('prompt_for'):
                console.print(f"[bold green]Step {step_index} completed successfully![/bold green]")
            return True
        else:  # Failure, check if should retry
            retry_count += 1
            if retry_count <= max_retries:
                console.print(f"[bold yellow]Retrying step... (attempt {retry_count + 1}/{max_retries + 1})[/bold yellow]")
            else:
                console.print(f"[bold red]Step {step_index} failed after {max_retries + 1} attempts. Aborting recipe.[/bold red]")
                console.input("\n[dim]Press Enter to return to the main menu...[/dim]")
                return False

def run_recipe_from_data(recipe_data: list, module_path: str):
    """Execute a recipe from already-loaded data (used by versioning system)."""
    if recipe_data is None:
        return
    
    recipe_module = load_recipe_module(module_path)
    title = recipe_data[0].get('title', 'Untitled Recipe') if recipe_data else 'Untitled Recipe'
    
    # Initialize recipe context for sharing data between steps
    recipe_context = {
        'variables': {},      # General variable storage
        'files': {},         # File paths and handles
        'settings': {},      # Configuration data
        'results': {},       # Function return values
        'metadata': {        # Recipe metadata
            'title': title,
            'start_time': None,
            'current_step': 0
        }
    }
    
    show_recipe_header(title)
    
    for step_index in range(1, len(recipe_data)):
        step = recipe_data[step_index]
        recipe_context['metadata']['current_step'] = step_index
        show_step(step_index, step)
        
        if not run_single_step(step, recipe_module, step_index, recipe_context):
            return  # Fatal error occurred
        
        if step_index < len(recipe_data) - 1:  # Not the last step
            console.input("\n[dim]Press Enter to continue...[/dim]")
    
    console.print("\n[bold green]--- Recipe Complete ---[/bold green]")
    console.input("\n[dim]Press Enter to return to the main menu...[/dim]")

def run_recipe(recipe_path: str, module_path: str):
    """Execute a recipe file step-by-step with user guidance."""
    recipe = load_recipe_json(recipe_path)
    if recipe is None:
        return
    
    recipe_module = load_recipe_module(module_path)
    title = recipe[0].get('title', 'Untitled Recipe')
    
    # Initialize recipe context for sharing data between steps
    recipe_context = {
        'variables': {},      # General variable storage
        'files': {},         # File paths and handles
        'settings': {},      # Configuration data
        'results': {},       # Function return values
        'metadata': {        # Recipe metadata
            'title': title,
            'start_time': None,
            'current_step': 0
        }
    }
    
    show_recipe_header(title)
    
    for step_index in range(1, len(recipe)):
        step = recipe[step_index]
        recipe_context['metadata']['current_step'] = step_index
        show_step(step_index, step)
        
        if not run_single_step(step, recipe_module, step_index, recipe_context):
            return  # Fatal error occurred
        
        if step_index < len(recipe) - 1:  # Not the last step
            console.input("\n[dim]Press Enter to continue...[/dim]")
    
    console.print("\n[bold green]--- Recipe Complete ---[/bold green]")
    console.input("\n[dim]Press Enter to return to the main menu...[/dim]")

if __name__ == "__main__":
    # Example of how to run it directly (for testing)
    # You would need a recipe.json and a recipe.py in the same directory
    # run_recipe("recipe.json", "recipe.py")
    pass
