# Installation Guide - Actionable Sequence Helper (ASH) v1.0

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Clone or Download the Project

```bash
git clone https://github.com/tboehnlein/ActionableSequenceHelper.git
cd ActionableSequenceHelper
```

*Or download the ZIP file and extract it to your desired location.*

### 2. Install Dependencies

ASH requires the `rich` library for its user interface:

```bash
pip install rich
```

*Note: If you have multiple Python versions, you may need to use `pip3` instead of `pip`.*

### 3. Verify Installation

Run the main menu to ensure everything is working:

```bash
python ash_menu.py
```

You should see the ASH welcome screen with any available recipes.

## Quick Start

### Creating Your First Recipe

1. Navigate to the `recipes/` directory
2. Create a simple recipe file `hello.json`:

```json
[
    {
        "title": "Hello World",
        "description": "A simple test recipe"
    },
    {
        "statement": "This is your first ASH recipe step!"
    },
    {
        "statement": "Congratulations! You've successfully set up ASH."
    }
]
```

3. Run ASH again and select your new recipe:

```bash
python ash_menu.py
```

## Directory Structure

After installation, your project should look like this:

```
ActionableSequenceHelper/
├── ash_menu.py          # Main application
├── execute_recipe.py    # Recipe execution engine
├── __version__.py       # Version information
├── README.md           # Project documentation
├── INSTALL.md          # This file
├── examples/           # Example recipes and documentation
│   ├── example.json    # Comprehensive example recipe
│   ├── example.py      # Example Python functions
│   └── README.md       # Examples documentation
└── recipes/            # Your recipe directory
    └── empty           # Add your recipes here!
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'rich'"**
- Solution: Install the rich library with `pip install rich`

**"No such file or directory: recipes/"**
- Solution: Ensure you're running `ash_menu.py` from the project root directory

**Recipe shows "LOAD ERROR"**
- Solution: Check that your JSON syntax is valid and any referenced Python functions exist

### Getting Help

1. Check the main README.md for detailed usage instructions
2. Look at the comprehensive examples in the `examples/` directory
3. Look at the working recipes in the `recipes/` directory
4. Use the 'R' command in the menu to refresh after fixing recipe errors

## Optional: Add to PATH

To run ASH from anywhere, you can add the installation directory to your system PATH or create an alias:

**Windows (PowerShell):**
```powershell
Set-Alias ash "C:\path\to\ActionableSequenceHelper\ash_menu.py"
```

**Linux/Mac (bash):**
```bash
echo 'alias ash="python /path/to/ActionableSequenceHelper/ash_menu.py"' >> ~/.bashrc
source ~/.bashrc
```

## Uninstallation

To remove ASH:
1. Delete the ActionableSequenceHelper directory
2. Optionally remove the `rich` package: `pip uninstall rich`

---

**Need more help?** Check the full documentation in README.md or create an issue on GitHub.
