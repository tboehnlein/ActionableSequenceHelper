"""
Recipe Version Management for ASH

This module handles versioning, validation, and upgrading of recipe files.
It ensures backward compatibility while allowing the recipe format to evolve.

VERSIONING SCHEME:
    - Version 1.0: Original format (no version field)
    - Version 1.1: Added recipe_context support + flat step format (current)
    - Future versions can add new features while maintaining compatibility

RECIPE FORMAT EVOLUTION:
    v1.0 (Legacy):
    [
        {"title": "Recipe", "description": "..."},
        {"statement": "Step", "function_name": "func"}
    ]
    
    v1.1+ (Current - Flat Format):
    {
        "version": "1.1",
        "title": "Recipe Name",
        "description": "What it does",
        "step1": {"statement": "First step"},
        "step2": {"statement": "Second step", "function_name": "func"},
        "step3": {"statement": "Third step"}
    }

BACKWARD COMPATIBILITY:
    - Legacy recipes (v1.0) are automatically detected and upgraded
    - All existing features continue to work
    - Upgrades preserve all functionality
"""

import json
import os
import shutil
from typing import Dict, List, Any, Tuple, Optional
from rich.console import Console

console = Console()

# Current supported recipe version
CURRENT_RECIPE_VERSION = "1.1"

# Version history and compatibility
VERSION_HISTORY = {
    "1.0": {
        "description": "Original format (array-based)",
        "features": ["basic_steps", "function_calls", "prompt_for"]
    },
    "1.1": {
        "description": "Added recipe_context support + flat step format",
        "features": ["basic_steps", "function_calls", "prompt_for", "recipe_context", "flat_format", "professional_naming"]
    }
}

def detect_recipe_version(recipe_data: Any) -> str:
    """
    Detect the version of a recipe file.
    
    Args:
        recipe_data: The loaded JSON recipe data
        
    Returns:
        str: The detected version (e.g., "1.0", "1.1")
    """
    if isinstance(recipe_data, dict) and "version" in recipe_data:
        return recipe_data["version"]
    elif isinstance(recipe_data, list):
        # Legacy format (v1.0)
        return "1.0"
    else:
        # Unknown format, assume legacy
        return "1.0"

def validate_recipe_version(version: str) -> bool:
    """
    Check if a recipe version is supported.
    
    Args:
        version: Version string to validate
        
    Returns:
        bool: True if version is supported
    """
    return version in VERSION_HISTORY

def upgrade_recipe_v1_0_to_v1_1(legacy_recipe: List[Dict]) -> Dict[str, Any]:
    """
    Upgrade a v1.0 recipe to v1.1 format.
    
    Args:
        legacy_recipe: The v1.0 recipe data (list format)
        
    Returns:
        dict: The upgraded v1.1 recipe data
    """
    if not legacy_recipe or not isinstance(legacy_recipe, list):
        raise ValueError("Invalid v1.0 recipe format")
    
    # Extract metadata from first element
    metadata = legacy_recipe[0] if legacy_recipe else {}
    
    # Extract steps (everything after metadata)
    steps = legacy_recipe[1:] if len(legacy_recipe) > 1 else []
    
    # Create v1.1 format with flat step structure
    upgraded_recipe = {
        "version": "1.1",
        "title": metadata.get("title", "Untitled Recipe"),
        "description": metadata.get("description", "No description available.")
    }
    
    # Add steps as flat properties (step1, step2, etc.)
    for i, step in enumerate(steps, 1):
        step_name = f"step{i}"
        upgraded_recipe[step_name] = step
    
    # Add metadata for tracking
    if steps:  # Only add metadata if there are actual steps
        upgraded_recipe["metadata"] = {
            "original_version": "1.0",
            "upgraded_on": "auto"
        }
    
    return upgraded_recipe

def upgrade_recipe_to_current(recipe_data: Any, current_version: str) -> Tuple[Dict[str, Any], bool]:
    """
    Upgrade a recipe to the current version.
    
    Args:
        recipe_data: The recipe data to upgrade
        current_version: The detected current version
        
    Returns:
        tuple: (upgraded_recipe, was_upgraded)
    """
    if current_version == CURRENT_RECIPE_VERSION:
        # Already current version
        if isinstance(recipe_data, dict):
            return recipe_data, False
        else:
            # Shouldn't happen, but handle gracefully
            return upgrade_recipe_v1_0_to_v1_1(recipe_data), True
    
    # Upgrade path
    if current_version == "1.0":
        upgraded = upgrade_recipe_v1_0_to_v1_1(recipe_data)
        return upgraded, True
    
    # Future version upgrade paths would go here
    # elif current_version == "1.1" and CURRENT_RECIPE_VERSION == "1.2":
    #     return upgrade_recipe_v1_1_to_v1_2(recipe_data), True
    
    # If we get here, the version is newer than we support
    raise ValueError(f"Recipe version {current_version} is newer than supported version {CURRENT_RECIPE_VERSION}")

def normalize_recipe_for_execution(recipe_data: Any) -> List[Dict]:
    """
    Convert any recipe version to the execution format (v1.0 list format).
    This allows the execution engine to work with any version.
    
    Args:
        recipe_data: Recipe data in any supported format
        
    Returns:
        list: Recipe in v1.0 execution format
    """
    version = detect_recipe_version(recipe_data)
    
    if version == "1.0":
        # Already in execution format
        return recipe_data
    elif version == "1.1":
        # Convert v1.1 to execution format
        # Title and description are at top level in v1.1
        title = recipe_data.get("title", "")
        color = recipe_data.get("color")
        color_end = recipe_data.get("color_end")
        description = recipe_data.get("description", "")
        
        # If they're still in metadata (old v1.1 format), use those as fallback
        metadata = recipe_data.get("metadata", {})
        if not title and "title" in metadata:
            title = metadata["title"]
        if not description and "description" in metadata:
            description = metadata["description"]
        if not color and "color" in metadata:
            color = metadata["color"]
        if not color_end and "color_end" in metadata:
            color_end = metadata["color_end"]
        
        # Set defaults if still empty
        if not title:
            title = "Untitled Recipe"
        if not description:
            description = "No description available."
        
        # Extract steps from flat structure (step1, step2, etc.) or legacy steps array
        steps = []
        if "steps" in recipe_data:
            # Legacy v1.1 format with steps array
            steps = []
            for i, step_data in enumerate(recipe_data["steps"], 1):
                step_copy = step_data.copy()  # Copy to avoid modifying original
                step_copy['_step_name'] = f"Step {i}"  # Add professional step name for legacy array format
                steps.append(step_copy)
        else:
            # New flat format - extract all step properties
            step_keys = [key for key in recipe_data.keys() if key.startswith("step") and key[4:].isdigit()]
            step_keys.sort(key=lambda x: int(x[4:]))  # Sort by step number
            steps = []
            for step_key in step_keys:
                step_data = recipe_data[step_key].copy()  # Copy to avoid modifying original
                # Convert stepN to "Step N" format for display
                step_number = step_key[4:]  # Extract number after "step"
                step_data['_step_name'] = f"Step {step_number}"
                steps.append(step_data)
        
        # Reconstruct v1.0 format for execution
        execution_metadata = {
            "title": title,
            "description": description
        }
        if color:
            execution_metadata["color"] = color
        if color_end:
            execution_metadata["color_end"] = color_end
        execution_format = [execution_metadata] + steps
        return execution_format
    else:
        raise ValueError(f"Cannot normalize unsupported recipe version: {version}")

def backup_recipe_file(recipe_path: str) -> str:
    """
    Create a backup of a recipe file before upgrading.
    
    Args:
        recipe_path: Path to the recipe file
        
    Returns:
        str: Path to the backup file
    """
    backup_path = f"{recipe_path}.backup"
    shutil.copy2(recipe_path, backup_path)
    return backup_path

def save_upgraded_recipe(recipe_path: str, upgraded_recipe: Dict[str, Any], create_backup: bool = True) -> str:
    """
    Save an upgraded recipe to disk.
    
    Args:
        recipe_path: Path to save the recipe
        upgraded_recipe: The upgraded recipe data
        create_backup: Whether to create a backup of the original
        
    Returns:
        str: Path to backup file if created, empty string otherwise
    """
    backup_path = ""
    
    if create_backup and os.path.exists(recipe_path):
        backup_path = backup_recipe_file(recipe_path)
    
    with open(recipe_path, 'w') as f:
        json.dump(upgraded_recipe, f, indent=2)
    
    return backup_path

def process_recipe_with_versioning(recipe_path: str, auto_upgrade: bool = False) -> Tuple[List[Dict], str, bool]:
    """
    Load and process a recipe with version handling.
    
    Args:
        recipe_path: Path to the recipe file
        auto_upgrade: Whether to automatically upgrade old recipes
        
    Returns:
        tuple: (execution_recipe, version_info, was_upgraded)
    """
    try:
        with open(recipe_path, 'r') as f:
            recipe_data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load recipe: {e}")
    
    # Detect version
    version = detect_recipe_version(recipe_data)
    
    # Validate version
    if not validate_recipe_version(version):
        raise ValueError(f"Unsupported recipe version: {version}")
    
    version_info = f"v{version}"
    was_upgraded = False
    
    # Check if upgrade is needed
    if version != CURRENT_RECIPE_VERSION:
        if auto_upgrade:
            # Perform upgrade
            upgraded_recipe, was_upgraded = upgrade_recipe_to_current(recipe_data, version)
            
            # Save upgraded version
            backup_path = save_upgraded_recipe(recipe_path, upgraded_recipe, create_backup=True)
            
            if was_upgraded:
                console.print(f"[green]✓[/green] Upgraded recipe from v{version} to v{CURRENT_RECIPE_VERSION}")
                console.print(f"[dim]  Backup saved: {os.path.basename(backup_path)}[/dim]")
                version_info = f"v{version} → v{CURRENT_RECIPE_VERSION}"
                recipe_data = upgraded_recipe
        else:
            # Just notify about version
            version_info = f"v{version} (legacy)"
    
    # Normalize for execution
    execution_recipe = normalize_recipe_for_execution(recipe_data)
    
    return execution_recipe, version_info, was_upgraded

def show_version_info():
    """Display version information and capabilities."""
    console.print("\n[bold blue]ASH Recipe Version Information[/bold blue]")
    console.print("=" * 50)
    
    for version, info in VERSION_HISTORY.items():
        marker = "🟢 CURRENT" if version == CURRENT_RECIPE_VERSION else "🔵 LEGACY"
        console.print(f"\n[yellow]Version {version}[/yellow] {marker}")
        console.print(f"  {info['description']}")
        console.print(f"  Features: {', '.join(info['features'])}")
    
    console.print(f"\n[green]Current target version: {CURRENT_RECIPE_VERSION}[/green]")
    console.print("[dim]Legacy recipes are automatically upgraded when loaded[/dim]")

def create_new_recipe_template(title: str, description: str) -> Dict[str, Any]:
    """
    Create a new recipe template in the current version format.
    
    Args:
        title: Recipe title
        description: Recipe description
        
    Returns:
        dict: New recipe template
    """
    return {
        "version": CURRENT_RECIPE_VERSION,
        "title": title,
        "description": description,
        "step1": {
            "statement": "Welcome to your new recipe! Edit this step to get started."
        },
        "step2": {
            "statement": "Add more steps by creating step3, step4, etc.",
            "function_name": "optional_function_name"
        }
    }
