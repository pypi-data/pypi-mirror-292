import zipfile
import tempfile
import os

from io import BytesIO, TextIOWrapper

import PIL.Image as im
from pylagg.cgr.image_gen import generate_image

from typing import Dict, Tuple

def contains_valid_characters(input_string: str) -> bool:
    """
    Checks if the given input string contains valid base pair characters
    """    
    for char in input_string:
        if char not in {'A', 'T', 'C', 'G'}:
            return False
    
    return True

def parse_count_file_line(line: str, k: int) -> Tuple[str, int]:
    """
    Reads a line from an input counts file with a given kmer length 'k', returns the tuple: (kmer, count)
    """

    line_split = line.split()
    kmer = line_split[0]

    if k <= 0:
        raise Exception("The k-mer length must be greater than zero")
    
    if len(kmer) != k:
        raise Exception(f"The k-mer does match the reported length k={k}")

    if not contains_valid_characters(kmer):
        raise Exception(f"Invalid k-mer character in {kmer} (valid characters are A, T, C, G)")

    try:
        count = int(line_split[1])
    except ValueError:
        raise Exception("Count must only contain integer values")

    if count < 1:
        raise Exception("All k-mer counts must be ≥1")
    
    return (kmer, count)


def count_file_to_dictionary(file: TextIOWrapper) -> Dict[str, int]:
    """
    Takes a counts file as input and outputs a dictionary representation used later for image generation
    """

    k_dict = {}

    with file:
        k = len(file.readline().split()[0])
        file.seek(0)

        for line in file:
            if 'N' in line: continue
            (kmer, count) = parse_count_file_line(line, k)
            k_dict.update({kmer : count})

    return k_dict

def count_file_to_image(input_data: TextIOWrapper, verbose=True) -> im.Image:
    """
    Takes a counts file as input and returns the generated image as an image object
    """

    k_dict = count_file_to_dictionary(input_data)
    return generate_image(k_dict, verbose)

def count_file_to_image_file(input_data: TextIOWrapper, output_file: str | BytesIO, output_type="png", verbose=True):
    """
    Takes counts file data and creates an image at the provided file path or buffer with the given output file type
    """
    
    img = count_file_to_image(input_data, verbose)
    img.save(output_file, output_type)

def counts_zip_to_images_zip(input_zip_path: str, output_zip_path: str, verbose=True):
    """
    Takes a zip file of multiple kmer counts data and creates a zip file containing all image outputs
    """

    # check if input is a zip folder
    if not input_zip_path.endswith('.zip'):
        raise Exception("Input is not a zip folder.")
    
    # Create a temporary folder/directory to store processed files
    with tempfile.TemporaryDirectory() as temp_dir:
    
        # Open the zip folder
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            current_file = 0

            # Iterate over the items in the zip folder
            for zip_info in zip_ref.infolist():
                with zip_ref.open(zip_info.filename) as file:
                    # send each file in the folder
                    current_file += 1
                    if verbose:
                        print(f"\nProcessing {current_file}/{len(zip_ref.infolist())}: {zip_info.filename}")

                    temp_img = count_file_to_image(TextIOWrapper(file, encoding='utf-8'))
                    
                    # save each generated image to our temporary folder/directory
                    temp_img_path = os.path.join(temp_dir, f"{os.path.splitext(zip_info.filename)[0]}.png")
                    os.makedirs(os.path.dirname(temp_img_path), exist_ok=True)
                    with open(temp_img_path, 'wb'):
                        temp_img.save(temp_img_path)

        # Create the output zip folder if it doesn't exist
        os.makedirs(output_zip_path, exist_ok=True)
        
        # Construct the path for the output zip file
        input_zip_basename = os.path.basename(input_zip_path)
        output_zip_basename = f"{os.path.splitext(input_zip_basename)[0]}_output.zip"
        output_zip_file = os.path.join(output_zip_path, output_zip_basename)
        
        # Create a new zip file since the output is a string path
        with zipfile.ZipFile(output_zip_file, 'w') as output_zip:
            # Add all files from temp_dir to the output zip folder
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    output_zip.write(file_path, os.path.relpath(file_path, temp_dir))