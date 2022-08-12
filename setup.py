
"""
setup file for python package
"""
import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="python_ocr",
    version="0.1.5",
    author="Crossml",
    author_email="amar@crossml.com",
    packages=setuptools.find_packages(),
    description="Input Adaptor to verify file extension",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords=['ocr', 'tesseract', 'easyocr','imgaeprocessing'],
    python_requires='>=3',
    install_requires=['pytesseract', 'pdf2image', 'boto3','easyocr',]
)

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
