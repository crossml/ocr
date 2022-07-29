import json
"""
easyocr pipline
"""
import json
import os
from re import T
from zipfile import ZipFile
import shutil
from cv2 import boundingRect
import easyocr
import cv2
from pdf2image import convert_from_path
from PIL import Image
EXTENSION_LIST = ['.png', '.jpg', '.jpeg']

import boto3
SESSION = boto3.Session()
S3 = SESSION.resource('s3')

S3_JSON_SESSION = boto3.client('s3')
# function to create json output and store in json file


def upload_file_to_s3(local_file_path, json_path):
    """
    Upload File to s3
    """
    try:
        # saving file to s3
        S3.meta.client.upload_file(
            local_file_path, 'input-adaptor', json_path+'.'+local_file_path.split('/')[-1].split('.')[-1])
    except Exception as error:
        return error

# function to create json output and store in json file


class Easyocrpipleline:
    """
    Easy ocr pipeline
    """

    def create_json(self, result, file, file_pdf='', file_zip=''):
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
        for i, item in enumerate(result):
            dictionary[result[i][1]] = {}
            dictionary[result[i][1]]["top"] = convert_rec(result[i][0][0])
            dictionary[result[i][1]]["left"] = convert_rec(result[i][0][1])
            dictionary[result[i][1]]["right"] = convert_rec(result[i][0][2])
            dictionary[result[i][1]]["bottom"] = convert_rec(result[i][0][3])
            dictionary[result[i][1]]["score"] = result[i][2]
        json_name = file.split('/')[-1].split('.')[0]
        file_pdf_name = file_pdf.split('/')[-1].split('.')[0]
        file_zip_name = file_zip.split('/')[-1].split('.')[0]
        pdf_dir_path = '/main_folder/'+file_pdf_name
        zip_dir_path = '/main_folder/'+file_zip_name
        print('file=',file)
        print('file_pdf=',file_pdf)
        print('zip_dir_path=',zip_dir_path)
        print('json_name=',json_name)

        def file_create(zip_dir_path, json_name):
            if not os.path.exists(zip_dir_path):
                os.makedirs(zip_dir_path)
            shutil.copy(file, zip_dir_path)
            json_path = os.path.join(zip_dir_path, json_name)
            upload_file_to_s3(file, json_path)
            print('json_path=',json_path)

            with open(json_path+".json", "w") as outfile:
                S3_JSON_SESSION.put_object(
                    Body=json.dumps(dictionary),
                    Bucket='input-adaptor',
                    Key=json_path+'.json'
                )
                json.dump(dictionary, outfile)
        if file_zip != '':
            if file_pdf_name != '':
                zip_pdf_dir_path = os.path.join(
                    zip_dir_path, file_pdf_name, json_name)
                file_create(zip_pdf_dir_path, json_name)
            else:
                zip_dir_path = os.path.join(zip_dir_path, json_name)
                file_create(zip_dir_path, json_name)
        elif file_pdf != '':
            pdf_dir_path = os.path.join(pdf_dir_path, json_name)
            file_create(pdf_dir_path, json_name)
        else:
            main_path = os.path.join('/main_folder/', json_name)
            file_create(main_path, json_name)

    def image_process(self, path, file_pdf='', file_zip=''):
        """
        image process method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        reader = easyocr.Reader(['hi', 'en'])
        result = reader.readtext(path, width_ths=0)
        self.create_json(result, path, file_pdf, file_zip)

    def tif_image_process(self, path, file_zip=''):
        """
        Tif image process

        Args:
             path (string): file path
            reader (object): easy ocr object
        """
        file_pdf = path
        img = Image.open(path)
        reader = easyocr.Reader(['hi', 'en'])
        tif_file_name = path.split('.tif')[0]
        for i in range(img.n_frames):
            if img.n_frames == 1:
                tif_file = cv2.imread(path)
                tif_file_path = path
            else:
                img.seek(i)
                tif_file_path = os.path.join('/folder/'+tif_file_name+'('+str(i)+').tif')
                img.save(tif_file_path)
            tif_file = cv2.imread(tif_file_path)
            result = reader.readtext(tif_file, width_ths=0)
            self.create_json(result, tif_file_path, file_pdf, file_zip)

    def pdf_process(self, path, file_zip=''):
        """
        PDF processing

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        file_pdf = path
        images = convert_from_path(path)
        file_name = path.split('/')[-1]
        file_name = file_name.split('.')[0]
        print(file_name,'+++')
        print(path)
        for index, image in enumerate(images):
            path = '/folder/'+file_name+'('+str(index)+').jpg'
            print(path,'path')
            image.save(path)
            self.image_process(path, file_pdf, file_zip)




    def zip_process(self, path):
        """
        zip processing method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        file_zip = path
        with ZipFile(path, 'r') as zip_file:
            # read each file of zip one by one
            for file in zip_file.namelist():
                zip_file.extract(file, "")
                extension = os.path.splitext(file)[-1].lower()
                if extension in EXTENSION_LIST:
                    self.image_process(file, file_zip=file_zip)
                elif extension == '.tif':
                    self.tif_image_process(file, file_zip)
                elif extension == '.pdf':
                    self.pdf_process(file, file_zip)


def detectextention(path):
    """
    Function to check file extension and get text from the image

    Args:
        path (string): file name
    """
    process = Easyocrpipleline()  # create object of Easyocrpipleline class
    if os.path.isfile(path):  # check file extension
        if path.lower().endswith(('jpg', 'jpeg', 'png')):
            process.image_process(path)
        elif path.lower().endswith(('tif')):
            process.tif_image_process(path)
        if path.lower().endswith(('pdf')):
            process.pdf_process(path)
        if path.lower().endswith(('.zip')):
            process.zip_process(path)


 # call detectextention function




def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    PATH = 'Yakul.png'  # file path
    process = Easyocrpipleline()
    process.image_process(PATH)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
