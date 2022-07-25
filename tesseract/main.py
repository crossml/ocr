"""
tessaract ocr pipeline
"""
import os
import json
import zipfile
import cv2
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
from config import INPUT_PATH
from config import OUTPUT_PATH
from config import EXTENSION_LIST


class TessaractOcr:
    """
    tesseract ocr
    """

    def image_processing(self, input_file):
        """
        image processing

        Args:
            input_file (str): input file name
        """
        file_name = input_file  # input file name
        # removing extension from input file name for output file initial name
        output_filename = os.path.splitext(file_name)[0]
        img = cv2.imread(INPUT_PATH+'/'+file_name)  # reading image
        # processing image using Tessaract Ocr
        process_image = pytesseract.image_to_data(img, output_type=Output.DICT)
        # writing output to json file
        with open(OUTPUT_PATH+'/' + output_filename+'.json', 'w') as f:
            output_json = {os.path.basename(file_name): [{'Confidence Score': conf, 'Text': text,
                                                          'Line no.': line_no, 'Top': top, 'Left':
                                                          left, } for conf, text, line_no,
                                                         top, left in zip(process_image['conf'],
                                                                          process_image['text'],
                                                                          process_image['line_num'],
                                                                          process_image['top'],
                                                                          process_image['left'])]}
            json.dump(output_json, f, indent=4)

    def pdf_processing(self, input_file):
        """
        pdf processing

        Args:
            input_file (str): input file name
        """
        pdf_pages = convert_from_path(
            INPUT_PATH+'/' + input_file, 500)  # getting total no. of pages inside pdf
        # removing extension from input file name for output file initial name
        output_filename = os.path.splitext(input_file)[0]
        # counter to add after each page for pdf in json file to
        # prevent writing one file again and again
        counter = 0
        # iterating over each page of pdf
        for page in pdf_pages:
            # processing each page of pdf using Tessaract Ocr
            process_image = pytesseract.image_to_data(
                page, output_type=Output.DICT)
            # writing output to json file
            with open(OUTPUT_PATH+'/' + output_filename+str(counter)+'.json', 'w') as f:
                output_json = {os.path.basename(input_file): [{'Confidence Score': conf,
                                                               'Text': text, 'Line no.': line_no,
                                                               'Top': top, 'Left': left, } for
                                                              conf, text, line_no, top, left
                                                              in zip(process_image['conf'],
                                                                     process_image['text'],
                                                                     process_image['line_num'],
                                                                     process_image['top'],
                                                                     process_image['left'])]}
                json.dump(output_json, f, indent=4)
            counter += 1


def ocr_call(input_file):
    """
    Calling function on the basis of extension
    Args:
        input_file (str): input file

    """
    tessaract_object = TessaractOcr()  # creating object for TessaractOcr class
    # fetching extension to validate type of file
    extension = os.path.splitext(input_file)[-1].lower()
    # calling image process module
    if extension in EXTENSION_LIST:
        tessaract_object.image_processing(input_file)
    # calling pdf process module
    elif extension == ".pdf":
        tessaract_object.pdf_processing(input_file)
    elif extension == ".zip":
        inp_file = input_file
        # reading zip file
        with zipfile.ZipFile(INPUT_PATH+'/' + inp_file, mode="r") as file_list:
            # getting list of file inside zip
            # iterating over each file of zip
            for file in file_list.namelist():
                file_list.extract(file, "")  # saving file
                # getting extension of file
                extension = os.path.splitext(file)[-1].lower()
                # if extesnion is image then calling image processing
                if extension in EXTENSION_LIST:
                    tessaract_object.image_processing(file)
                # else calling pdf procssing
                else:
                    tessaract_object.pdf_processing(file)

    else:
        return "invalid file"
