"""
easyocr pipline
"""
import os
import boto3
from config import EXTENSION_LIST, S3_BUCKET_NAME
from DataAdaptor import InputAdaptor
from DocExtractor import Easyocrpipleline

SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def downloaddirectoryfroms3(remotedirectoryname):
    """
    Download file from s3

    Args:
        remotedirectoryname (string): s3 directory path
    """
    try:
        # for managing S3 in an AWS Partition
        bucket = S3.Bucket(S3_BUCKET_NAME)
        for obj in bucket.objects.filter(Prefix=remotedirectoryname):
            # give folder exists or not
            if not os.path.exists(os.path.dirname(obj.key)):
                # make folder if folder does not exists
                os.makedirs(os.path.dirname(obj.key))
            # download file from s3
            bucket.download_file(obj.key, obj.key)
    except Exception as error:
        return error


def detectextention(path):
    """
    Function to check file extension and get text from the image

    Args:
        path (string): file name
    """
    try:
        # create object of Easyocrpipleline class
        process = Easyocrpipleline()
        if os.path.isfile(path):
            # check file extension
            file_type = os.path.splitext(path)[-1].lower()
            if file_type in EXTENSION_LIST:
                # function call for images process
                process.image_process(path)
            elif file_type == '.pdf':
                # function call for pdf process
                process.pdf_process(path)
            elif file_type == '.zip':
                # function call for zip file process
                process.zip_process(path)
            else:
                return "Invalid file extension"
            
    except Exception as error:
        return error


if __name__ == '__main__':
    # create object of inputadaptor
    inputadaptor = InputAdaptor()
    # function for file upload on S3
    file_path = inputadaptor.zip_upload('', "aws")
    if file_path:
        # function call for download file from s3
        downloaddirectoryfroms3(file_path)
        # function call for text extract from images
        detectextention(file_path)
