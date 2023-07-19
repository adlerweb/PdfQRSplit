import argparse
import glob
import sys
import io
import PyPDF4
import zxing

from typing import List
from tempfile import TemporaryDirectory
from PIL import Image

parser = argparse.ArgumentParser(description='Split PDF-file into separate files based on a separator barcode')
parser.add_argument('filename', metavar='inputfile', type=str,
                    help='Filename or glob to process')
parser.add_argument('-p', '--prefix', default="split",
                    help='Prefix for generated PDF files. Default: split')
parser.add_argument('-s', '--separator', default="ADAR-NEXTDOC",
                    help='Barcode content used to find separator pages. Default: ADAR-NEXTDOC')
parser.add_argument('-k', '--keep-page', action='store_true',
                    help='Keep separator page in previous document')
parser.add_argument('--keep-page-next', action='store_true',
                    help='Keep separator page in next document')
parser.add_argument('-b', '--brightness', type=int, default=128,
                    help='brightness threshold for barcode preparation (0-255). Default: 128')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Show verbose processing messages')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Show debug messages')

class PdfQrSplit:
    def __init__(self, filepath: str, verbose: bool, debug: bool, brightness: 128) -> None:
        self.filepath = filepath
        self.verbose = verbose
        self.debug = debug
        self.brightness = brightness
        self.input_pdf = PyPDF4.PdfFileReader(filepath, "rb")
        self.total_pages = self.input_pdf.getNumPages()
        if verbose:
            print(
                "Processing file {} containing {} pages".format(
                    filepath, self.total_pages
                )
            )

    def split_qr(self, split_text: str, ifiles: int) -> int:
        """Creates new files based on barcode contents.
        Args:
            split_text: Barcode content to recognize a separator page
        Returns:
            int: Number of generated files.
        """
        pdfs_count = 0
        current_page = 0

        reader = zxing.BarCodeReader()
        pdf_writer = PyPDF4.PdfFileWriter()

        while current_page != self.total_pages:

            if self.verbose:
                print("  Analyzing page {}".format((current_page+1)))

            page = self.input_pdf.getPage(current_page)

            xObject = page['/Resources']['/XObject'].getObject()

            with TemporaryDirectory() as temp_dir:
                if self.debug:
                    print("    Writing page images to temporary directory {}".format(temp_dir))

                split = False
                for obj in xObject:
                    tgtn=False
                    if xObject[obj]['/Subtype'] == '/Image':
                        data = xObject[obj].getData()

                        if '/FlateDecode' in xObject[obj]['/Filter']  or \
                            '/DCTDecode' in xObject[obj]['/Filter'] or \
                            '/JPXDecode' in xObject[obj]['/Filter']:
                                tgtn = temp_dir + "/" + obj[1:] + ".png"
                                img = Image.open(io.BytesIO(data))
                                fn = lambda x : 255 if x > self.brightness else 0
                                img = img.convert('L').point(fn, mode='1')
                                img.save(tgtn)
                        elif self.debug:
                            print(f"      Unknown filter type {xObject[obj]['/Filter']}")
                        
                        if tgtn:
                            if self.debug:
                                print("      Wrote image {}; Checking for separator barcode".format(tgtn))
                            barcode = reader.decode(tgtn)
                            if barcode and args.separator in barcode.parsed:
                                if self.debug:
                                    print("        Found separator barcode")
                                split = True

                if split:
                    if args.keep_page:
                        pdf_writer.addPage(page)
                    
                    output = args.prefix + '_' + str(ifiles) + '_' + str(pdfs_count) + '.pdf'
                    if self.verbose:
                        print("    Found separator - writing {} pages to {}".format(pdf_writer.getNumPages(), output))
                    with open(output, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)

                    pdf_writer = PyPDF4.PdfFileWriter()
                    pdfs_count += 1
                    #Due to a bug in PyPDF4 PdfFileReader breaks when invoking PdfFileWriter.write - reopen file
                    self.input_pdf = PyPDF4.PdfFileReader(filepath, "rb")

                    if args.keep_page_next:
                        pdf_writer.addPage(page)
                else:
                    pdf_writer.addPage(page)
            
            current_page += 1

        output = args.prefix + '_' + str(ifiles) + '_' + str(pdfs_count) + '.pdf'
        if self.verbose:
            print("    End of input - writing {} pages to {}".format(pdf_writer.getNumPages(), output))
        with open(output, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        pdfs_count += 1
        
        return pdfs_count

args = parser.parse_args()

if args.debug:
    args.verbose = True

if args.brightness < 0:
    args.brightness = 0
if args.brightness > 255:
    args.brightness = 255

filepaths = glob.glob(args.filename)
if not filepaths:
    sys.exit("Error: no file found, check the documentation for more info.")
    
ofiles = 0
ifiles = 0

for filepath in filepaths:
    splitter = PdfQrSplit(filepath, args.verbose, args.debug, brightness=args.brightness)
    ofiles += splitter.split_qr(args.separator, ifiles)
    ifiles += 1

print(
    "Split {} given files into {} files".format(
        ifiles, ofiles
    )
)
