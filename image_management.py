import cv2
import numpy as np
import os
from PIL import Image

def split_image(image):
    """
    Divide a PIL image into 3 vertical parts.

    Args:
        image: PIL image.

    Returns:
        list[PIL.Image.Image]: 3 PIL Images List.
    """
    
    
    width, height = image.size
    segment_width = width // 3

    # Splitting image
    part1 = image.crop((0, 0, segment_width, height))
    part2 = image.crop((segment_width, 0, 2 * segment_width, height))
    part3 = image.crop((2 * segment_width, 0, width, height))

    return [part1, part2, part3]
