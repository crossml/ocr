# Optical Character Recognition for images, Pdfs, zip files, tif files.

What you can expect from this repository:

- Efficient ways to get textual information from your documents like images, pdfs, zip files.


## Quick Tour

Get text from documents and save results in JSON.

## Installation

Developer mode

```
pip install python-ocr
```

## For tesseractOcr process 

storage_type='local/aws' #currently only local and aws supported.
local storage_path='Desired path of your OS where you want to store the output' # for local storage.
local storage_path='S3 bucket' # for AWS storage (CASE SENSTIVE).


e.g. for Storing output to AWS
```
config={'storage_type':'AWS','storage_path:'your-bucket-name'}
```

```
from ocr import TesseractOcrProcessor
process=TesseractOcrProcessor(config)
```

## For EasyOcr process 


```
from ocr import EasyOcrProcessor
process=EasyOcrProcessor(config)

```

storage_type: type of storage local or aws.

storage_path: storage path is path where user wants to store the output result.

```
# Path of file
PATH=''

# reading image files
process.process_image(PATH)

# reading pdf files
process.process_pdf(PATH)

# reading zip files
process.process_zip(PATH)
```

# Documentation:

The full package documentation is available here.

First of all, you have to create dict of storage_type and storage_path.

1. storage_type: storage type is type of storage where the user wants to store the output result. It may be local or aws.

2. storage_path: storage path is path where the user wants to store the output result.

    - if you want to store the file in local system than give the path of folder where user wants to store the result as storage_path.

    - if user wants to store the result in aws than in storage_path you have to give the bucket name.

```
config={'storage_type':'','storage_path':''}
```

Now create the object of EasyOcrProcessor which take the config as a object parameter.

```
process = EasyOcrProcessor(config)
```

## Image process:

To read the text from image user have to call the process_image method of EasyOcrProcessor and pass the path of image file as a parameter in it.
process_image method store the output at the storage_path.

```
process.process_image(PATH)
```

## Pdf process:

To read the text from pdf file user have to call the process_pdf method of EasyOcrProcessor and pass the path of pdf file as a parameter in it.
process_pdf method convert each page of pdf into images and create the result of each page and store the result at the storage_path.

```
process.process_pdf(PATH)
```

## Zip process:

To read the text from zip file user have to call the process_zip method of EasyOcrProcessor and pass the path of zip file as a parameter in it.
Zip should contain only files with valid extensions. process_zip method extract each file of zip one by one and save the result at the storage path.

```
process.process_zip(PATH)
```

## Result output:

```
[{
        "left": 125,
        "top": 141,
        "right": 259,
        "bottom": 161,
        "text": "Folin MGA-5875",
        "confidence": 0.3961432168382489
    },
    {
        "left": 1115,
        "top": 140,
        "right": 1272,
        "bottom": 161,
        "text": "OM8 N0 : 2126-0006",
        "confidence": 0.41482855467690777
    },
    {
        "left": 1281,
        "top": 139,
        "right": 1498,
        "bottom": 165,
        "text": "Epiration Datc 12/31/2024",
        "confidence": 0.40780972855935615
}]
```