import cv2
import fitz
import numpy as np

from predict_module.unknown_search.unknown_lib import get_unknown_boxes_from_pdf, get_unknown_boxes_from_image
from predict_module.unknown_search.unknown_search_config import UnknownSearchConfig


# image_path = "C:/Users/usiko/Desktop/Схемы png/01/01_01.png"
# image_data = np.fromfile(image_path, dtype=np.uint8)
# image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
# get_unknown_boxes_from_image(image=image, recognized_boxes=[])

doc_path = "C:/Users/usiko/Desktop/Схемы pdf/01/01_01.pdf"
doc = fitz.open(doc_path)
get_unknown_boxes_from_pdf(pdf_doc=doc, recognized_boxes=[])
