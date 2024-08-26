"""
Color Manipulation and Analysis Utilities (lescolors / Les colors / The colors)

This module provides a set of functions for working with colors in various formats.
It includes utilities for calculating adjacent and analogous colors, finding complementary
colors, converting RGB values to hexadecimal format, and extracting the dominant color
from an image via a URL.

Functions:
    - adjacent_colors(rgb: list[int], d: float = DEG30) -> list[map]:
        Calculates and returns the adjacent colors on the color wheel for a given RGB value.

    - analogous_colors(rgb: list[int]) -> list[int]:
        Computes and returns the analogous colors for a given RGB value.

    - complementary(rgb: list[int]) -> list[int]:
        Computes and returns the complementary color for a given RGB value.

    - rgb_to_hex(rgb: list[int]) -> str:
        Converts an RGB color value to its hexadecimal (Hex) string format.

    - dominant_color_finder(image_url: str, quality: int = 1) -> list[int]:
        Extracts and returns the most dominant RGB color from an image located at a given URL.
        
Usage:
    This module can be used to explore color relationships, generate color schemes,
    and analyze colors from images. It is particularly useful for tasks related
    to graphic design, web development, and visual content creation.

Dependencies:
    - colorsys: A standard Python module for converting between color systems.
    - requests: A Python library for making HTTP requests.
    - colorthief: A library for grabbing the dominant color or a
                representative color palette from an image.

Examples:
    - Finding analogous colors for a given RGB value:
        print(analogous_colors([255, 0, 0]))

    - Getting the complementary color of a given RGB value:
        print(complementary([255, 0, 0]))

    - Converting an RGB value to Hex format:
        print(rgb_to_hex([255, 0, 0]))

    - Finding the dominant color in an image:
        print(dominant_color_finder(image_url='https://i.stack.imgur.com/JM4F2.png', quality=1))
"""

import colorsys
from io import BytesIO
from colorthief import ColorThief
import requests


DEG30 = 30/360.

def adjacent_colors(rgb: list[int], d: float = DEG30) -> list[map]:
    '''
    Takes in an RGB color value and returns a list of mapped adjacent colors.
    
    This function calculates the two adjacent colors in the color wheel, 
    separated by a given degree value `d`. The color is first converted 
    from RGB to HLS (Hue, Lightness, Saturation). The hue is then adjusted 
    by `d` degrees in both the positive and negative directions to find 
    the adjacent colors. These colors are converted back to RGB format 
    and returned as a list.

    Args:
        rgb (list[int]): A list containing the RGB components of the color.
        d (float): The degree difference used to calculate adjacent colors 
                   (default is 30 degrees, i.e., 1/12th of a full circle).

    Returns:
        list[map]: A list of two RGB values representing the adjacent colors.
    '''
    r, g, b = map(lambda x: x/255., rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = [(h + d) % 1 for d in (-d, d)]
    adjacent = [map(lambda x: int(round(x * 255)), colorsys.hls_to_rgb(hi, l, s))
                for hi in h]
    return adjacent

def analogous_colors(rgb: list[int]) -> list[int]:
    '''
    Takes in an RGB color value and returns a list of analogous colors.
    
    Analogous colors are those that are adjacent to each other on the 
    color wheel. This function uses the `adjacent_colors` function to 
    determine these colors and formats them as lists of integers.

    Args:
        rgb (list[int]): A list containing the RGB components of the color.

    Returns:
        list[list[int]]: A list of two lists, each containing the RGB values of an analogous color.
    '''
    colors = adjacent_colors(rgb)
    colors[0] = [i for i in colors[0]]
    colors[1] = [i for i in colors[1]]

    return colors

def complementary(rgb: list[int]) -> list[int]:
    '''Returns the RGB components of the complementary color.
    
    The complementary color is found by adding 180 degrees (0.5 in hue space) 
    to the hue of the original color in HSV space. The result is converted 
    back to RGB.

    Args:
        rgb (list[int]): A list containing the RGB components of the color.

    Returns:
        list[int]: A list containing the RGB values of the complementary color.
    '''
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    return [int(color) for color in colorsys.hsv_to_rgb((hsv[0] + 0.5) % 1, hsv[1], hsv[2])]

def rgb_to_hex(rgb: list[int]) -> str:
    '''
    Converts an RGB value to its hexadecimal (Hex) format.
    
    The RGB components are converted to a hex string prefixed with "#".

    Args:
        rgb (list[int]): A list containing the RGB components of the color.

    Returns:
        str: The hex representation of the color, prefixed with "#".
    '''
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

def dominant_color_finder(image_url: str, quality: int = 1) -> list[int]:
    '''
    Returns the most common RGB values from the image provided by a URL.
    
    This function downloads an image from the specified URL, processes 
    it to determine the most dominant color using the ColorThief library, 
    and returns the RGB values of that color.

    Args:
        image_url (str): The URL of the image to process.
        quality (int): An optional parameter to set the quality of the color extraction. 
                       Higher quality values are slower but more accurate.

    Returns:
        list[int]: A list containing the RGB values of the dominant color in the image.
    '''
    response = requests.get(image_url, timeout=2)
    image = ColorThief(BytesIO(response.content))
    color = image.get_color(quality = quality)

    return color

# Example usage:
# print(rgb_to_hex(
    # dominant_color_finder(
        # image_url = 'https://i.stack.imgur.com/JM4F2.png',
        # quality = 1)
    # )
# )
