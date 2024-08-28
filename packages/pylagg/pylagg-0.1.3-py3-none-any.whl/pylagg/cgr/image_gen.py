import math
import numpy as np
import PIL.Image as im

from typing import Tuple, Dict

from tqdm import tqdm


def normalize(arr: np.ndarray) -> np.ndarray:
    """
    Takes a numpy array and returns it's normalized verison 
    """
    return arr / np.max(arr)


def calculate_pos(kmer: str, size: int, corner_labels: Tuple[str, str, str, str]) -> Tuple[int, int]:
    """
    Returns the pixel position (x, y) of a kmer in a CGR image with a given size
    """

    x, y = 0, 0

    # use bit shifting instead of division to avoid floating point values
    offset = size >> 1

    bot_left, _, top_right, bot_right = corner_labels

    for base in reversed(kmer):
        if base == top_right or base == bot_right:
            x += offset

        if base == bot_left or base == bot_right:
            y += offset

        offset >>= 1

    return (x, y)


def generate_image_arr(k_dict: Dict[str, int], verbose=True) -> np.ndarray:
    """
    Generates a numpy array representing an image covering RGB channels
    """

    k = len(next(iter(k_dict)))  # gets the length of the first key in k_dict

    size = 2 ** k
    r = np.zeros((size, size))
    g = np.zeros((size, size))
    b = np.zeros((size, size))

    for kmer, count in tqdm(iterable=k_dict.items(), disable=not verbose):
        count = math.log10(count)

        # weak H-bonds W = {A, T} and strong H-bonds S = {G, C} on the diagonals
        r_pos = calculate_pos(kmer, size, ('A', 'G', 'T', 'C'))
        r[r_pos] = count
        
        # purine R = {A, G} and pyrimidine Y = {C, T} on the diagonals
        g_pos = calculate_pos(kmer, size, ('A', 'T', 'G', 'C'))
        g[g_pos] = count

        # amino group M = {A, C} and keto group K = {G, T} on the diagonals
        b_pos = calculate_pos(kmer, size, ('A', 'T', 'C', 'G'))
        b[b_pos] = count

    rgb = np.dstack((r, g, b))

    return (normalize(rgb) * 255).astype(np.uint8)


def generate_image(k_dict: Dict[str, int], verbose=True) -> im.Image:
    """
    Generates an PIL Image using a given dictionary of k counts
    """
    chaos = generate_image_arr(k_dict, verbose)
    return im.fromarray(chaos)
