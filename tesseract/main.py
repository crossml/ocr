from cgitb import text
from tempfile import TemporaryDirectory
from typing import Dict
import cv2
from cv2 import line
import pytesseract
import json

# lst=[]
# img = cv2.imread('1.png')
# custom_config = r'--oem 3 --psm 6'
# text= pytesseract.image_to_data(img, config=custom_config)
# # lst.append(text)
# # print(lst)
# # for b in text.splitlines():
# #   b = b.split(' ')
# # with open('main.txt', 'w') as f:
# #     for l in lst:
# #         f.write(l)
# #         f.write("/n")

# json_string = json.dumps(text)
# print(json_string)
# # text = pytesseract.image_to_boxes(img)
# with open('main1.json', 'w') as f:
#     json.dump(json_string, f)
import os
from pytesseract import Output
from pdf2image import convert_from_path
image_file_list = []
inp_path = "/home/sourav/project/OCR/images"
out_path = "/home/sourav/project/OCR/json_dir"
for imageName in os.listdir(inp_path):
    extension = os.path.splitext(imageName)[-1].lower()

    if extension == 'zip':

        with TemporaryDirectory() as tempdir:
            pdf_pages = convert_from_path(imageName, 500)
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
                page.save(filename, "JPEG")
                image_file_list.append(filename)
        with open(out_path+'/' + output_filename+'.json', 'w') as f:
            for image_file in image_file_list:
                d = {os.path.basename(file_name): [{'Confidence Score': conf, 'Text': text, 'Line no.': line_no, 'Top': top, 'Left': left, }
                                                   for conf, text, line_no, top, left in zip(d['conf'], d['text'], d['line_num'], d['top'], d['left'])]}
            json.dump(d, f, indent=4)

    else:

        file_name = imageName
        output_filename = os.path.splitext(file_name)[0]
        print(imageName)
        img = cv2.imread(inp_path+'/'+file_name)

        d = pytesseract.image_to_data(img, output_type=Output.DICT)

        # print(d['conf'])
        # print(d['text'])
        # print(d['line_num'])
        print(d.keys())
        # z=zip(d['conf'],d['text'],d['line_num'])
        with open(out_path+'/' + output_filename+'.json', 'w') as f:
            # for text in d['text']:
            #     for lineno in d['line_num']:
            # pass
            d = {os.path.basename(file_name): [{'Confidence Score': conf, 'Text': text, 'Line no.': line_no, 'Top': top, 'Left': left, }
                                               for conf, text, line_no, top, left in zip(d['conf'], d['text'], d['line_num'], d['top'], d['left'])]}
            json.dump(d, f, indent=4)

            # json.dump({'text': text, 'line no': lineno},f,indent=4)
            # f.write(json.dumps({'text': text, 'line no': lineno}))

        # print(d.keys())
