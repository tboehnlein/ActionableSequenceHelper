"""
Simple ASH v1.1 Example Functions

This file demonstrates basic Python functions for ASH recipes using only
supported features: dependency injection, prompts, and error handling.
"""

import os

def get_user_info(name, project, console, recipe_context):
    """
    Collect user information and store in recipe context.
    
    Parameters:
        name (str): User's name from prompt_for
        project (str): Project name from prompt_for  
        console: Injected Rich console object
        recipe_context: Shared data dictionary
    
    Returns:
        bool: True for success
    """
    console.print(f"[bold green]Hello, {name}![/bold green]")
    console.print(f"[cyan]Working on project: {project}[/cyan]")
    
    # Store in recipe context for later steps
    recipe_context['variables']['user_name'] = name
    recipe_context['variables']['project_name'] = project
    
    return True

def select_file(console, run_tk_dialog, recipe_context):
    """
    File selection with GUI dialog.
    
    Parameters:
        console: Injected Rich console object
        run_tk_dialog: Injected dialog helper function
        recipe_context: Shared data dictionary
        
    Returns:
        bool: True for success
    """
    from tkinter import filedialog
    
    user_name = recipe_context['variables'].get('user_name', 'User')
    console.print(f"[blue]Opening file dialog for {user_name}...[/blue]")
    
    file_path = run_tk_dialog(
        filedialog.askopenfilename,
        title="Select a file",
        filetypes=[("All files", "*.*")]
    )
    
    if file_path:
        console.print(f"[green]Selected: {file_path}[/green]")
        recipe_context['variables']['selected_file'] = file_path
    else:
        console.print("[yellow]No file selected[/yellow]")
        recipe_context['variables']['selected_file'] = None
    
    return True

def demonstrate_retry(console, recipe_context):
    """
    Show error handling and retry capability.
    
    Parameters:
        console: Injected Rich console object
        recipe_context: Shared data dictionary
        
    Returns:
        bool: False on first attempt (triggers retry), True on retry
    """
    retry_count = recipe_context['variables'].get('retry_count', 0) + 1
    recipe_context['variables']['retry_count'] = retry_count
    
    if retry_count == 1:
        console.print("[red]❌ Simulated failure![/red]")
        console.print("[yellow]This will be retried automatically...[/yellow]")
        return False  # Triggers retry
    else:
        console.print("[green]✓ Success on retry![/green]")
        console.print("[dim]Error handling demonstrated successfully[/dim]")
        return True
