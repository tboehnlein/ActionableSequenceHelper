import colorsys
import random
from rich.text import Text
from rich.style import Style
from rich.color import Color, blend_rgb

def gradient_text(text: str, start_color: str, end_color: str) -> Text:
    """Creates rich Text with a gradient effect."""
    
    # Parse the colors into Color objects, then get their RGB triplets
    start_rgb = Color.parse(start_color).get_truecolor()
    end_rgb = Color.parse(end_color).get_truecolor()
    
    gradient = Text()
    text_length = len(text)
    
    if text_length == 0:
        return gradient

    for i, char in enumerate(text):
        # Calculate the blend ratio (0.0 to 1.0)
        # For a single character, blend_ratio will be 0.0
        blend_ratio = i / (text_length - 1) if text_length > 1 else 0.0
        
        # Get the interpolated color
        interpolated_rgb = blend_rgb(start_rgb, end_rgb, cross_fade=blend_ratio)
        
        # Create a style with the new color
        char_style = Style(color=interpolated_rgb.hex)
        
        # Append the character with its specific style
        gradient.append(char, style=char_style)
        
    return gradient

def get_color_from_hue(hue: float) -> str:
    """
    Calculates an RGB color string from a hue value (0.0 to 1.0).
    """
    # Convert HSV to RGB. Saturation and Value are 1.0 for bright, vibrant colors.
    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    # Scale to 0-255 for rich
    red, green, blue = (int(c * 255) for c in rgb)
    return f"rgb({red},{green},{blue})"

def rainbow_text(text: str, start_hue: float = None) -> Text:
    """Creates rich Text with a rainbow gradient effect with a random start color."""
    if start_hue is None:
        start_hue = random.random()

    rainbow = Text()
    text_length = len(text)
    
    if text_length == 0:
        return rainbow

    for i, char in enumerate(text):
        # Calculate how far into the text we are (0.0 to 1.0)
        ratio = i / text_length if text_length > 0 else 0
        # Calculate the hue, starting from a random point and wrapping around
        hue = (start_hue + ratio) % 1.0
        color_str = get_color_from_hue(hue)
        
        # Create a style with the new color
        char_style = Style(color=color_str)
        
        # Append the character with its specific style
        rainbow.append(char, style=char_style)
        
    return rainbow
