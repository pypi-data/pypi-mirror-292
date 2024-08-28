import PIL.Image as im
from PIL import ImageChops

import numpy as np

import cgr.kmer_input as kmer_input

import os
# the direct path for this python file (useful for finding image paths)
dir_path = os.path.dirname(os.path.realpath(__file__))


def diff_test(counts_file_path: str, py_img_path: str, r_img_path: str, diff_img_path: str | None, tolerance: int = 0):
    '''
    Checks if the image output from the counts_file_path matches the original R implementation up to an optional tolerance (0-255).
    Optionally allows for saving the difference between the outputs in diff_img_path.
    '''

    with open(counts_file_path) as f:
        kmer_input.count_file_to_image_file(f, py_img_path)

    r_img = im.open(r_img_path).convert("RGB")
    py_img = im.open(py_img_path).convert("RGB")
    diff = ImageChops.difference(r_img, py_img)

    if diff_img_path is str:
        diff.save(fp=diff_img_path, format="png")

    diff_arr = np.asarray(diff)

    return np.all(diff_arr <= tolerance)


def test_small_diff():
    '''
    Compares the small k10 counts file to the original R output.
    Passes as long as no pixel channel values are different by 1/255.
    '''

    assert diff_test(
        counts_file_path=dir_path + "/small_k10.txt",
        py_img_path=dir_path + "/small_k10_py.png",
        r_img_path=dir_path + "/small_k10_r.png",
        diff_img_path=dir_path + "/small_diff.png",
        tolerance=1
    )


def test_large_diff():
    '''
    Compares a large (8mb+) k10 counts file to the original R output.
    Passes as long as no pixel channel values are different by more than 93/255.
    '''

    assert diff_test(
        counts_file_path=dir_path + "/large_k10.txt",
        py_img_path=dir_path + "/large_k10_py.png",
        r_img_path=dir_path + "/large_k10_r.png",
        diff_img_path=dir_path + "/large_diff.png",
        tolerance=93
    )
