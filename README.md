# Optical Character Recognition for images, Pdfs, zip files, and tif files.

What you can expect from this repository:

- Efficient ways to get textual information from your documents like images, pdfs, and zip files.

## Quick Tour

Get text from documents and save results in JSON.

## Installation

Developer mode

```
pip install python-ocr
```

## Getting your pretrained model

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

storage_type: type of storage local or aws.

storage_path: storage path is the path where the user wants to store the output result.

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

First of all, you have to create a dict of storage_type and storage_path.

1. storage_type: storage type is a type of storage where the user wants to store the output result. It may be local or aws.

2. storage_path: storage path is the path where the user wants to store the output result.

    - if you want to store the file in the local system then give the path of the folder where you want to store the result as storage_path.

    - if the user wants to store the result in aws then in storage_path you have to give the bucket name.

```
config={'storage_type':'','storage_path':''}
```

Now create the object of TesseractOcrProcessor which take the config as an object parameter.

```
process = TesseractOcrProcessor(config)
```

## Image process:

To read the text from the image user have to call the process_image method of TesseractOcrProcessor and pass the path of the image file as a parameter in it.
process_image method stores the output at the storage_path.

```
process.process_image(PATH)
```

## Pdf process:

To read the text from the pdf file user have to call the process_pdf method of TesseractOcrProcessor and pass the path of the pdf file as a parameter in it.
process_pdf method converts each page of pdf into images and create the result of each page and store the result at the storage_path.

```
process.process_pdf(PATH)
```

## Zip process:

To read the text from the zip file user have to call the process_zip method of TesseractOcrProcessor and pass the path of the zip file as a parameter in it.
Zip should contain only files with valid extensions. process_zip method extracts each file one by one and saves the result at the storage path.

```
process.process_zip(PATH)
```

## Result output:

```
[{
	"left": 138,
	"top": 57,
	"right": 175,
	"bottom": 75,
	"text": "Can",
	"confidence": 95.33
}, {
	"left": 181,
	"top": 57,
	"right": 220,
	"bottom": 75,
	"text": "You",
	"confidence": 95.33
}, {
	"left": 226,
	"top": 56,
	"right": 262,
	"bottom": 75,
	"text": "Tell",
	"confidence": 95.75
}]

```