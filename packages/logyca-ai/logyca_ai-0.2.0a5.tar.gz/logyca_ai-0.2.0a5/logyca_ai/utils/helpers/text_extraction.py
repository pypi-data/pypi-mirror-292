from enum import StrEnum
from PIL import Image # Pillow
import fitz  # PyMuPDF
import os
import pytesseract

class OCREngine(StrEnum):
    WINDOWS_PATH_01     = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    WINDOWS_PATH_02     = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    LINUX_PATH_01       = "/usr/bin/tesseract"
    LINUX_PATH_02       = "/usr/local/bin/tesseract"
    
    @classmethod
    def get_binary_path(cls):
        for location in cls:
            if os.path.exists(location):
                return str(location)
        return None

def extract_text_from_pdf_file(filename_full_path:str,advanced_image_recognition:bool=False,ocr_engine_path:str=None,output_temp_dir:str=None):
    """
    Extracts text from a PDF file.

    :param filename_full_path: Full path to the PDF file from which to extract text.
    :type filename_full_path: str
    :param advanced_image_recognition: Indicates whether to perform text recognition on images within the PDF.
                               If True, OCR techniques will be used to extract text from images.
    :type advanced_image_recognition: bool
    :param ocr_engine_path: Path to the OCR executable. If provided, this path will be used instead of the default.
    :type ocr_engine_path: str, optional
    :param output_temp_dir: Temporary directory for storing output files.
                            If not provided, a default tmp temporary directory in the application root folder will be used.
    :type output_temp_dir: str, optional

    :return: Extracted text from the PDF file.
    :rtype: str

    :raises FileNotFoundError: If the specified PDF file is not found.
    :raises ValueError: If the OCR path is invalid.

    :example:

    # Example usage
    ```python
    text = extract_text_from_pdf_file('/tmp/example.pdf', advanced_image_recognition=True, ocr_engine_path='/usr/local/bin/tesseract', output_temp_dir='/tmp/tesseract_output')
    ```

    """

    if advanced_image_recognition:
        if ocr_engine_path is None:
            pytesseract.pytesseract.tesseract_cmd=OCREngine.get_binary_path()
        else:
            pytesseract.pytesseract.tesseract_cmd=ocr_engine_path

    doc = fitz.open(filename_full_path)

    text = ""
    if output_temp_dir is None:
        output_temp_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),"tmp"))
    if not os.path.exists(output_temp_dir):
        os.makedirs(output_temp_dir)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        text += page.get_text()
        if advanced_image_recognition:
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                image_path = os.path.join(output_temp_dir, f"image_{page_num+1}_{img_index+1}.png")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                image = Image.open(image_path)
                ocr_text = pytesseract.image_to_string(image)
                text += ocr_text

                os.remove(image_path)

    doc.close()
    return text