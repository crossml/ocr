"""
easyocr pipline
"""
import json
import os
from zipfile import ZipFile
import shutil
import easyocr
import cv2
from pdf2image import convert_from_path
import boto3
from PIL import Image
from config import EXTENSION_LIST


SESSION = boto3.Session()
S3 = SESSION.resource('s3')
S3_JSON_SESSION = boto3.client('s3')
BUCKET_NAME='input-adaptor'
TEMP='/tmp/'


def upload_file_to_s3(json_path):
    """
    Upload File to s3
    """
    try:
        json_path=os.path.join(TEMP,os.path.basename(json_path))
        for file in os.listdir(json_path):
            S3.meta.client.upload_file(
                json_path+'/'+file, BUCKET_NAME, json_path+'/'+file)
    except Exception as error:
        return error


class Easyocrpipleline:
    """
    Easy ocr pipeline
    """
    main_folder = '/tmp/'
    def file_create(self, dir_path, json_name, file, dictionary):
        """
        To create a file

        Args:
            dir_path (string): directory path
            json_name (string): json file name
            file (string): file path in zip
            dictionary (dictionary): json to write in file
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        shutil.copy(file, dir_path)
        json_path = os.path.join(dir_path, json_name)
        with open(json_path+".json", "w") as outfile:
            json.dump(dictionary, outfile)


    def create_json(self, result, file, file_pdf=''):
        """
        json file save
        """
        def convert_rec(input_dict):
            """
            input input dict integer
            """
            if isinstance(input_dict, list):
                return list(map(convert_rec, input_dict))
            else:
                return int(input_dict)
        dictionary = {}
        # create proper json to store in json file
        dictionary = [{'left':int(i[0][0][0]), \
            'top':int(i[0][1][1]), \
                'right':int(i[0][2][0]), \
                    'bottom':int(i[0][3][1]), \
                        'text':i[1], \
                            'confidence':i[-1]} for i in result]
        json_name = os.path.splitext(os.path.basename(file))[0]
        file_pdf_name = os.path.splitext(os.path.basename(file_pdf))[0]
        pdf_dir_path = os.path.join(self.main_folder, file_pdf_name)
        if file_pdf != '':
            self.file_create(pdf_dir_path, json_name, file, dictionary)
        else:
            dir_path = os.path.join(self.main_folder, json_name)
            self.file_create(dir_path, json_name, file, dictionary)

    def tif_image_process(self, path):
        """
        Tif image process

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            file_pdf = path
            img = Image.open(path)
            # create object of easy ocr to read from image
            reader = easyocr.Reader(['hi', 'en'])
            # get file name without extension
            tif_file_name = os.path.splitext(path)[0]
            # iterate the each page of tif
            for i in range(img.n_frames):
                if img.n_frames == 1:
                    tif_file = cv2.imread(path)
                    tif_file_path = path
                else:
                    img.seek(i)
                    tif_file_path = os.path.join(
                        self.main_folder+tif_file_name+'('+str(i)+').tif')
                    # save each page of image
                    img.save(tif_file_path)
                tif_file = cv2.imread(tif_file_path)
                # read the image data
                result = reader.readtext(tif_file, width_ths=0)
                # function to create json
                self.create_json(result, tif_file_path, file_pdf)
            main_path = os.path.join(
                self.main_folder, os.path.splitext(os.path.basename(path))[0])
            # upload folder into s3
            upload_file_to_s3(main_path)
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
            file_pdf = path
            images = convert_from_path(path)
            # get the image name without image extension
            file_name = os.path.splitext(os.path.basename(path))[0]
            # iterate the each page of pdf
            for index, image in enumerate(images):
                path = self.main_folder+file_name+'('+str(index)+').jpg'
                # save each page of image
                image.save(path)
                # read each page of pdf
                self.image_process(path, file_pdf)
            main_path = os.path.join(self.main_folder, file_name)
            # upload folder into s3
            upload_file_to_s3(main_path)
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
                    elif extension == '.tif':
                        self.tif_image_process(file)
                    elif extension == '.pdf':
                        self.pdf_process(file)
        except Exception as error:
            return error

    def image_process(self, path, file_pdf=''):
        """
        image process method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            # create object of easy ocr to read from image
            reader = easyocr.Reader(['hi', 'en'])
            # read the image data
            result = reader.readtext(path, width_ths=0)
            # function to create json
            self.create_json(result, path, file_pdf)
            if not file_pdf:
                main_path = os.path.join(
                    self.main_folder, os.path.splitext(path)[0])
                upload_file_to_s3(main_path)
            # upload folder into s3
        except Exception as error:
            return error


