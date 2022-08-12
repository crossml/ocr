"""
@author: Crossml

Optical Character Recognition for images, Pdfs, zip files, tif files.
In this module, We have used EasyOCR for processing documents.
You can give any document and generate meaningful JSON of that document.
"""
import json
import os
import shutil
from turtle import width
import easyocr
import boto3
from zipfile import ZipFile
from pdf2image import convert_from_path
from PIL import ImageSequence
from PIL import Image
from config import EXTENSION_LISTS
from config import TEMP

EASYOCR_OUTPUT_PATH='easyocr_output'
SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(json_path,storage_path):
    """
    This method is used to save files from an entire folder to AWS S3 Bucket
    The user will give the input file path and S3 bucket name.
    This module will create a dir named "easyocr_output" in S3 and save the output
    to that folder.

    Args:
        json_path (dict): path where file is store on s3.
        storage_path (string): name of s3 bucket.
    """
    try:
        for file in os.listdir(json_path):
            s3_json_path = os.path.join(json_path, file)
            S3.meta.client.upload_file(
                s3_json_path, storage_path, os.path.join(EASYOCR_OUTPUT_PATH,os.path.basename(json_path),file))
    except Exception as error:
        print(error)
        return error


class EasyOcrProcessor:
    """
    Easy ocr pipeline for images pdf tif jpef zip file read.

    Attributes:

    1. config (dict): dictionary of storage type and storage path.

    Methods:

    process_image:

        method for process the images of type jpg, jpeg, tif.

    process_pdf:

        method for process the pdf files.

    process_zip:

        method for process the zip files.

    image_read:

        method for create image path and upload the file in s3 or save file in local system
        according to user input.

    create_json:

        method for create json file of ocr result.
    """
    def __init__(self, config):
        self.config=config

    def create_json(self, result, file):
        """
        Function for create json of ocr result and txt file of text extracted from image.

        1. Create dictionary of result ocr in proper format.
        2. Save the dictionary in file with the name of relative image.

        Args:
            result (dict): dictionary of result.
            file (string): name of file.
        """
        try:
            dictionary = {}
            # create proper json to store in json file
            dictionary = [{'left': int(i[0][0][0]),
                        'top':int(i[0][1][1]),
                        'right':int(i[0][2][0]),
                        'bottom':int(i[0][3][1]),
                        'text':i[1],
                        'confidence':i[-1]} for i in result]
            text_list=[i[1]+'\n' for i in result]
            # get json file path
            json_name = os.path.splitext(file)[0]
            # save text output file
            with open(json_name+".txt", "w") as textfile:
                textfile.writelines(text_list)
            # create json log file
            with open(json_name+".json", "w") as outfile:
                json.dump(dictionary, outfile)
        except Exception as error:
            print(error)
            return error


    def image_read(self, path, images):
        """
        Function for create image path and upload the file in s3 or save file in local system
        according to user input.

        1. Make folder of image name.
        2. save image in relative folder for each image.
        3. read text from each image and store json in relative folder.
        4. upload image and json file on s3.

        Args:
            path (string): path of image.
            images (object): object of image.
        """
        try:
            reader = easyocr.Reader(['hi', 'en'],gpu=False)
            path = os.path.basename(path)
            # get file name
            file_name = os.path.splitext(path)[0]
            # get folder path
            folder_path = TEMP+file_name
            # get file extension
            file_extension = os.path.splitext(path)[-1].lower()
            # create folder if not exists
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # iterate image
            for index, img in enumerate(images):
                if file_extension == '.tif' or file_extension == '.pdf':
                    file_path = file_name+'_'+str(index)+'.jpg'
                else:
                    file_path = path
                file_path = os.path.join(folder_path, file_path)
                # save image
                img.save(file_path)
                # read the image data
                result = reader.readtext(file_path)
                # function to create json
                self.create_json(result, file_path)
            if self.config.get('storage_type').lower()=='aws':
                # upload file into s3
                upload_file_to_s3(folder_path, self.config.get('storage_path'))
            elif self.config.get('storage_type').lower()=='local':
                shutil.copytree(folder_path, os.path.join(self.config.get('storage_path'),file_name), symlinks=False, ignore=None, ignore_dangling_symlinks=False, dirs_exist_ok=True)
        except Exception as error:
            print(error)
            return error

    # def image_process(self, path):
    def process_image(self, path):
        """
        In this function, we will take an image from the user
        and read that image using the open function of the Image module.
        Then we will enumerate the image to get index no. and image object
        from the given object.
        
        Args:
            path (string): file path.
        """
        try:
            img = Image.open(path)
            images = ImageSequence.Iterator(img)
            # read the image
            self.image_read(path, images)
        except Exception as error:
            print(error)
            return error

    # def pdf_process(self, path):
    def process_pdf(self, path):
        """
        In this function, we will take a pdf file from the user
        and iterate over each page of the pdf using the convert_from_path function.
        Then we will enumerate the image to get index no. and image object
        from the given object.
        Process the pdf file.

        1. convert each page of pdf into image.
        2. pass images to image read function to get text from each image.

        Args:
            path (string): pdf file path.
        """
        try:
            # convert the pdf into images
            images = convert_from_path(path)
            # read the image
            self.image_read(path, images)
        except Exception as error:
            print(error)
            return error

    def process_zip(self, path):
        """
        In this function, we will take the zip file from the user and check the files in zip.
        and than extract each file one by one and saved to /tmp/ of the local device.
        Then after checking the extension of the file process image or pdf function
        will be called.

        1. Extract each file in zip one by one.
        2. If file is of pdf type than file is pass in process_pdf function for further process.
        3. If file is of image type than it is pass in process_image function for further process.

        Args:
            path (string): zip file path.
        """
        try:
            # read the zip file
            with ZipFile(path, 'r') as zip_file:
                for file in zip_file.namelist():
                    zip_file.extract(file, TEMP)
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LISTS:
                        self.process_image(TEMP+file)
                    elif extension == '.pdf':
                        self.process_pdf(TEMP+file)
                    else:
                        print("Invalid Extension")
                        return "Invalid Extension"
        except Exception as error:
            print(error)
            return error

config={'storage_path':'/home/yakul/Desktop/','storage_type':'local'}
process=EasyOcrProcessor(config)
process.process_pdf('/home/yakul/Desktop/IDX/ocr/easy_ocr/KN_UIC_ICA3.pdf')
