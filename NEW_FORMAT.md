# New v1.1 Recipe Format - Quick Start Guide

## Creating Recipes is Now Much Simpler!

### v1.1 Format (Current - Flat Structure)
```json
{
  "version": "1.1",
  "title": "My Awesome Recipe",
  "description": "What this recipe accomplishes",
  "step1": {
    "statement": "Step 1: Do something"
  },
  "step2": {
    "statement": "Step 2: Call a function",
    "function_name": "my_function",
    "prompt_for": {
      "name": "What's your name?",
      "option": "Choose an option"
    }
  },
  "step3": {
    "statement": "Step 3: Another action"
  }
}
```

### Key Improvements:
- ✅ **Title and description at top level** - no more nested metadata!
- ✅ **Flat step structure** - no more `steps` array boilerplate!
- ✅ **Direct step properties** - just add `step1`, `step2`, `step3`, etc.
- ✅ **Clean, readable structure** - easy to understand at a glance
- ✅ **Professional step naming** - displays as "Step 1", "Step 2", etc.
- ✅ **Backward compatible** - v1.0 recipes automatically upgrade
- ✅ **All v1.1 features** - recipe_context, dependency injection, etc.

### Optional Metadata Section:
```json
{
  "version": "1.1",
  "title": "Advanced Recipe",
  "description": "With optional metadata",
  "metadata": {
    "author": "Your Name",
    "created": "2025-01-01",
    "category": "automation"
  },
  "step1": {
    "statement": "First step"
  },
  "step2": {
    "statement": "Second step"
  }
}
```

### Migration:
- **v1.0 recipes**: Automatically upgraded when loaded to flat v1.1 format
- **Legacy v1.1 with steps array**: Also supported and normalized for execution
- **Backups created**: Original files preserved as `.backup`
- **Zero breaking changes**: All existing functionality preserved

### Format Comparison:

#### v1.0 (Legacy - Array Format)
```json
[
  {"title": "Recipe Name", "description": "What it does"},
  {"statement": "First step"},
  {"statement": "Second step", "function_name": "my_function"}
]
```

#### v1.1 (Current - Flat Format)
```json
{
  "version": "1.1",
  "title": "Recipe Name", 
  "description": "What it does",
  "step1": {"statement": "First step"},
  "step2": {"statement": "Second step", "function_name": "my_function"}
}
```

### Benefits of Flat Format:
- **Less Boilerplate**: No nested `steps` array wrapper
- **Easier to Edit**: Direct access to step properties
- **Better Readability**: Clear structure without unnecessary nesting
- **Professional Display**: Steps show as "Step 1", "Step 2", etc.
- **Simpler Creation**: Just add `step1`, `step2`, `step3` properties directly
