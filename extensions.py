import colorsys
import random
import re
from rich.text import Text
from rich.style import Style
from rich.color import Color, blend_rgb



from rich.style import Style
from rich.color import Color, blend_rgb

def gradient_text(text: str, start_color: str, end_color: str, by_word: bool = False) -> Text:
    """
    Creates rich Text with a gradient effect.

    Args:
        text (str): The text to color.
        start_color (str): The starting color for the gradient.
        end_color (str): The ending color for the gradient.
        by_word (bool, optional): If True, colors word-by-word instead of character-by-character.
                                  Defaults to False.

    Returns:
        Text: The rich Text object with gradient colors.
    """

    # Parse the colors into Color objects, then get their RGB triplets
    start_rgb = Color.parse(start_color).get_truecolor()
    end_rgb = Color.parse(end_color).get_truecolor()

    gradient = Text()
    text_length = len(text)

    if text_length == 0:
        return gradient

    if by_word:
        # Split text into words and separators (spaces)
        parts = re.split(r'(\s+)', text)
        char_offset = 0
        for part in parts:
            if not part:
                continue

            if part.isspace():
                gradient.append(part)
            else:  # It's a word
                # Calculate blend ratio for the first character of the word
                blend_ratio = char_offset / (text_length - 1) if text_length > 1 else 0.0

                # Get the interpolated color
                interpolated_rgb = blend_rgb(start_rgb, end_rgb, cross_fade=blend_ratio)

                # Create a style with the new color
                word_style = Style(color=interpolated_rgb.hex)

                # Append the word with its specific style
                gradient.append(part, style=word_style)

            char_offset += len(part)
    else:
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

def rainbow_text(text: str, start_hue: float = None, by_word: bool = False) -> Text:
    """
    Creates rich Text with a rainbow gradient effect.

    Args:
        text (str): The text to color.
        start_hue (float, optional): The starting hue for the rainbow (0.0 to 1.0).
                                     Defaults to a random value.
        by_word (bool, optional): If True, colors word-by-word instead of character-by-character.
                                  Defaults to False.

    Returns:
        Text: The rich Text object with rainbow colors.
    """
    if start_hue is None:
        start_hue = random.random()

    rainbow = Text()
    text_length = len(text)

    if text_length == 0:
        return rainbow

    if by_word:
        # Split text into words and separators (spaces)
        parts = re.split(r'(\s+)', text)
        char_offset = 0
        for part in parts:
            if not part:
                continue

            if part.isspace():
                rainbow.append(part)
            else:  # It's a word
                # Calculate hue for the first character of the word
                ratio = char_offset / text_length if text_length > 0 else 0
                hue = (start_hue + ratio) % 1.0
                color_str = get_color_from_hue(hue)
                word_style = Style(color=color_str)

                rainbow.append(part, style=word_style)

            char_offset += len(part)
    else:
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
