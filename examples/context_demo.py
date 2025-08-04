# Recipe Context Demo Functions
# This module demonstrates how to use recipe_context to share data between recipe steps

import os
from tkinter import filedialog

def collect_user_info(console, name, project, recipe_context):
    """Collect user information and store it in recipe_context for later use."""
    console.print(f"[green]Collecting information...[/green]")
    
    # Store the collected information in recipe_context
    recipe_context['variables']['user_name'] = name
    recipe_context['variables']['project_name'] = project
    recipe_context['metadata']['collection_time'] = "just now"
    
    console.print(f"[blue]Stored information for {name} working on {project}[/blue]")
    return f"User info collected for {name}"

def select_file_to_process(console, run_tk_dialog, recipe_context):
    """Let user select a file and store the path in recipe_context."""
    console.print("[green]Opening file selection dialog...[/green]")
    
    # Get a file from the user using the injected dialog function
    file_path = run_tk_dialog(
        filedialog.askopenfilename,
        title="Select a file to process",
        filetypes=[("All files", "*.*"), ("Text files", "*.txt"), ("Python files", "*.py")]
    )
    
    if file_path:
        # Store the file path in recipe_context
        recipe_context['files']['selected_file'] = file_path
        recipe_context['variables']['file_name'] = os.path.basename(file_path)
        recipe_context['variables']['file_size'] = os.path.getsize(file_path)
        
        console.print(f"[blue]Selected file: {os.path.basename(file_path)}[/blue]")
        console.print(f"[blue]File size: {recipe_context['variables']['file_size']} bytes[/blue]")
        return f"Selected file: {file_path}"
    else:
        console.print("[red]No file selected![/red]")
        return "No file selected"

def process_selected_file(console, recipe_context):
    """Process the file using information from previous steps."""
    # Get the user info from recipe_context
    user_name = recipe_context['variables'].get('user_name', 'Unknown User')
    project_name = recipe_context['variables'].get('project_name', 'Unknown Project')
    
    # Get the file info from recipe_context
    file_path = recipe_context['files'].get('selected_file')
    file_name = recipe_context['variables'].get('file_name', 'Unknown File')
    file_size = recipe_context['variables'].get('file_size', 0)
    
    if not file_path:
        console.print("[red]No file was selected in previous step![/red]")
        return "Cannot process - no file selected"
    
    console.print(f"[green]Processing file for {user_name}'s {project_name} project...[/green]")
    
    try:
        # Read the file content (first 100 characters for demo)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_preview = f.read(100)
        
        # Store processing results in recipe_context
        recipe_context['results']['processed_file'] = file_path
        recipe_context['results']['content_preview'] = content_preview
        recipe_context['results']['processing_status'] = 'success'
        recipe_context['metadata']['lines_processed'] = len(content_preview.split('\n'))
        
        console.print(f"[blue]File processed successfully![/blue]")
        console.print(f"[blue]Preview: {content_preview[:50]}...[/blue]")
        
        return f"Processed {file_name} ({file_size} bytes)"
        
    except Exception as e:
        recipe_context['results']['processing_status'] = 'failed'
        recipe_context['results']['error'] = str(e)
        console.print(f"[red]Error processing file: {e}[/red]")
        return f"Failed to process {file_name}"

def show_recipe_summary(console, recipe_context):
    """Show a summary of everything that happened in this recipe."""
    console.print("\n[bold yellow]RECIPE SUMMARY[/bold yellow]")
    console.print("=" * 50)
    
    # Show user information
    user_name = recipe_context['variables'].get('user_name', 'Unknown')
    project_name = recipe_context['variables'].get('project_name', 'Unknown')
    console.print(f"[cyan]User:[/cyan] {user_name}")
    console.print(f"[cyan]Project:[/cyan] {project_name}")
    
    # Show file information
    file_name = recipe_context['variables'].get('file_name', 'None selected')
    file_size = recipe_context['variables'].get('file_size', 0)
    console.print(f"[cyan]File:[/cyan] {file_name} ({file_size} bytes)")
    
    # Show processing results
    status = recipe_context['results'].get('processing_status', 'unknown')
    console.print(f"[cyan]Processing Status:[/cyan] {status}")
    
    if status == 'success':
        lines = recipe_context['metadata'].get('lines_processed', 0)
        console.print(f"[cyan]Lines Processed:[/cyan] {lines}")
        
        preview = recipe_context['results'].get('content_preview', '')
        if preview:
            console.print(f"[cyan]Content Preview:[/cyan] {preview[:30]}...")
    elif status == 'failed':
        error = recipe_context['results'].get('error', 'Unknown error')
        console.print(f"[red]Error:[/red] {error}")
    
    # Show all data stored in recipe_context
    console.print(f"\n[yellow]Total variables stored:[/yellow] {len(recipe_context['variables'])}")
    console.print(f"[yellow]Total files tracked:[/yellow] {len(recipe_context['files'])}")
    console.print(f"[yellow]Total results stored:[/yellow] {len(recipe_context['results'])}")
    console.print(f"[yellow]Metadata entries:[/yellow] {len(recipe_context['metadata'])}")
    
    return "Recipe summary displayed"
