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






def image_read(file_name='',type='pdf'):
    directory = 'folder'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            # breakpoint()
            reader = easyocr.Reader(['hi','en']) # this needs to run only once to load the model into memory
            if f.lower().endswith(('.tif')):
                tif_file = cv2.imread(f) #in case of tif
                result = reader.readtext(tif_file,width_ths=0)
            else:
                result = reader.readtext(f,width_ths=0)
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
            # img=cv2.imread(f)
            # for i,item in enumerate(result):
            #     top_left=result[i][0][0]
            #     for j,items in enumerate(item):
            #         bottom_right=result[j][0][2]
            #     text=result[i][1]
            #     font=result[i][0][0]
            #     font=cv2.FONT_HERSHEY_SIMPLEX
            #     img=cv2.rectangle(img,top_left,bottom_right,(0,255,0),5)
            #     # img=cv2.putText(img,text,top_left,font,.5,(255,255,255),cv2.LINE_AA)
            #     cv2.putText(img, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, .9, (36,25,122), 7)
            #     plt.imshow(img)
            #     if (i==len(result)-2):
            #         break
            # plt.show()
            # if f.split('/')[1].startswith('<PIL.'):
            # breakpoint()
            # if f.split("/")[1].startswith('itispdf'):
            breakpoint()
            matches = re.findall(r'itspdf.+?.pdf',f.split('/')[1])

            if os.path.exists('log/'+f.split('/')[1]):
                with open("log/"+f.split('/')[1]+".json", "a") as outfile:
                    json.dump(dictionary, outfile)


            else:
                with open("log/"+f.split('/')[1]+".json", "w") as outfile:
                    json.dump(dictionary, outfile)



folder = os.listdir('file_folder/')
for file_name in folder:
    # file_name = "Resume.zip"
    if file_name.lower().endswith(('.zip')):
        with ZipFile('file_folder/'+file_name, 'r') as zip:
            zip.printdir()
            zip.extractall(path='folder')
    elif file_name.lower().endswith(('.pdf')):
        images=convert_from_path("file_folder/"+file_name)
        for index,image in enumerate(images):
            filename = str(image) + ".jpg" 
            image.save('folder/itispdf'+file_name+'('+str(index)+').jpg')
        # image_read(file_name=file_name,type='pdf')ss
    elif file_name.lower().endswith(('.jpg','jpeg','tif','png')):
        shutil.copy('file_folder/'+file_name, 'folder')
image_read()



# folder = os.listdir('file_folder/')
# for file_name in folder:
#     # file_name = "Resume.zip"
#     if file_name.lower().endswith(('.pdf')):
#         images=convert_from_path("file_folder/"+file_name)
#         for index,image in enumerate(images):
#             filename = str(image) + ".jpg" 
#             image.save('folder/'+file_name+'('+str(index)+').jpg')
#     directory = 'folder'
#     for filename in os.listdir(directory):
#         f = os.path.join(directory, filename)
#         if os.path.isfile(f):
#             # breakpoint()
#             reader = easyocr.Reader(['hi','en']) # this needs to run only once to load the model into memory
#             if f.lower().endswith(('.tif')):
#                 tif_file = cv2.imread(f) #in case of tif
#                 result = reader.readtext(tif_file,width_ths=0)
#             else:
#                 result = reader.readtext(f,width_ths=0)
#             def convert_rec(x):
#                 if isinstance(x, list):
#                     return list(map(convert_rec, x))
#                 else:
#                     return int(x)
#             dictionary={}       
#             for i,item in enumerate(result):
#                 top_left=convert_rec(result[i][0])
#                 dictionary[result[i][1]] = {}
#                 dictionary[result[i][1]]["top"]=convert_rec(result[i][0][0])
#                 dictionary[result[i][1]]["left"]=convert_rec(result[i][0][1])
#                 dictionary[result[i][1]]["right"]=convert_rec(result[i][0][2])
#                 dictionary[result[i][1]]["bottom"]=convert_rec(result[i][0][3])
#             if os.path.exists('log/'+file_name+'.json'):
#                 with open("log/"+file_name+".json", "a") as outfile:
#                     json.dump(dictionary, outfile)
#             else:
#                 with open("log/"+file_name+".json", "w") as outfile:
#                     json.dump(dictionary, outfile)












































    # dictionary[result[i][1]] = top_left
    # breakpoint()
# dictionary["coddrdinates"]=convert_rec(dictionary["coddrdinates"])
# for i in dictionary["coddrdinates"]:
#     dictionary[result[i][1]]=[result[i][0]]
# breakpoint()
#     # for j,items in enumerate(item):
#     #     bottom_right=result[j][0][2]
# # breakpoint()
# # dictionary = {
# #     "name": "sathiyajith",
# #     "rollno": 56,
# #     "cgpa": 8.6,
# #     "phonenumber": "9976770500"
# # }






# import easyocr
# reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
# result = reader.readtext('im.jpeg')
# print(result)
# def convert_rec(x):
#     if isinstance(x, list):
#         return list(map(convert_rec, x))
#     else:
#         return int(x)
# dictionary={'coddrdinates':[]}
# for i,item in enumerate(result):
#     top_left=[result[i][0]]
#     dictionary["coddrdinates"] += top_left
# dictionary["coddrdinates"]=convert_rec(dictionary["coddrdinates"])
# # for i in dictionary["coddrdinates"]:
# #     dictionary[result[i][1]]=[result[i][0]]
# # breakpoint()
# #     # for j,items in enumerate(item):
# #     #     bottom_right=result[j][0][2]
# # # breakpoint()
# # # dictionary = {
# # #     "name": "sathiyajith",
# # #     "rollno": 56,
# # #     "cgpa": 8.6,
# # #     "phonenumber": "9976770500"
# # # }
 
# with open("sample.json", "w") as outfile:
#     json.dump(dictionary, outfile)