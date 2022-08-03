"""
easyocr pipline
"""
import json
import os
from zipfile import ZipFile
import easyocr
from pdf2image import convert_from_path
import boto3
from PIL import Image
from config import EXTENSION_LIST
from PIL import Image, ImageSequence


SESSION = boto3.Session()
S3 = SESSION.resource('s3')
S3_JSON_SESSION = boto3.client('s3')
BUCKET_NAME = 'input-adaptor'
TEMP = '/tmp/'


def upload_file_to_s3(json_path):
    """
    Upload File to s3
    """
    try:
        json_path = os.path.join(TEMP, os.path.basename(json_path))
        for file in os.listdir(json_path):
            S3.meta.client.upload_file(
                json_path+'/'+file, BUCKET_NAME, json_path+'/'+file)
    except Exception as error:
        return error


class Easyocrpipleline:
    """
    Easy ocr pipeline
    """

    def create_json(self, result, file, file_pdf=''):
        """
        json file save
        """
        dictionary = {}
        # create proper json to store in json file
        dictionary = [{'left': int(i[0][0][0]),
                       'top':int(i[0][1][1]),
                       'right':int(i[0][2][0]),
                       'bottom':int(i[0][3][1]),
                       'text':i[1],
                       'confidence':i[-1]} for i in result]
        json_name = os.path.splitext(os.path.basename(file))[0]
        file_pdf_name = os.path.splitext(os.path.basename(file_pdf))[0]
        dir_path = os.path.join(TEMP, file_pdf_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        json_path = os.path.join(dir_path, json_name)
        with open(json_path+".json", "w") as outfile:
            json.dump(dictionary, outfile)

    def image_read(self, path, images):
        """
        Read the image and give text

        Args:
            path (string): _description_
            images (object): _description_
        """
        try:
            file_pdf = path
            path = os.path.basename(path)
            file_name = os.path.splitext(path)[0]
            if not os.path.exists(TEMP+file_name):
                os.makedirs(TEMP+file_name)
            for index, img in enumerate(images):
                if os.path.splitext(path)[-1] == '.png':
                    file_path = path
                else:
                    file_path = file_name+'('+str(index)+').jpg'
                file_path = os.path.join(TEMP+file_name, file_path)
                img.save(file_path)
                reader = easyocr.Reader(['hi', 'en'])
                # read the image data
                result = reader.readtext(file_path, width_ths=0)
                # function to create json
                self.create_json(result, file_path, file_pdf)
            main_path = os.path.join(TEMP, file_name)
            upload_file_to_s3(main_path)
        except Exception as error:
            return error

    def image_process(self, path):
        """
        Tif image process

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            img = Image.open(path)
            images = ImageSequence.Iterator(img)
            self.image_read(path, images)
        except Exception as error:
            return error

    def pdf_process(self, path):
        """
        PDF processing

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            images = convert_from_path(path)
            self.image_read(path, images)
        except Exception as error:
            return error

    def zip_process(self, path):
        """
        zip processing method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            # read the zip file
            with ZipFile(path, 'r') as zip_file:
                for file in zip_file.namelist():
                    zip_file.extract(file, "")
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LIST:
                        self.image_process(file)
                    elif extension == '.pdf':
                        self.pdf_process(file)
        except Exception as error:
            return error