import lzma
from os import remove

def lzma_and_remove(input_filepath, output_filepath):
    with open(input_filepath, "rb") as input_file:
        with lzma.open(output_filepath, "w") as output_file:
            output_file.write(input_file.read())
        remove(input_filepath)
