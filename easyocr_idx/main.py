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
from config import EXTENSION_LIST, BUCKET_NAME, TEMP
from PIL import Image, ImageSequence


SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(json_path):
    """
    Upload File to s3
    """
    try:
        for file in os.listdir(json_path):
            s3_json_path = os.path.join(json_path, file)
            print('json_path', json_path)
            S3.meta.client.upload_file(
                s3_json_path, BUCKET_NAME, s3_json_path)
    except Exception as error:
        return error


class Easyocrpipleline:
    """
    Easy ocr pipeline
    """

    def create_json(self, result, file):
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
        # get json file path
        json_name = os.path.splitext(file)[0]
        # create json log file
        with open(json_name+".json", "w") as outfile:
            json.dump(dictionary, outfile)

    def image_read(self, path, images):
        """
        Read the image and give text

        Args:
            path (string): _description_
            images (object): _description_
        """
        try:
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
                    file_path = file_name+'('+str(index)+').jpg'
                else:
                    file_path = path
                file_path = os.path.join(folder_path, file_path)
                # save image
                img.save(file_path)
                reader = easyocr.Reader(['hi', 'en'])
                # read the image data
                result = reader.readtext(file_path, width_ths=0)
                # function to create json
                self.create_json(result, file_path)
            # upload file into s3
            upload_file_to_s3(folder_path)
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
            # read the image
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
            # convert the pdf into images
            images = convert_from_path(path)
            # read the image
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
                    zip_file.extract(file, TEMP)
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LIST:
                        self.image_process(TEMP+file)
                    elif extension == '.pdf':
                        self.pdf_process(TEMP+file)
                    else:
                        return "Invalid Extension"
        except Exception as error:
            return error
