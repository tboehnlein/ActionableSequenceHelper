"""
Recipe Loading and Verification for ASH

This module is responsible for loading recipe definitions from JSON files,
handling different recipe versions, and verifying their integrity. It prepares
the recipes for execution by the main menu and execution engine.

CORE FUNCTIONALITY:
    - Scans the 'recipes' directory for JSON recipe files.
    - Loads recipe details, including title, description, and custom colors.
    - Integrates with 'recipe_version.py' to handle version detection and
      automatic upgrades of legacy recipe formats.
    - Verifies that functions and parameters specified in a recipe exist in the
      corresponding Python module, preventing runtime errors.
    - Reports any loading or verification errors, which are then displayed
      in the main menu.

Functions:
    - load_recipe_details: The main function that orchestrates loading and
      verification of all recipes.
    - verify_recipe: Verifies a legacy (v1.0) recipe format.
    - verify_recipe_with_execution_format: Verifies the normalized,
      execution-ready recipe format.
"""
import os
import json
from rich.console import Console
import importlib.util
import inspect
from __version__ import __version__
import recipe_version

RECIPES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes")

def load_recipe_details(recipe_files, console:Console):
    """
    Loads and verifies recipe details from a list of recipe files.

    This function iterates through each recipe file, processes it for versioning,
    and verifies its contents against its corresponding Python module. It
    constructs a list of menu items for display and a dictionary of
    execution-ready recipe data.

    It handles both legacy (v1.0) and current (v1.1+) recipe formats,
    automatically upgrading legacy recipes if configured. It also extracts
    metadata like title, description, and colors for rich menu presentation.

    Args:
        recipe_files (list[str]): A list of recipe filenames (e.g., 'my_recipe.json').
        console (Console): The rich Console object for printing errors and warnings.

    Returns:
        tuple[list[dict], dict]: A tuple containing:
            - A list of dictionaries, where each dictionary represents a menu item
              with details like title, description, version info, and any load errors.
            - A dictionary mapping recipe filenames to their loaded and normalized
              execution-ready recipe data.
    """
    menu_items = []
    recipes_data = {}
    for i, recipe_file in enumerate(recipe_files):
        try:
            recipe_path = os.path.join(RECIPES_DIR, recipe_file)
            module_name = os.path.splitext(recipe_file)[0]
            module_path = os.path.join(RECIPES_DIR, f"{module_name}.py")
            try:
                execution_recipe, version_info, was_upgraded = recipe_version.process_recipe_with_versioning(
                    recipe_path, auto_upgrade=True
                )
                recipes_data[recipe_file] = execution_recipe
                if execution_recipe and isinstance(execution_recipe, list) and len(execution_recipe) > 0:
                    metadata = execution_recipe[0]
                    title = metadata.get('title', f"Recipe {i + 1}")
                    description = metadata.get('description', "No description available.")
                    color = metadata.get('color', "white")
                    color_end = metadata.get('color_end')
                    load_errors = verify_recipe_with_execution_format(execution_recipe, module_path, console)
                    menu_item = {
                        "filename": recipe_file,
                        "title": title,
                        "description": description,
                        "version_info": version_info,
                        "was_upgraded": was_upgraded,
                        "color": color
                    }
                    if color_end:
                        menu_item['color_end'] = color_end
                    if load_errors:
                        menu_item["load_error"] = "\n".join(load_errors)
                    menu_items.append(menu_item)
                else:
                    menu_items.append({
                        "filename": recipe_file,
                        "title": f"{recipe_file} - No valid steps found.",
                        "description": "",
                        "version_info": "unknown",
                        "was_upgraded": False,
                        "color": "blue"
                    })
            except Exception as version_error:
                console.print(f"[yellow]Warning: Version processing failed for {recipe_file}, using legacy mode: {version_error}[/yellow]")
                with open(recipe_path, 'r') as f:
                    recipe = json.load(f)
                    recipes_data[recipe_file] = recipe
                    load_errors = verify_recipe(recipe_path, module_path, console)
                    if recipe and isinstance(recipe, list) and len(recipe) > 0:
                        title = recipe[0].get('title', f"Recipe {i + 1}")
                        description = recipe[0].get('description', "No description available.")
                        color = recipe[0].get('color', "blue")
                        menu_item = {
                            "filename": recipe_file,
                            "title": title,
                            "description": description,
                            "version_info": "v1.0 (legacy)",
                            "was_upgraded": False,
                            "color": color
                        }
                        if load_errors:
                            menu_item["load_error"] = "\n".join(load_errors)
                        menu_items.append(menu_item)
        except Exception as e:
            console.print(f"[bold red]Error reading {recipe_file}: {e}[/bold red]")
            menu_items.append({
                "filename": recipe_file,
                "title": f"{recipe_file} - Error loading",
                "description": str(e),
                "version_info": "error",
                "was_upgraded": False,
                "color": "blue"
            })
    return menu_items, recipes_data

def verify_recipe(recipe_path, module_path, console:Console):
    """
    Verify a legacy (v1.0, list-based) recipe.

    Checks that all functions and parameters specified in the recipe steps
    exist in the corresponding Python module. It uses introspection to validate
    function signatures.

    Args:
        recipe_path (str): The file path to the JSON recipe.
        module_path (str): The file path to the corresponding Python module.
        console (Console): The rich Console object for output (currently unused but
                           kept for signature consistency).

    Returns:
        list[str]: A list of error messages. The list is empty if no errors are found.
    """
    errors = []
    try:
        with open(recipe_path, 'r') as f:
            recipe = json.load(f)
    except Exception as e:
        errors.append(f"JSON load error: {e}")
        return errors
    module = None
    if os.path.exists(module_path):
        try:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        except Exception as e:
            errors.append(f"Python load error: {e}")
    for idx, step in enumerate(recipe[1:], start=2):
        func_name = step.get('function_name')
        if func_name is not None:
            if not func_name:
                errors.append(f"Step {idx}: 'function_name' cannot be an empty string.")
                continue
            if not module:
                errors.append(f"Step {idx}: Missing Python file for function '{func_name}'")
                continue
            func = getattr(module, func_name, None)
            if not func:
                errors.append(f"Step {idx}: Function '{func_name}' not found in module")
                continue
            sig = inspect.signature(func)
            func_params = sig.parameters
            prompt_for = step.get('prompt_for', {})
            
            # Check prompt_for parameters exist in function
            for param in prompt_for:
                if param not in func_params:
                    errors.append(f"Step {idx}: Parameter '{param}' in prompt_for not found in function '{func_name}'")
            
            # Check for unknown parameters (excluding injected dependencies and internal properties)
            injected_params = {'console', 'run_tk_dialog', 'recipe_context'}
            step_params = set(step.keys()) - {'statement', 'function_name', 'prompt_for'}
            for param in step_params:
                # Skip internal properties that start with underscore
                if param.startswith('_'):
                    continue
                if param not in func_params and param not in injected_params:
                    errors.append(f"Step {idx}: Parameter '{param}' not found in function '{func_name}'")
    return errors

def verify_recipe_with_execution_format(execution_recipe, module_path, console:Console):
    """
    Verify a recipe in the normalized execution format (v1.0 list-based).

    This function is used for all recipe versions after they have been normalized
    by the versioning system. It checks that all functions and parameters
    specified in the recipe steps exist in the corresponding Python module.

    Args:
        execution_recipe (list[dict]): The recipe data in the normalized,
                                       list-based execution format.
        module_path (str): The file path to the corresponding Python module.
        console (Console): The rich Console object for output (currently unused but
                           kept for signature consistency).

    Returns:
        list[str]: A list of error messages. The list is empty if no errors are found.
    """
    errors = []
    if not execution_recipe or not isinstance(execution_recipe, list):
        errors.append("Invalid recipe format")
        return errors
    
    module = None
    if os.path.exists(module_path):
        try:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        except Exception as e:
            errors.append(f"Python load error: {e}")
    
    for idx, step in enumerate(execution_recipe[1:], start=2):
        func_name = step.get('function_name')
        if func_name is not None:
            if not func_name:
                errors.append(f"Step {idx}: 'function_name' cannot be an empty string.")
                continue
            if not module:
                errors.append(f"Step {idx}: Missing Python file for function '{func_name}'")
                continue
            func = getattr(module, func_name, None)
            if not func:
                errors.append(f"Step {idx}: Function '{func_name}' not found in module")
                continue
            sig = inspect.signature(func)
            func_params = sig.parameters
            prompt_for = step.get('prompt_for', {})
            
            # Check prompt_for parameters exist in function
            for param in prompt_for:
                if param not in func_params:
                    errors.append(f"Step {idx}: Parameter '{param}' in prompt_for not found in function '{func_name}'")
            
            # Check for unknown parameters (excluding injected dependencies and internal properties)
            injected_params = {'console', 'run_tk_dialog', 'recipe_context'}
            step_params = set(step.keys()) - {'statement', 'function_name', 'prompt_for'}
            for param in step_params:
                # Skip internal properties that start with underscore
                if param.startswith('_'):
                    continue
                if param not in func_params and param not in injected_params:
                    errors.append(f"Step {idx}: Parameter '{param}' not found in function '{func_name}'")
    return errors