# PdfQRSplit

*PdfQRSplit* is a small utility to split a multi-page PDF document into separate PDF files based on pages containing a specified barcode. This concept is known as "separator page" and used in combination with high volume document scanners to scan a large number of unrelated documents in bulk.

While named "*QR*" this tool will also work with most other barcode types.

## Installation and requirements

Python 3 or newer is required. You also need **zxing** (Barcode recognition), **pypdf4** (PDF handling) and **pillow** (image handling) - all of them can be installed using pip:

```
pip install zxing pypdf4 pillow
```

## Usage
```
usage: PdfQRSplit.py [-h] [-p PREFIX] [-s SEPARATOR] [-k] [--keep-page-next] [-b BRIGHTNESS] [-v] [-d] inputfile

Split PDF-file into separate files based on a separator barcode

positional arguments:
  inputfile             Filename or glob to process

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        Prefix for generated PDF files. Default: split
  -s SEPARATOR, --separator SEPARATOR
                        Barcode content used to find separator pages. Default: ADAR-NEXTDOC
  -k, --keep-page       Keep separator page in previous document
  --keep-page-next      Keep separator page in next document
  -b BRIGHTNESS, --brightness BRIGHTNESS
                        brightness threshold for barcode preparation (0-255). Default: 128
  -v, --verbose         Show verbose processing messages
  -d, --debug           Show debug messages
```

### Example

Take the file **input.pdf**, search all pages for barcodes containing the text *"SPLITME"*. If found (or at the end of the input file) previously encountered pages will be written to a separate file, in this case (-k) including the page containing the separator barcode. Since no prefix was given the first file will be named "*split_0_0.pdf*". *split* is the default prefix, 0 indicates it was generated from the first (and in this case only) input file and the second 0 indicates it's the first document extracted from this file.

```python .\test.py .\input.pdf -s "SPLITME" -k -v```

```
Processing file .\input.pdf containing 66 pages
  Analyzing page 1
  Analyzing page 2
  [...]
  Analyzing page 6
    Found separator - writing 6 pages to split_0_0.pdf
  Analyzing page 7
  [...]
  Analyzing page 13
    Found separator - writing 7 pages to split_0_1.pdf
  Analyzing page 14
  [...]
Split 1 given files into 19 files
```

## Thanks

This script is based on ["pdf_split_tool" by Thiago Carvalho D'Ávila (staticdev)](https://github.com/staticdev/pdf-split-tool/).
