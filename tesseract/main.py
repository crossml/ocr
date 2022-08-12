"""
@author: crossml

Optical Character Recognition for images, Pdfs, zip files, tif files.
In this module We have used tesseract ocr for proceesing documents.
You can give an any document and generate meaningful json of that document.
"""
import os
import json
import zipfile
import shutil
import boto3
import pytesseract
from pytesseract import Output
from PIL import Image
from PIL import ImageSequence
from pdf2image import convert_from_path
from config import OUTPUT_PATH
from config import EXTENSION_LIST

SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(local_file_path, storage_path):
    """
    This module is used to save files from an entire folder to AWS S3 Bucket
    User will give input file path and S3 bucket name.
    This module will cretae a dir named "tesseract_output" in S3 and save the output
    to that folder.

    Args:
        local_file_path (str): Input file path of the file given by user
        storage_path (string): name of s3 bucket.

    """
    try:
        # saving file to s3
        for filename in os.listdir(local_file_path):
            S3.meta.client.upload_file(
                local_file_path+'/'+filename, storage_path, os.path.join('tesseract_output', os.path.basename(local_file_path), filename))
            return (os.path.join('tesseract_output', os.path.basename(local_file_path), filename))
    except Exception as error:
        return error


class TessaractOcr:
    """
    Tesseract ocr pipeline for images pdf tif jpef zip file read.
    Attributes:
    1. config (dict): dictionary of storage type and storage path.
    Methods:
    process_image:
        method for process the images of type jpg, jpeg, tif, png.
    process_pdf:
        method for process the pdf files.
    process_zip:
        method for process the zip files.
    extract_text_from_image:
        method for extracting text from image,create json file of ocr
        result and upload the output file in s3 or save file in local system
        according to user input.
    """

    def __init__(self, config):
        """
        Args:
            config (dict): dictionary of storage type and storage path.
        """
        self.config = config

    def extract_text_from_image(self, image, file_name, index):
        """
        In this function we will extract data from the image objects.
        Then we will proces sthe data to store the output in json and text format.
        Args:
            image (object): image object from process pdf or image function
            file_name (str): name of the input file
            index (int): index no of image object
        """
        try:
            # removing extension from input file name for output file initial name
            file_name = os.path.basename(file_name)
            output_filename = os.path.splitext(file_name)[0]
            # processing image using Tessaract Ocr
            process_image_txt = pytesseract.image_to_string(
                image, output_type=Output.DICT)
            process_image = pytesseract.image_to_data(
                image, output_type=Output.DICT)
            temp_path = OUTPUT_PATH+output_filename
            if not os.path.exists(temp_path):
                os.makedirs(OUTPUT_PATH+output_filename)
            # writing output to json file
            with open(temp_path+'/' + output_filename+'('+str(index) + ')' + '.json', 'w') as f:
                json_list = []
                for left, top, width, height, text, conf in zip(process_image.get('left'),
                                                                process_image.get(
                                                                    'top'),
                                                                process_image.get(
                                                                    'width'),
                                                                process_image.get(
                                                                    'height'),
                                                                process_image.get(
                                                                    'text'),
                                                                process_image.get('conf')):
                    # removing empty values from output
                    if float(conf) > 0:
                        output_json = {'left': left, 'top': top, 'right': left+width,
                                       'bottom': top+height, 'text': text, 'confidence':
                                       round(float(conf), 2)}
                        json_list.append(output_json)
                f.write(json.dumps(json_list))
                path = temp_path+'/'+output_filename+'('+str(index)+').jpg'
                image.save(path)
            if config['storage_type'].lower() == 'local':
                shutil.copytree(temp_path, os.path.join(
                    config['storage_path'], output_filename), symlinks=False, ignore=None,
                    ignore_dangling_symlinks=False, dirs_exist_ok=True)
            elif config['storage_type'].lower() == 'aws':
                upload_file_to_s3(temp_path, config['storage_path'])
        except Exception as error:
            return error

    def process_image(self, input_file):
        """
        In this function we will take image from the user
        and read that image using open function of Image module.
        Then we will enumerate the image to get index no. and image object
        from the given object.
        Args:
            input_file (str): input(image) file from the user
        """
        try:
            file_name = Image.open(input_file)
            # processing image using Tessaract Ocr
            for index, page in enumerate(ImageSequence.Iterator(file_name)):
                self.extract_text_from_image(page, input_file, index)
        except Exception as error:
            return error

    def process_pdf(self, input_file):
        """
        In this function we will take pdf file from the user
        and iterate over each page of the pdf using convert_from_path function
        and store them in images module.
        Then we will enumerate the image to get index no. and image object
        from the given object.
        Args:
            input_file (str): input(pdf) file from the user
        """
        try:
            images = convert_from_path(input_file)
            for index, image in enumerate(images):
                self.extract_text_from_image(image, input_file, index)
        except Exception as error:
            return error

    def process_zip(self, input_file):
        """
        In this function we will take zip file from the user and validate the zip
        file. After that the zip file will be iterated using namelist function and
        save them to /tmp/ of loacl device.
        Then after checking the extension of the file process image or pdf function
        will be called.
        Args:
            input_file (str): input(zip) file from the user
        """
        try:
            # reading zip file
            with zipfile.ZipFile(input_file, mode="r") as file_list:
                # getting list of file inside zip
                # iterating over each file of zip
                for file in file_list.namelist():
                    file_list.extract(file, OUTPUT_PATH)  # saving file
                    # getting extension of file
                    extension = os.path.splitext(file)[-1].lower()
                    # if extesnion is image then calling image processing
                    if extension in EXTENSION_LIST:
                        self.process_image(OUTPUT_PATH+file)
                    # else calling pdf procssing
                    elif extension == '.pdf':
                        self.process_pdf(OUTPUT_PATH+file)
                    else:
                        return "Invalid extension"
        except Exception as error:
            return error
