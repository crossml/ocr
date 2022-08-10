# Optical Character Recognition for images, Pdfs, zip files, tif files.

What you can expect from this repository:

- Efficient ways to get textual information from your documents like images, pdfs, zip files.

## Quick Tour

Get text from documents and save result in json.

## Installation

Developer mode

```
git clone 'repo link'
```

## Getting your pretrained model

```
from main import EasyOcrProcessor
config={'storage_type':'','storage_path:''}
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

## Documentation:

The full package documentation is available here.

First of all you have to create dict of storage_type and storage_path.

1. storage_type: storage type is type of storage where user wants to store the output result. It may be local or aws.

2. storage_path: storage path is path where user wants to store the output result.

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
![Result json](result.png)