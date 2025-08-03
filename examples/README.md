# ASH Examples

This folder contains example recipes that demonstrate the features and capabilities of the Actionable Sequence Helper (ASH) system.

## Contents

### `example.json` + `example.py`
A comprehensive example that showcases:
- **Text-only steps** - Simple instructions that don't require code
- **User prompting** - Collecting input via `prompt_for` fields  
- **Dependency injection** - Using `console` and `run_tk_dialog`
- **File dialogs** - Safe GUI integration for file selection
- **Error handling** - Demonstrating retry logic on failure
- **Rich formatting** - Colors, styles, and visual feedback

## Using the Examples

### Option 1: Run from Examples Folder
Copy the example files to your `recipes/` directory:
```bash
cp examples/example.* recipes/
python ash_menu.py
```

### Option 2: Point ASH to Examples
Temporarily modify `ash_menu.py` to use the examples folder:
```python
RECIPES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
```

## Learning from the Examples

1. **Study the JSON structure** - See how steps are defined
2. **Examine the Python functions** - Note parameter handling and return values  
3. **Run the example** - Experience the user interaction flow
4. **Modify and experiment** - Change prompts, add steps, etc.

## Creating Your Own Recipes

Use the example as a template:
1. Copy `example.json` → `your_recipe.json`
2. Copy `example.py` → `your_recipe.py` 
3. Modify the steps and functions for your specific workflow
4. Test using ASH's recipe verification and error display

## Best Practices Demonstrated

- **Clear step statements** - Tell users exactly what's happening
- **Meaningful function names** - Descriptive and purpose-driven
- **Proper error handling** - Return False for retry, None for fatal errors
- **Rich console output** - Use colors and formatting for better UX
- **Parameter validation** - Check inputs before processing
- **Helpful feedback** - Keep users informed of progress and results

Happy recipe creation! 🍳
