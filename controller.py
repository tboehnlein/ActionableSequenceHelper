import json
import importlib.util
import os
import inspect
import tkinter as tk
from tkinter import filedialog
from rich.console import Console
from rich.panel import Panel

# Create a console object for beautiful output
console = Console()

def run_tk_dialog(dialog_func, *args, **kwargs):
    """
    Safely run a tkinter dialog, ensuring the window is on top and the root window is properly destroyed.

    Parameters:
        dialog_func (callable): The tkinter dialog function to call (e.g., filedialog.askopenfilename).
        *args: Positional arguments to pass to the dialog function.
        **kwargs: Keyword arguments to pass to the dialog function.

    Returns:
        The result returned by the dialog function (e.g., selected file path).
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

def execute_step(step, recipe_module):
    """
    Execute a single step in the recipe, handling function calls and user prompts.

    Parameters:
        step (dict): The current recipe step.
        recipe_module (module or None): The loaded Python module, or None if not present.

    Returns:
        bool: True if the step was successful, False otherwise.
    """
    # If there's no function, the step is just text. It's automatically successful.
    if not step.get('function_name'):
        return True
    # If a function is required, but we have no module, it's an error.
    if not recipe_module:
        console.print(f"\n[bold red]Configuration Error:[/] Step requires function '{step['function_name']}', but no code file was found.\n")
        return False
    try:
        func_to_call = getattr(recipe_module, step['function_name'])
        func_params = inspect.signature(func_to_call).parameters
        call_args = {}
        # Inject dependencies
        if 'console' in func_params:
            call_args['console'] = console
        if 'run_tk_dialog' in func_params:
            call_args['run_tk_dialog'] = run_tk_dialog
        # Prompt for parameters
        prompt_args = prompt_for_parameters(step, func_params)
        if prompt_args is None:
            return False
        call_args.update(prompt_args)
        # Pass any other parameters directly from JSON
        for param_name, param_value in step.items():
            if param_name in func_params and param_name not in call_args:
                call_args[param_name] = param_value
        # Function Execution
        if func_to_call(**call_args):
            return True
        else:
            console.print("[bold yellow]The step failed. Please review the output and try again.[/bold yellow]\n")
            return False
    except AttributeError:
        console.print(f"\n[bold red]FATAL ERROR:[/] Function [yellow]'{step['function_name']}'[/yellow] not found in the module! Cannot proceed.\n")
        return False
    except Exception as e:
        console.print(f"\n[bold red]ERROR:[/] An unexpected error occurred in function '{step['function_name']}': {e}\n")
        return False

def run_recipe(recipe_path: str, module_path: str):
    """
    Executes a recipe file step-by-step, guiding the user with rich formatting.
    Dynamically loads functions from an optional associated module.

    Parameters:
        recipe_path (str): Path to the recipe JSON file.
        module_path (str): Path to the associated Python module file (optional).

    Returns:
        None
    """
    recipe = load_recipe_json(recipe_path)
    if recipe is None:
        return
    recipe_module = load_recipe_module(module_path)
    title = recipe[0].get('title', 'Untitled Recipe')
    console.print(f"[bold green]--- Starting Recipe [bold white]{title}[/bold white] ---[/bold green]")
    console.print("-" * 25)
    current_step_index = 1
    while current_step_index < len(recipe):
        step = recipe[current_step_index]
        console.print(Panel(
            f"{step.get('statement', '')}",
            title=f"[yellow bold]Step {current_step_index}[/yellow bold]",
            border_style="blue"
        ))
        step_success = False
        while not step_success:
            step_success = execute_step(step, recipe_module)
            if not step_success:
                # If the step failed, allow retry
                continue
        current_step_index += 1
        if current_step_index < len(recipe):
            console.input("\n[dim]Press Enter to continue...[/dim]")
            console.print("-" * 25)
    console.print("\n[bold green]--- Recipe Complete ---")

if __name__ == "__main__":
    # Example of how to run it directly (for testing)
    # You would need a recipe.json and a recipe.py in the same directory
    # run_recipe("recipe.json", "recipe.py")
    pass
