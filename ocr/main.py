"""
@author: crossml

Optical Character Recognition for images, Pdfs, zip files, tif files.
In this module, We have used tesseract OCR for processing documents.
You can give any document and generate meaningful JSON of that document.
"""
import os
import json
import zipfile
import shutil
import boto3
import pytesseract
from pytesseract import Output
import easyocr
from PIL import Image
from PIL import ImageSequence
from pdf2image import convert_from_path
from config import OUTPUT_PATH
from config import EXTENSION_LIST
from zipfile import ZipFile


SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(local_file_path, storage_path):
    """
    This module is used to save files from an entire folder to AWS S3 Bucket
    The user will give the input file path and S3 bucket name.
    This module will create a dir named "tesseract_output" in S3 and save the output
    to that folder.

    Args:
        local_file_path (str): Input file path of the file given by the user
        storage_path (string): name of s3 bucket.

    """
    try:
        # saving file to s3
        for filename in os.listdir(local_file_path):
            S3.meta.client.upload_file(
                local_file_path+'/'+filename, storage_path, os.path.join('tesseract_output',
                                                                         os.path.basename(local_file_path), filename))
            return (os.path.join('tesseract_output', os.path.basename(local_file_path), filename))
    except Exception as error:
        return error


class TesseractOcrProcessor:
    """
    Tesseract OCR pipeline for images pdf tif jpeg zip file read.
    Attributes:
    1. config (dict): a dictionary of storage type and storage path.
    Methods:
    process_image:
        method for processing the images of type jpg, jpeg, tif, png.
    process_pdf:
        method for processing the pdf files.
    process_zip:
        method for processing the zip files.
    extract_text_from_image:
        method for extracting text from the image, create JSON file of ocr
        result and upload the output file in s3 or save the file in the local system
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
        In this function, we will extract data from the image objects.
        Then we will process the data to store the output in JSON and text format.
        Args:
            image (object): image object from process pdf or image function
            file_name (str): name of the input file
            index (int): index no of the image object
        """
        try:
            # removing extension from input file name for output file initial name
            file_name = os.path.basename(file_name)
            output_filename = os.path.splitext(file_name)[0]
            # processing image using Tessaract Ocr
            get_txt = pytesseract.image_to_string(
                image, output_type=Output.DICT)
            process_image = pytesseract.image_to_data(
                image, output_type=Output.DICT)
            temp_path = OUTPUT_PATH+output_filename
            if not os.path.exists(temp_path):
                os.makedirs(OUTPUT_PATH+output_filename)
            file_path = temp_path+'/' + output_filename+'_'+str(index)
            # writing output text to text file
            with open(file_path + '.txt', 'w') as f:
                f.write(get_txt['text'])
            # writing output json to json file
            with open(file_path + '.json', 'w') as f:
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
                path = file_path+'.jpg'
                image.save(path)
            if self.config.get('storage_type').lower() == 'local':
                shutil.copytree(temp_path, os.path.join(
                    self.config.get('storage_path'), output_filename), symlinks=False, ignore=None,
                    ignore_dangling_symlinks=False, dirs_exist_ok=True)
            elif self.config.get('storage_type').lower() == 'aws':
                upload_file_to_s3(temp_path, self.config.get('storage_path'))
        except Exception as error:
            return error

    def process_image(self, input_file):
        """
        In this function, we will take an image from the user
        and read that image using the open function of the Image module.
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
        In this function, we will take a pdf file from the user
        and iterate over each page of the pdf using the convert_from_path function
        and store them in the images module.
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

        In this function, we will take the zip file from the user and validate the zip
        file. After that, the zip file will be iterated using namelist function and
        saved to /tmp/ of the local device.
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
        self.config = config

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
            text_list = [i[1]+'\n' for i in result]
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
            reader = easyocr.Reader(['hi', 'en'], gpu=False)
            path = os.path.basename(path)
            # get file name
            file_name = os.path.splitext(path)[0]
            # get folder path
            folder_path = OUTPUT_PATH+file_name
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
            if self.config.get('storage_type').lower() == 'aws':
                # upload file into s3
                upload_file_to_s3(folder_path, self.config.get('storage_path'))
            elif self.config.get('storage_type').lower() == 'local':
                shutil.copytree(folder_path, os.path.join(self.config.get('storage_path'), file_name),
                                symlinks=False, ignore=None, ignore_dangling_symlinks=False, dirs_exist_ok=True)
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
                    zip_file.extract(file, OUTPUT_PATH)
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LIST:
                        self.process_image(OUTPUT_PATH+file)
                    elif extension == '.pdf':
                        self.process_pdf(OUTPUT_PATH+file)
                    else:
                        print("Invalid Extension")
                        return "Invalid Extension"
        except Exception as error:
            print(error)
            return error
