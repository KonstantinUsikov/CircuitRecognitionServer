import fitz
from unknown_search.unknown_lib import get_unknown_boxes_from_pdf
from unknown_search.unknown_search_config import UnknownSearchConfig


doc = fitz.open(r"C:\Users\usiko\Desktop\Схемы pdf\01\01_01.pdf")
get_unknown_boxes_from_pdf(doc, [], UnknownSearchConfig())
