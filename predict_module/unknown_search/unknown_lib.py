import fitz
import numpy as np
import cv2
from typing import List

from predict_module.unknown_search.pdf_operations import convert_pdf_to_image_by_dpi, remove_text_and_annotations_from_pdf
from predict_module.unknown_search.boxes import Box, BoxFloat
from predict_module.unknown_search.image_operations import grayscale_image, thresh_binary_image, remove_all_lines_from_image, dilate_image, draw_boxes, \
    erode_image, crop_images, find_text_boxes, show_image
from predict_module.unknown_search.unknown_search_config import config


class DebugImages:
    initial_image = None
    image_no_text = None
    image_no_lines = None
    preprocessed_image = None


def find_global_boxes(preprocessed_image: np.ndarray) -> List[Box]:
    contours, _ = cv2.findContours(
        preprocessed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if config.contour_min_width < w and config.contour_min_height < h and w * h < config.contour_max_area:
            boxes.append(Box(int(x + w / 2), int(y + h / 2), w, h))

    return boxes


def merge_boxes(boxes: List[Box], threshold: float) -> List[Box]:
    merged = []
    remaining_boxes = set(boxes)

    while remaining_boxes:
        box = remaining_boxes.pop()
        merged_boxes = {box}

        while True:
            new_boxes = {b for b in remaining_boxes if any(b.adjacent_to(mb, threshold) for mb in merged_boxes)}
            if not new_boxes:
                break
            merged_boxes.update(new_boxes)
            remaining_boxes -= new_boxes

        x1 = min(b.x - b.w / 2 for b in merged_boxes)
        y1 = min(b.y - b.h / 2 for b in merged_boxes)
        x2 = max(b.x + b.w / 2 for b in merged_boxes)
        y2 = max(b.y + b.h / 2 for b in merged_boxes)
        merged_box = Box(int((x1 + x2) / 2), int((y1 + y2) / 2), int(x2 - x1), int(y2 - y1))
        merged.append(merged_box)

    return merged


def merge_boxes_full(boxes: List[Box], threshold: float) -> List[Box]:
    while True:
        merged_boxes = merge_boxes(boxes, threshold)
        if len(merged_boxes) == len(boxes):
            break
        boxes = merged_boxes

    return merged_boxes


def correct_boxes(image_no_lines: np.ndarray, boxes: List[Box]) -> List[Box]:
    correct_boxes = []

    for box in boxes:
        x, y, w, h = box.x, box.y, box.w, box.h

        x1, x2 = int(y - h / 2), int(y + h / 2)
        y1, y2 = int(x - w / 2), int(x + w / 2)

        local_image = image_no_lines[x1:x2, y1:y2]

        contours, _ = cv2.findContours(255 - local_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            correct_boxes.append(Box(x, y, w, h))
            continue

        # Определяем минимальную коробку для всех контуров внутри текущего box
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for contour in contours:
            local_x, local_y, local_w, local_h = cv2.boundingRect(contour)
            # Преобразуем координаты из локальных (внутри local_image) в глобальные
            gx, gy = y1 + local_x, x1 + local_y
            min_x = min(min_x, gx)
            min_y = min(min_y, gy)
            max_x = max(max_x, gx + local_w)
            max_y = max(max_y, gy + local_h)

        new_box = Box(
            x=(min_x + max_x) / 2,
            y=(min_y + max_y) / 2,
            w=max_x - min_x,
            h=max_y - min_y
        )
        correct_boxes.append(new_box)

    return correct_boxes


def box_can_be_component(box: Box) -> bool:
    return (config.component_min_width < box.w < config.component_max_width
            and config.component_min_height < box.h < config.component_max_height
            and config.component_min_area < box.w * box.h < config.component_max_area
            and box.w * config.component_max_side_multiplier > box.h
            and box.h * config.component_max_side_multiplier > box.w)


def find_unknown_boxes(preprocessed_image: np.ndarray, image_no_lines: np.ndarray) -> List[Box]:
    global_boxes = find_global_boxes(preprocessed_image)
    #show_image(draw_boxes(DebugImages.preprocessed_image, global_boxes, show_text=True))

    merged_global_boxes = merge_boxes_full(global_boxes, 0)
    merged_global_boxes = merge_boxes_full(merged_global_boxes, config.max_threshold_to_merge_boxes)
    #show_image(draw_boxes(DebugImages.preprocessed_image, merged_global_boxes, show_text=True))

    corrected_boxes = correct_boxes(image_no_lines, merged_global_boxes)
    #show_image(draw_boxes(DebugImages.initial_image, corrected_boxes, show_text=True))

    component_boxes = [box for box in corrected_boxes if box_can_be_component(box)]
    #show_image(draw_boxes(DebugImages.initial_image, component_boxes, show_text=True))

    final_boxes = [box.increase(config.box_increase_coef) for box in component_boxes]
    return final_boxes


def get_unknown_boxes(image: np.ndarray,
                      recognized_boxes: List[Box]) -> List[Box]:
    image_gray = grayscale_image(image)
    #show_image(image_gray)

    image_binary = thresh_binary_image(image_gray)
    #show_image(image_binary)

    image_no_lines = remove_all_lines_from_image(image_binary)
    image_no_lines = draw_boxes(image_no_lines, recognized_boxes, color=(255, 255, 255), fill=True)
    DebugImages.image_no_lines = cv2.cvtColor(image_no_lines, cv2.COLOR_GRAY2RGB)
    #show_image(image_no_lines)

    #image_dilate = dilate_image(image_no_lines, dilate_kernel_size, dilate_iterations)
    #show_image(image_dilate)

    image_erode = erode_image(image_no_lines)
    DebugImages.preprocessed_image = cv2.cvtColor(image_erode, cv2.COLOR_GRAY2RGB)
    #show_image(image_erode)

    unknown_boxes = find_unknown_boxes(preprocessed_image=image_erode, image_no_lines=image_no_lines)
    return unknown_boxes


def get_unknown_components(initial_image:np.ndarray,
                           image: np.ndarray,
                           recognized_boxes: List[Box]) -> List[np.ndarray]:
    unknown_boxes = get_unknown_boxes(image=image,
                                      recognized_boxes=recognized_boxes)
    unknown_components = crop_images(image=initial_image, boxes=unknown_boxes)
    return unknown_components


def get_unknown_boxes_from_pdf(pdf_doc: fitz.Document,
                               recognized_boxes: List[BoxFloat]) -> (List[BoxFloat], List[np.ndarray]):
    initial_image = convert_pdf_to_image_by_dpi(pdf_doc)
    DebugImages.initial_image = initial_image
    #show_image(initial_image)

    pdf_doc = remove_text_and_annotations_from_pdf(pdf_doc)
    image = convert_pdf_to_image_by_dpi(pdf_doc)
    #show_image(image)
    text_boxes = find_text_boxes(image)
    image_no_text = draw_boxes(image, text_boxes, color=(255, 255, 255), fill=True)
    DebugImages.image_no_text = image_no_text

    image_height, image_width = image_no_text.shape[:2]
    recognized_boxes = [box_float.to_box(image_width, image_height) for box_float in recognized_boxes]

    unknown_boxes = get_unknown_boxes(image=image_no_text,
                                      recognized_boxes=recognized_boxes)

    #show_image(draw_boxes(DebugImages.initial_image, unknown_boxes, show_text=True))
    return [box.to_box_float(image_width, image_height) for box in unknown_boxes]


def get_unknown_boxes_from_image(image: np.ndarray,
                                 recognized_boxes: List[BoxFloat]) -> (List[BoxFloat], List[np.ndarray]):
    initial_image = image.copy()
    DebugImages.initial_image = initial_image

    image = image.copy()
    text_boxes = find_text_boxes(image)
    image_no_text = draw_boxes(image, text_boxes, color=(255, 255, 255), fill=True)
    DebugImages.image_no_text = image_no_text

    image_height, image_width = image_no_text.shape[:2]
    recognized_boxes = [box_float.to_box(image_width, image_height) for box_float in recognized_boxes]

    unknown_boxes = get_unknown_boxes(image=image_no_text,
                                      recognized_boxes=recognized_boxes)

    #show_image(draw_boxes(DebugImages.initial_image, unknown_boxes, show_text=True))
    return [box.to_box_float(image_width, image_height) for box in unknown_boxes]


def crop_boxes_from_pdf(pdf_doc: fitz.Document, boxes: List[BoxFloat]) -> List[np.ndarray]:
    image = convert_pdf_to_image_by_dpi(pdf_doc)
    image_height, image_width = image.shape[:2]
    result = crop_images(image=image, boxes=[box.to_box(image_width, image_height) for box in boxes])
    return result


def crop_boxes_from_image(image: np.ndarray, boxes: List[BoxFloat]) -> List[np.ndarray]:
    image_height, image_width = image.shape[:2]
    result = crop_images(image=image, boxes=[box.to_box(image_width, image_height) for box in boxes])
    return result
