# ASH v1.1 Recipe Format - Quick Reference

## Current Format (v1.1 Flat)

```json
{
  "version": "1.1",
  "title": "Recipe Name",
  "description": "What this recipe does",
  "step1": {
    "statement": "First step description"
  },
  "step2": {
    "statement": "Second step with function call",
    "function_name": "my_function",
    "param1": "value1",
    "prompt_for": {
      "user_input": "Enter something:"
    }
  },
  "step3": {
    "statement": "Third step"
  }
}
```

## Key Features
- **No boilerplate**: No `steps` array wrapper
- **Direct properties**: `step1`, `step2`, `step3`, etc.
- **Professional display**: Shows as "Step 1", "Step 2", "Step 3"
- **Top-level metadata**: Title and description at root level
- **Auto-upgrade**: Legacy recipes automatically converted

## Template
```json
{
  "version": "1.1",
  "title": "Your Recipe Title",
  "description": "What your recipe accomplishes",
  "step1": {"statement": "First thing to do"},
  "step2": {"statement": "Second thing to do"},
  "step3": {"statement": "Third thing to do"}
}
```

## Adding Function Calls
```json
{
  "version": "1.1",
  "title": "Function Example",
  "description": "Shows how to call functions",
  "step1": {
    "statement": "Call a function with parameters",
    "function_name": "my_function",
    "param1": "direct_value",
    "prompt_for": {
      "param2": "Enter value for param2:"
    }
  }
}
```

**That's it!** Just add `step1`, `step2`, etc. properties directly to your recipe object.
