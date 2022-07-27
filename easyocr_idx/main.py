"""
easyocr pipline
"""
import json
import os
from zipfile import ZipFile
import easyocr
import cv2
from pdf2image import convert_from_path
from PIL import Image
from config import EXTENSION_LIST


# function to create json output and store in json file

class Easyocrpipleline:
    """
    Easy ocr pipeline
    """

    def create_json(self, result, file):
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
        # json log file create
        with open("/tmp/"+json_name+".json", "w") as outfile:
            json.dump(dictionary, outfile)

    def image_process(self, path):
        """
        image process method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        reader = easyocr.Reader(['en'])
        result = reader.readtext(path,width_ths=0)
        self.create_json(result, path)

    def tif_image_process(self, path):
        """
        Tif image process

        Args:
             path (string): file path
            reader (object): easy ocr object
        """
        img = Image.open(path)  
        reader = easyocr.Reader(['en'])
        tif_file_name=path.split('.tif')[0]
        for i in range(img.n_frames):
            if img.n_frames==1:
                tif_file = cv2.imread(path)
                tif_file_path=path
            else:
                img.seek(i)
                tif_file_path=('folder/'+tif_file_name+'(%s).tif'%(i,))
                img.save(tif_file_path)
            tif_file = cv2.imread(tif_file_path)  # in case of tif
            result = reader.readtext(tif_file, width_ths=0)
            self.create_json(result, tif_file_path)

    def pdf_process(self, path):
        """
        PDF processing

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        images = convert_from_path(path)
        file_name = path.split('/')[-1]
        file_name = file_name.split('.')[0]
        for index, image in enumerate(images):
            path = 'folder/'+file_name+'('+str(index)+').jpg'
            image.save(path)
            self.image_process(path)

    def zip_process(self, path):
        """
        zip processing method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        with ZipFile(path, 'r') as zip_file:
            # read each file of zip one by one
            for file in zip_file.namelist():
                zip_file.extract(file, "")
                extension = os.path.splitext(file)[-1].lower()
                if extension in EXTENSION_LIST:
                    self.image_process(file)
                elif extension == '.tif':
                    self.tif_image_process(file)
                elif extension == '.pdf':
                    self.pdf_process(file)


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


PATH = 'ICA_101_555090004.tif'  # file path
detectextention(PATH)  # call detectextention function
