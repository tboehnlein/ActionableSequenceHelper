
import json
import importlib.util
import os
import inspect
from rich.console import Console
from rich.panel import Panel

# Create a console object for beautiful output
console = Console()

def run_recipe(recipe_path: str, module_path: str):
    """
    Executes a recipe file step-by-step, guiding the user with rich formatting.
    Dynamically loads functions from the associated module.
    """
    try:
        with open(recipe_path, 'r') as f:
            recipe = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Recipe file not found at [cyan]'{recipe_path}'[/cyan]")
        return
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/] Could not decode JSON from [cyan]'{recipe_path}'[/cyan]")
        return

    try:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            recipe_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(recipe_module)
        else:
            console.print(f"[bold red]Error:[/] Could not create module spec for [cyan]'{module_path}'[/cyan].")
            return
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to load module from [cyan]'{module_path}'[/cyan]: {e}")
        return
    
    title = recipe[0]['title']

    console.print(f"[bold green]--- Starting Recipe [bold white]{title}[/bold white] ---[/bold green]")
    console.print("-" * 25)

    current_step_index = 1
    while current_step_index < len(recipe):
        step = recipe[current_step_index]
        
        console.print(Panel(
            f"{step['statement']}",
            title=f"[yellow bold]Step {current_step_index + 1}[/yellow bold]",
            border_style="blue"
        ))

        step_success = False
        # Loop until the current step is successfully completed
        while not step_success:
            if not step.get('function_name'):
                # If there's no function, the step is automatically successful
                step_success = True
                continue

            try:
                func_to_call = getattr(recipe_module, step['function_name'])
                func_params = inspect.signature(func_to_call).parameters

                # --- Argument & Parameter Handling ---
                call_args = {}

                # 1. Inject console if requested
                if 'console' in func_params:
                    call_args['console'] = console

                # 2. Prompt user for specified parameters
                if 'prompt_for' in step and isinstance(step['prompt_for'], dict):
                    step_success = True  # Assume success unless we find an issue
                    for param_name, prompt_text in step['prompt_for'].items():
                        if param_name in func_params:
                            user_input = console.input(f"[cyan]{prompt_text}[/cyan]").strip()
                            if not user_input:
                                console.print("[bold red]Input cannot be empty. Please try again.[/bold red]")
                                # We need to break out and restart the step loop
                                step_success = False
                                break
                            call_args[param_name] = user_input
                        else:
                            console.print(f"[bold red]Configuration Error:[/] Recipe wants to prompt for '{param_name}', but function has no such parameter.")
                            step_success = False
                            break
                    if not step_success: # If any prompt failed, restart the step
                        continue
                
                # 3. Pass any other parameters directly from JSON
                for param_name, param_value in step.items():
                    if param_name in func_params and param_name not in call_args:
                        call_args[param_name] = param_value

                # --- Function Execution ---
                try:
                    if func_to_call(**call_args):
                        step_success = True
                    else:
                        console.print("[bold yellow]The step failed. Please review the output and try again.[/bold yellow]\n")
                except Exception as e:
                    console.print(f"\n[bold red]ERROR:[/] An unexpected error occurred in function '{step['function_name']}': {e}\n")


            except AttributeError:
                console.print(f"\n[bold red]FATAL ERROR:[/] Function [yellow]'{step['function_name']}'[/yellow] not found in the module! Cannot proceed.\n")
                return # Exit the entire recipe
            except Exception as e:
                console.print(f"\n[bold red]ERROR:[/] An unexpected error occurred: {e}\n")
                # This will cause the loop to repeat, allowing a retry
        
        # If the step was successful, advance to the next one
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
