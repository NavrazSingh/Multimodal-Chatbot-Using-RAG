import pytesseract
import cv2
from PIL import Image
import logging

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = logging.getLogger(__name__)

class ImageCaptioningService:

    def __init__(self):
        pass

    def get_caption(self, image_path: str) -> str:
        try:
            img = cv2.imread(image_path)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

            text = pytesseract.image_to_string(gray, config="--psm 6")

            print("OCR TEXT:", text)

            return text

        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return ""