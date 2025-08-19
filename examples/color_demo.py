# Color Demo Functions
# This module demonstrates how to display all supported colors.

import re
from colorsys import rgb_to_hls
from rich.console import Console
from rich.color import ANSI_COLOR_NAMES, Color
from rich.columns import Columns
from rich.text import Text

def print_colors(console: Console):
    """
    Prints all supported ANSI color names, sorted by hue for a rainbow effect.
    Also displays the hex and RGB values for each color.
    """
    
    color_names = list(ANSI_COLOR_NAMES.keys())

    # Pre-calculate sort data to avoid parsing in the key function repeatedly
    color_data = {}
    for name in color_names:
        color = Color.parse(name)        
        rgb_triplet = color.get_truecolor()
        h, l, s = rgb_to_hls(*rgb_triplet.normalized)
        is_gray = s < 0.15
        # Extract base name by removing trailing digits
        base_name = re.sub(r'\d+$', '', name)
        color_data[name] = (is_gray, h, l, s, base_name)

    def sort_key(color_name: str):
        """
        Sort key function to order colors by their hue, saturation, and lightness,
        with grayscale colors grouped at the end.
        """
        is_gray, h, l, s, base_name = color_data[color_name]
        
        # Quantize hue to group similar colors. The multiplier determines sensitivity.
        quantized_hue = round(h * 20)
        
        # Sort by:
        # 1. Grayscale status (colors first)
        # 2. Quantized Hue (for a coarse rainbow effect)
        # 3. Base name (to group families like 'dodger_blue' together)
        # 4. Lightness (to order shades within a family, e.g., dark to light)
        return (is_gray, quantized_hue, base_name, l)

    color_list = sorted(color_names, key=sort_key)
    
    renderables = []
    for color_name in color_list:
        if 'grey' in color_name:
            continue
        color = Color.parse(color_name)
        rgb_triplet = color.get_truecolor()
        
        # Create a more informative Text object
        color_text = Text()
        # Apply the color to the name itself, padded for alignment
        color_text.append(f"{color_name:<22}", style=color_name)
        # Add hex and rgb values in a dimmed style for context
        #color_text.append(f" {rgb_triplet.hex}", style="dim")
        #color_text.append(f" {rgb_triplet.rgb}", style="dim")
        renderables.append(color_text)

    console.print(Columns(renderables, equal=True, expand=True, column_first=True))
    return True
