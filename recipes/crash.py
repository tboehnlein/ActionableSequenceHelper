import tkinter as tk
from tkinter import filedialog
from rich.console import Console
from rich.panel import Panel

def OpenFileWindow(title: str, console: Console):
    """
    Opens a file dialog window for the user to select a file.
    Prints the selected file path to stdout.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Pass the title to the dialog and ensure the window is on top
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(title=title)
    root.attributes('-topmost', False)

    # Explicitly destroy the root window to prevent hanging
    root.destroy()

    if file_path:
        console.print(f"[bold green]Selected file:[/] [italic white]{file_path}[/italic white]")
        return True
    else:
        console.print("[bold red]No file selected.[/bold red]")
        return False

if __name__ == '__main__':
    OpenFileWindow("Select a file", console=Console())
