from curses import beep
import json
# from lib2to3.pytree import convert
import easyocr
import cv2
from matplotlib import pyplot as plt
import os
from zipfile import ZipFile
from pdf2image import convert_from_path  
import shutil, os
import re
import urllib.request


EXTENSION_LIST = ('.pdf', '.png', '.jpg', '.tif', '.jpeg')
# function to create json output and store in json file
def create_json(result,file):
    def convert_rec(x):
        if isinstance(x, list):
            return list(map(convert_rec, x))
        else:
            return int(x)
    dictionary={}       
    for i,item in enumerate(result):
        top_left=convert_rec(result[i][0])
        dictionary[result[i][1]] = {}
        dictionary[result[i][1]]["top"]=convert_rec(result[i][0][0])
        dictionary[result[i][1]]["left"]=convert_rec(result[i][0][1])
        dictionary[result[i][1]]["right"]=convert_rec(result[i][0][2])
        dictionary[result[i][1]]["bottom"]=convert_rec(result[i][0][3])
        dictionary[result[i][1]]["score"]=result[i][2]
        print(dictionary)
    json_name=(file.split('/')[1]).rsplit('.', 1)[0]
    with open("log/"+json_name+".json", "w") as outfile:
        json.dump(dictionary, outfile)



def image_read():
    directory = 'folder'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            reader = easyocr.Reader(['hi','en']) # this needs to run only once to load the model into memory
            if f.lower().endswith(('.tif')):
                tif_file = cv2.imread(f) #in case of tif
                result = reader.readtext(tif_file,width_ths=0)
            else:
                result = reader.readtext(f,width_ths=0)
            
            create_json(result,f)


def pdf_to_image(images,file_name):
    file_name=file_name.split('/')[-1]
    file_name=file_name.split('.')[0]
    for index,image in enumerate(images):
        filename = str(image) + ".jpg" 
        image.save('folder/'+file_name+'('+str(index)+').jpg')



# code to download image form given link
# opener=urllib.request.build_opener()
# opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
# urllib.request.install_opener(opener)
# filename = 'sunshine_dog.jpg'
# path='https://cdn.pixabay.com/photo/2018/04/26/16/39/beach-3352363_960_720.jpg'
# filename=path.split('/')[-1]
# dir = 'folder/'
# for file in os.scandir(dir):
#     os.remove(file.path)
# urllib.request.urlretrieve(path, 'folder/'+filename)
# path='folder/'+filename
# path='file_folder/'
# path='test.zip'
path='folder/33.png'
# path='file_folder/pdfzip.zip'
# path='Resume.pdf'
folder = os.listdir('file_folder/')
# loop for if folder is given in input
if os.path.isdir(path):
    ext=all(file.lower().endswith(EXTENSION_LIST) for file in folder)
    if ext:
        for file_name in folder:
            if file_name.lower().endswith(('.pdf')):
                images=convert_from_path("file_folder/"+file_name)
                pdf_to_image(images,file_name)
            elif file_name.lower().endswith(('.jpg','jpeg','tif','png')):
                shutil.copy('file_folder/'+file_name, 'folder')
        image_read()
    else:
        print("invalid file extension")
elif os.path.isfile(path):
    # loop for file in input
    if path.lower().endswith(('jpg','jpeg','png','tif')):
        reader = easyocr.Reader(['hi','en'])
        result = reader.readtext(path,width_ths=0)
        print(result)
        create_json(result,path)
    elif path.lower().endswith(('pdf')):
        images=convert_from_path(path)
        file_name=(path).rsplit('.', 1)[0]
        pdf_to_image(images,file_name)
        image_read() 
    elif path.lower().endswith(('.zip')):
        with ZipFile(path, 'r') as zip:
            zip.printdir()
            zip.extractall(path='folder')
        folder = os.listdir('folder/')
        for file_name in folder:
            if file_name.lower().endswith(('.pdf')):
                images=convert_from_path("folder/"+file_name)
                pdf_to_image(images,file_name)
                os.remove('folder/'+file_name)
        image_read()
    else:
        print("wrong extension")
