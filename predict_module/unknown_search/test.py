import fitz
from predict_module.unknown_search.lib_unknown import get_unknown_boxes_from_pdf
from predict_module.unknown_search.unknown_search_config import UnknownSearchConfig

# image_path = r'C:\Users\usiko\Desktop\Схемы png\01\01_01.png'
# image = cv2.imread(image_path)
# get_unknown_boxes_from_image(image=image, recognized_boxes=[])

doc_path = r'C:\Users\usiko\Desktop\Схемы pdf\01\01_01.pdf'
doc = fitz.open(doc_path)
get_unknown_boxes_from_pdf(pdf_doc=doc, recognized_boxes=[])
