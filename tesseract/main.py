"""
tessaract ocr pipeline
"""
import os
import json
import cv2
import pytesseract
import zipfile
from pytesseract import Output
from pdf2image import convert_from_path
from config import INPUT_PATH
from config import OUTPUT_PATH


class TessaractOcr:
    """
    tesseract ocr
    """

    def __init__(self):
        pass

    def image_processing(self, input_file):
        """
        image processing

        Args:
            input_file (str): input file name
        """
        file_name = input_file
        output_filename = os.path.splitext(file_name)[0]
        img = cv2.imread(INPUT_PATH+'/'+file_name)
        process_image = pytesseract.image_to_data(img, output_type=Output.DICT)
        with open(OUTPUT_PATH+'/' + output_filename+'.json', 'w') as f:
            process_image = {os.path.basename(file_name): [{'Confidence Score': conf, 'Text': text,
                                                           'Line no.': line_no, 'Top': top, 'Left':
                                                            left, } for conf, text, line_no,
                                                           top, left in zip(process_image['conf'],
                                                                            process_image['text'],
                                                                            process_image['line_num'],
                                                                            process_image['top'],
                                                                            process_image['left'])]}
            json.dump(process_image, f, indent=4)

    def pdf_processing(self, input_file):
        """
        pdf processing

        Args:
            input_file (str): input file name
        """
        pdf_pages = convert_from_path(INPUT_PATH+'/' + input_file, 500)
        output_filename = os.path.splitext(input_file)[0]
        counter = 0
        for i in pdf_pages:
            process_image = pytesseract.image_to_data(
                i, output_type=Output.DICT)
            process_image = {os.path.basename(input_file): [{'Confidence Score': conf, 'Text': text,
                                                            'Line no.': line_no, 'Top': top, 'Left':
                                                             left, } for conf, text, line_no,
                                                            top, left in zip(process_image['conf'],
                                                                             process_image['text'],
                                                                             process_image['line_num'],
                                                                             process_image['top'],
                                                                             process_image['left'])]}
            with open(OUTPUT_PATH+'/' + output_filename+str(counter)+'.json', 'w') as f:
                json.dump(process_image, f, indent=4)
            counter += 1

    def zip_processing(self, input_file):
        """
        zip processing

        Args:
            input_file (str): input file name
        """
        inp_file = input_file
        with zipfile.ZipFile(INPUT_PATH+'/' + inp_file, mode="r") as archive:
            archive.printdir()
            for file in archive.namelist():
                archive.extract(file, "/tmp")
                output_filename = os.path.splitext(file)[0]
                process_image = pytesseract.image_to_data(
                    "/tmp/"+file, output_type=Output.DICT)
                with open(OUTPUT_PATH+'/' + output_filename+'.json', 'w') as f:
                    process_image = {os.path.basename(file): [{'Confidence Score': conf,
                                                              'Text': text, 'Line no.': line_no,
                                                               'Top': top, 'Left': left, }
                                                              for conf, text, line_no, top,
                                                              left in zip(process_image['conf'],
                                                                          process_image['text'],
                                                              process_image['line_num'],
                                                              process_image['top'],
                                                              process_image['left'])]}
                    json.dump(process_image, f, indent=4)


