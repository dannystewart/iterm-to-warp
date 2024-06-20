#!/usr/bin/env python3

"""Convert an iTerm plist-based `.itermcolors` theme file to a YAML Warp theme."""

import argparse
import plistlib
import re
import yaml

ansi_color_names = [
    "Black",
    "Red",
    "Green",
    "Yellow",
    "Blue",
    "Magenta",
    "Cyan",
    "White",
    "Bright Black (Gray)",
    "Bright Red",
    "Bright Green",
    "Bright Yellow",
    "Bright Blue",
    "Bright Magenta",
    "Bright Cyan",
    "Bright White",
]


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    """
    Convert RGB components from range [0, 1] to hex format.

    Args:
        rgb: Tuple of RGB components in range [0, 1].

    Returns:
        Hexadecimal representation of the RGB color.
    """
    r, g, b = (int(c * 255) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def extract_rgb_components(color_dict: dict[str, float]) -> tuple[float, float, float]:
    """
    Extract RGB components from a color dictionary.

    Args:
        color_dict: Dictionary containing RGB components.

    Returns:
        Tuple of RGB components.
    """
    red = color_dict.get("Red Component")
    green = color_dict.get("Green Component")
    blue = color_dict.get("Blue Component")
    return red, green, blue


def extract_ansi_colors(plist_data: dict) -> list[tuple[int, str]]:
    """
    Extract ANSI color values from plist data.

    Args:
        plist_data: Dictionary containing plist data.

    Returns:
        List of tuples containing color index and hex color value.
    """
    colors = []

    for key, color_dict in plist_data.items():
        if match := re.search(r"Ansi (\d+) Color", key):
            color_index = int(match[1])
            if color_index < len(ansi_color_names):
                rgb = extract_rgb_components(color_dict)
                if None not in rgb:
                    hex_color = rgb_to_hex(rgb)
                    colors.append((color_index, hex_color))

    return colors


def extract_theme_colors(plist_data: dict) -> dict[str, str]:
    """
    Extract theme-specific colors from plist data.

    Args:
        plist_data: Dictionary containing plist data.

    Returns:
        Dictionary of theme-specific colors.
    """
    theme_colors = {}
    keys_of_interest = {
        "Background Color": "background",
        "Foreground Color": "foreground",
        "Link Color": "accent",
    }

    for key, value in keys_of_interest.items():
        color_dict = plist_data.get(key)
        if color_dict:
            rgb = extract_rgb_components(color_dict)
            if None not in rgb:
                hex_color = rgb_to_hex(rgb)
                theme_colors[value] = hex_color

    return theme_colors


def sort_colors_for_terminal(colors: list[tuple[int, str]]) -> dict[str, dict[str, str]]:
    """
    Organize terminal colors into 'normal' and 'bright' categories.

    Args:
        colors: List of tuples containing color index and hex color value.

    Returns:
        Dictionary of organized terminal colors.
    """
    terminal_colors = {"normal": {}, "bright": {}}
    for index, hex_color in colors:
        category = "normal" if index < 8 else "bright"
        color_name = ansi_color_names[index]
        color_key = (
            color_name.split()[0].lower()
            if category == "normal"
            else ansi_color_names[index - 8].split()[0].lower()
        )
        terminal_colors[category][color_key] = hex_color

    return terminal_colors


def convert_iterm_to_warp(input_file: str) -> None:
    """
    Convert iTerm plist-based itermcolors theme to Warp YAML theme.

    Args:
        input_file: Path to the input plist (itermcolors) file.
    """
    with open(input_file, "rb") as fp:
        plist_data = plistlib.load(fp)

    ansi_colors = extract_ansi_colors(plist_data)
    theme_colors = extract_theme_colors(plist_data)
    terminal_colors = sort_colors_for_terminal(ansi_colors)

    theme_name = input("\nEnter the theme name: ")
    output_file = f"{theme_name.lower().replace(' ', '_')}.yaml"

    theme = {
        "name": theme_name,
        "accent": theme_colors.get("accent", "#6ba4f8"),
        "background": theme_colors.get("background", "#131418"),
        "foreground": theme_colors.get("foreground", "#e6e6e6"),
        "details": "darker",
        "terminal_colors": terminal_colors,
    }

    with open(output_file, "w") as yaml_file:
        yaml.dump(theme, yaml_file, default_flow_style=False)

    print(f"\nTheme converted and saved as {output_file}.")


def main() -> None:
    """Get input file path from command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert iTerm theme to Warp theme.")
    parser.add_argument("input_file", help="Path to the input itermcolors file")
    args = parser.parse_args()

    convert_iterm_to_warp(args.input_file)


if __name__ == "__main__":
    main()
