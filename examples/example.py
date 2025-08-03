"""
Example Recipe Functions for ASH

This file demonstrates how to write Python functions for ASH recipes.
It shows dependency injection, parameter handling, and return values.
"""

import os

# Global variable to track retry attempts (for demonstration)
retry_count = 0

def get_user_info(name, project, console):
    """
    Demonstrates parameter prompting and console output.
    
    Parameters:
        name (str): User's name from prompt_for
        project (str): Project name from prompt_for  
        console: Injected Rich console object
    
    Returns:
        bool: True for success, False for failure
    """
    console.print(f"\n[bold green]Hello, {name}![/bold green]")
    console.print(f"[cyan]Working on project: {project}[/cyan]")
    console.print("[dim]This information was collected via the 'prompt_for' feature.[/dim]\n")
    return True

def select_file(console, run_tk_dialog):
    """
    Demonstrates file dialog integration.
    
    Parameters:
        console: Injected Rich console object
        run_tk_dialog: Injected tkinter dialog helper
    
    Returns:
        bool: True for success, False for failure
    """
    from tkinter import filedialog
    
    console.print("[yellow]Opening file dialog...[/yellow]")
    
    # Use the injected helper to safely run the dialog
    file_path = run_tk_dialog(
        filedialog.askopenfilename,
        title="Select any file (or cancel to continue)",
        filetypes=[
            ("Text files", "*.txt"),
            ("Python files", "*.py"), 
            ("All files", "*.*")
        ]
    )
    
    if file_path:
        console.print(f"[bold green]✓ Selected file:[/bold green] [italic]{file_path}[/italic]")
        # Check if file exists and show some info
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            console.print(f"[dim]File size: {size} bytes[/dim]")
    else:
        console.print("[yellow]No file selected (that's okay!)[/yellow]")
    
    return True

def demonstrate_retry(console):
    """
    Demonstrates retry logic - fails the first time, succeeds the second.
    
    Parameters:
        console: Injected Rich console object
    
    Returns:
        bool: True for success, False for failure (triggers retry)
    """
    global retry_count
    retry_count += 1
    
    if retry_count == 1:
        console.print("[bold red]❌ Simulated failure![/bold red]")
        console.print("[yellow]This demonstrates ASH's retry capability.[/yellow]")
        console.print("[dim]The step will now be retried automatically...[/dim]")
        return False  # Return False to trigger retry
    else:
        console.print("[bold green]✓ Success on retry![/bold green]")
        console.print("[dim]This shows how steps can recover from temporary failures.[/dim]")
        return True  # Return True for success

def show_summary(console):
    """
    Shows a summary of what was demonstrated.
    
    Parameters:
        console: Injected Rich console object
    
    Returns:
        bool: True for success
    """
    console.print("\n[bold blue]🎉 Example Recipe Complete![/bold blue]")
    console.print("\n[bold]Features demonstrated:[/bold]")
    console.print("• [green]Text-only steps[/green] - No Python code required")
    console.print("• [green]User prompting[/green] - Collect input via 'prompt_for'")
    console.print("• [green]Dependency injection[/green] - 'console' and 'run_tk_dialog' auto-provided")
    console.print("• [green]File dialogs[/green] - Safe GUI integration") 
    console.print("• [green]Error handling[/green] - Automatic retry on failure")
    console.print("• [green]Rich formatting[/green] - Colors, styles, and emojis")
    
    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Copy this example to the recipes/ folder to use it")
    console.print("2. Modify the JSON and Python files for your own workflows")
    console.print("3. Create new recipes for your specific tasks")
    
    return True

# Example of a function that might be called directly (for testing)
if __name__ == "__main__":
    print("This is the example recipe Python module.")
    print("Functions in this file are called by example.json")
    print("Run 'python ash_menu.py' to see it in action!")
