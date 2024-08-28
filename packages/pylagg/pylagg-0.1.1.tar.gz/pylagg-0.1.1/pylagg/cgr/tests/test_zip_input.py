import zipfile
import os

from cgr.kmer_input import counts_zip_to_images_zip

# the direct path for this python file (useful for finding image paths)
dir_path = os.path.dirname(os.path.realpath(__file__))


def compare_zip_contents(zip_file_path1, zip_file_path2):
    """
    Compares the contents of the two input zip files.
    Returns boolean of whether the contents of the zip files are the same.
    
    Args:
    - zip_file_path1 (str): Path to the first zip file.
    - zip_file_path2 (str): Path to the second zip file.
    """
    # Create ZipFile objects for both zip files
    with zipfile.ZipFile(zip_file_path1, 'r') as zip1, zipfile.ZipFile(zip_file_path2, 'r') as zip2:
        # Get lists of file names in each zip file
        file_list1 = sorted(zip1.namelist())
        file_list2 = sorted(zip2.namelist())
        
        # Compare the file lists
        if file_list1 != file_list2:
            return False
        
        # Iterate through the files and compare their contents
        for file1, file2 in zip(file_list1, file_list2):
            # Compare the contents of each file in the zip files
            with zip1.open(file1, 'r') as file1_data, zip2.open(file2, 'r') as file2_data:
                if file1_data.read() != file2_data.read():
                    return False
    
    return True


# Compares the output of the small zip input with the expected output
def test_zip_input_one():
    counts_zip_to_images_zip(dir_path + '/zip_test_input1.zip', dir_path)
    is_match = compare_zip_contents(dir_path + '/zip_test_input1_output.zip', dir_path + '/zip_test_input1_output_expected.zip')

    assert (is_match)


# Compares the output of the large zip input with the expected output
def test_zip_input_two():
    counts_zip_to_images_zip(dir_path + '/zip_test_input2.zip', dir_path)
    is_match = compare_zip_contents(dir_path + '/zip_test_input2_output.zip', dir_path + '/zip_test_input2_output_expected.zip')

    assert (is_match)