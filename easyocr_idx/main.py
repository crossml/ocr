"""
easyocr pipline
"""
from curses import beep
import json
import os
from zipfile import ZipFile
import shutil
import easyocr
import cv2
from pdf2image import convert_from_path
import boto3
from PIL import Image


EXTENSION_LIST = ['.png', '.jpg', '.jpeg']

SESSION = boto3.Session()
S3 = SESSION.resource('s3')
S3_JSON_SESSION = boto3.client('s3')


def upload_file_to_s3(json_path):
    """
    Upload File to s3
    """
    try:
        for file in os.listdir(json_path):
            S3.meta.client.upload_file(
                json_path+'/'+file, 'input-adaptor', json_path+'/'+file)
    except Exception as error:
        print ("An error occurred in upload file to s3")
        return error


def download_directory(bucketname, remotedirectoryname):
    """
    download the s3 folder

    Args:
        bucketname (_type_): bucket name
        remotedirectoryname (_type_): directory path
    """
    try:
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucketname)
        for obj in bucket.objects.filter(Prefix=remotedirectoryname):
            if not os.path.exists(os.path.dirname(obj.key)):
                os.makedirs(os.path.dirname(obj.key))
            bucket.download_file(obj.key, obj.key)
    except Exception as error:
        print ("An error occurred in download folder")
        return error


class Easyocrpipleline:
    """
    Easy ocr pipeline
    """
    main_folder = 'main_folder/'
    folder_path = 'folder/'

    def file_create(self, zip_dir_path, json_name, file, dictionary):
        """
        To create a file

        Args:
            zip_dir_path (_type_): zip path
            json_name (_type_): json file name
            file (_type_): file path in zip
            dictionary (_type_): json to write in file
        """
        if not os.path.exists(zip_dir_path):
            os.makedirs(zip_dir_path)
        shutil.copy(file, zip_dir_path)
        json_path = os.path.join(zip_dir_path, json_name)
        with open(json_path+".json", "w") as outfile:
            json.dump(dictionary, outfile)

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
        pdf_dir_path = os.path.join(self.main_folder, file_pdf_name)
        if file_zip != '':
            if file_pdf_name != '':
                zip_pdf_dir_path = os.path.join(self.main_folder, file_pdf_name)
                self.file_create(zip_pdf_dir_path, json_name, file, dictionary)
            else:
                zip_dir_path = os.path.join(self.main_folder, json_name)
                self.file_create(zip_dir_path, json_name, file, dictionary)
        elif file_pdf != '':
            self.file_create(pdf_dir_path, json_name, file, dictionary)
        else:
            zip_pdf_dir_path = os.path.join(self.main_folder, json_name)
            self.file_create(zip_pdf_dir_path, json_name, file, dictionary)

    def image_process(self, path, file_pdf='', file_zip=''):
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
            self.create_json(result, path, file_pdf, file_zip)
            if file_pdf=='':
                main_path=os.path.join(self.main_folder,path.split('.')[0])
                upload_file_to_s3(main_path)
            # upload folder into s3
        except Exception as error:
            print ("An error occurred in image process")
            return error

    def tif_image_process(self, path, file_zip=''):
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
            tif_file_name = path.split('.tif')[0]
            # iterate the each page of tif
            for i in range(img.n_frames):
                if img.n_frames == 1:
                    tif_file = cv2.imread(path)
                    tif_file_path = path
                else:
                    img.seek(i)
                    tif_file_path = os.path.join(
                        self.folder_path+tif_file_name+'('+str(i)+').tif')
                    # save each page of image
                    img.save(tif_file_path)
                tif_file = cv2.imread(tif_file_path)
                # read the image data
                result = reader.readtext(tif_file, width_ths=0)
                # function to create json
                self.create_json(result, tif_file_path, file_pdf, file_zip)
            main_path=os.path.join(self.main_folder,path.split('.')[0])
            # upload folder into s3
            upload_file_to_s3(main_path)
        except Exception as error:
            print ("An error occurred in tif process")
            return error

    def pdf_process(self, path, file_zip=''):
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
            file_name = path.split('/')[-1].split('.')[0]
            # iterate the each page of pdf
            for index, image in enumerate(images):
                path = self.folder_path+file_name+'('+str(index)+').jpg'
                # save each page of image
                image.save(path)
                # read each page of pdf
                self.image_process(path, file_pdf, file_zip)
            main_path=os.path.join(self.main_folder,file_name)
            # upload folder into s3
            upload_file_to_s3(main_path)
        except Exception as error:
            print ("An error occurred in pdf process")
            return error

    def zip_process(self, path):
        """
        zip processing method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            file_zip = path
            # read the zip file
            with ZipFile(path, 'r') as zip_file:
                for file in zip_file.namelist():
                    zip_file.extract(file, "")
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LIST:
                        self.image_process(file, file_zip=file_zip)
                    elif extension == '.tif':
                        self.tif_image_process(file, file_zip)
                    elif extension == '.pdf':
                        self.pdf_process(file, file_zip)
        except Exception as error:
            print ("An error occurred in zip process")
            return error



# download_directory('input-adaptor','main_folder/1')
# PATH = 'Resume.pdf'
# PATH = 'ICA_101_555090004.tif'
PATH = 't2.zip'
# PATH = '@#@$#$^#$%.png'
process = Easyocrpipleline()
# process.tif_image_process(PATH)
process.zip_process(PATH)
# process.image_process(PATH)
# process.pdf_process(PATH)
