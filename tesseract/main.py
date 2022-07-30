"""
tessaract ocr pipeline
"""
import os
import json
import zipfile
import boto3
import pytesseract
from pytesseract import Output
from PIL import Image, ImageSequence
from pdf2image import convert_from_path

from config import EXTENSION_LIST
from config import OUTPUT_PATH

SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(local_file_path):
    """
    Upload File to s3
    """
    try:
        # saving file to s3
        S3.meta.client.upload_file(
            local_file_path, "input-adaptor", local_file_path)
        # return INPUT_FILE_FOLDER + os.path.basename(local_file_path)
    except Exception as error:
        return error


class TessaractOcr:
    """
    tesseract ocr
    """

    def extract_text_from_image(self, image, file_name, index):
        """
        extracting text from images

        Args:
            image (object): image object
            file_name (str): name of file
            index (int): index no of pages
        """
        # removing extension from input file name for output file initial name
        output_filename = os.path.splitext(file_name)[0]
        # processing image using Tessaract Ocr
        process_image = pytesseract.image_to_data(
            image, output_type=Output.DICT)
        if not os.path.exists(OUTPUT_PATH+output_filename):
            os.makedirs(OUTPUT_PATH+output_filename)
        # writing output to json file
        outs = OUTPUT_PATH+output_filename+'/'
        with open(outs + output_filename+str(index) + '.json', 'w') as f:
            output_json = {os.path.basename(file_name):
                           [{'Confidence Score': conf, 'Text': text,
                             'Line no.': line_no, 'Top': top, 'Left':
                             left, } for conf, text, line_no,
                            top, left in zip(process_image['conf'],
                                             process_image['text'],
                                             process_image['line_num'],
                                             process_image['top'],
                                             process_image['left'])]}
            json.dump(output_json, f, indent=4)
            path = outs+output_filename+'('+str(index)+').jpg'
            image.save(path)
            upload_file_to_s3(path)
            path = outs+output_filename+str(index) + '.json'
            upload_file_to_s3(path)

    def image_processing(self, input_file):
        """
        image processing

        Args:
            input_file (str): input file name
        """

        file_name = Image.open(input_file)
        # processing image using Tessaract Ocr
        for index, page in enumerate(ImageSequence.Iterator(file_name)):
            self.extract_text_from_image(page, input_file, index)

    def pdf_processing(self, input_file):
        """
        pdf processing

        Args:
            input_file (str): input file name
        """
        images = convert_from_path(input_file)
        file_name = input_file.split('/')[-1]
        file_name = file_name.split('.')[0]
        for index, image in enumerate(images):
            self.extract_text_from_image(image, input_file, index)

    def zip_processing(self, input_file):
        """
        zip processing

        Args:
            input_file (str): input file name
        """
        inp_file = input_file
        # reading zip file
        with zipfile.ZipFile(inp_file, mode="r") as file_list:
            # getting list of file inside zip
            # iterating over each file of zip
            for file in file_list.namelist():
                file_list.extract(file, "")  # saving file
                # getting extension of file
                extension = os.path.splitext(file)[-1].lower()
                # if extesnion is image then calling image processing
                if extension in EXTENSION_LIST:
                    self.image_processing(file)
                   # else calling pdf procssing
                else:
                    self.pdf_processing(file)
