import fitz
import numpy as np
from typing import List
import math


def split_pdf(pdf_doc: fitz.Document) -> List[fitz.Document]:
    pages_count = len(pdf_doc)
    pages = []

    for i in range(pages_count):
        new_doc = fitz.open()
        new_doc.insert_pdf(pdf_doc, from_page=i, to_page=i)
        pages.append(new_doc)

    return pages


def remove_text_and_annotations_from_pdf(pdf_doc: fitz.Document) -> fitz.Document:
    for page in pdf_doc:
        word_list = page.get_text("blocks")
        for x0, y0, x1, y1, *_ in word_list:
            page.add_redact_annot(fitz.Rect(x0, y0, x1, y1))
        page.apply_redactions()

        for annot in list(page.annots() or []):
            rect = annot.rect
            page.add_redact_annot(rect)
            page.delete_annot(annot)
        page.apply_redactions()

    return pdf_doc


def convert_pdf_to_image_by_dpi(pdf_doc: fitz.Document, page_index: int = 0, dpi: int = 300) -> np.ndarray:
    page = pdf_doc[page_index]
    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)
    pixmap = page.get_pixmap(matrix=matrix)

    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
    return image


def convert_pdf_to_image_by_pixel_count(pdf_doc: fitz.Document, page_index: int = 0, pixel_count: int = 20_000_000) -> np.ndarray:
    page = pdf_doc[page_index]
    scale = pixel_count / (page.rect.width * page.rect.height)
    matrix = fitz.Matrix(scale, scale)
    pixmap = page.get_pixmap(matrix=matrix)

    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
    return image


def convert_pdf_to_image_by_max_side(pdf_doc: fitz.Document, page_index: int = 0, max_side: int = 2500) -> np.ndarray:
    page = pdf_doc[page_index]
    scale = max_side / max(page.rect.width, page.rect.height)
    matrix = fitz.Matrix(scale, scale)
    pixmap = page.get_pixmap(matrix=matrix)

    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
    return image


def get_pdf_image_size_by_dpi(pdf_doc: fitz.Document, page_index: int = 0, dpi: int = 300):
    page = pdf_doc[page_index]

    width_pt, height_pt = page.rect.width, page.rect.height
    width_px = int(width_pt * dpi / 72)
    height_px = int(height_pt * dpi / 72)

    return height_px, width_px


def get_pdf_image_size_by_pixel_count(pdf_doc: fitz.Document, page_index: int = 0, pixel_count: int = 20_000_000):
    page = pdf_doc[page_index]

    width_pt, height_pt = page.rect.width, page.rect.height
    aspect_ratio = width_pt / height_pt
    height_px = int(round(math.sqrt(pixel_count / aspect_ratio)))
    width_px = int(round(height_px * aspect_ratio))

    return height_px, width_px


def get_pdf_image_size_by_max_side(pdf_doc: fitz.Document, page_index: int = 0, max_side: int = 2500):
    page = pdf_doc[page_index]

    width_pt, height_pt = page.rect.width, page.rect.height
    scale = max_side / max(width_pt, height_pt)
    width_px = int(round(width_pt * scale))
    height_px = int(round(height_pt * scale))

    return height_px, width_px
