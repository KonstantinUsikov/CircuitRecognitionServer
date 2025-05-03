import numpy as np
from PIL import Image
import cv2
import easyocr
from typing import List, Tuple

from predict_module.unknown_search.unknown_search_config import UnknownSearchConfig
from predict_module.unknown_search.boxes import Box


def find_text_boxes(image_np: np.ndarray) -> List[Box]:
    reader = easyocr.Reader(['ru', 'en'])
    results = reader.readtext(image_np)

    boxes = []
    for (bbox, text, confidence) in results:
        p0, p1, p2, p3 = bbox
        x = int((p0[0] + p2[0]) / 2)
        y = int((p0[1] + p2[1]) / 2)
        w = int(max(p0[0], p1[0], p2[0], p3[0]) - min(p0[0], p1[0], p2[0], p3[0]))
        h = int(max(p0[1], p1[1], p2[1], p3[1]) - min(p0[1], p1[1], p2[1], p3[1]))
        boxes.append(Box(x, y, w, h))

    return boxes


def show_image(image: np.ndarray):
    Image.fromarray(image).show()


def draw_boxes(image: np.ndarray, boxes: List[Box], color: Tuple[int, int, int] = (255, 0, 0), thickness: int = 2, fill: bool = False, show_text: bool = False) -> np.ndarray:
    img_copy = image.copy()

    for box in boxes:
        x1, y1 = int(box.x - box.w / 2), int(box.y - box.h / 2)
        x2, y2 = int(box.x + box.w / 2), int(box.y + box.h / 2)

        if fill:
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, -1)
        else:
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)

        if show_text:
            text = f"({box.w}, {box.h})"
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
            text_x = x1 + (x2 - x1 - text_size[0]) // 2
            text_y = y1 - 10
            cv2.putText(img_copy, text, (text_x, text_y), font, 0.5, color, 1, cv2.LINE_AA)

    return img_copy


def crop_images(image: np.ndarray, boxes: List[Box]) -> List[np.ndarray]:
    cropped_images = []

    for box in boxes:
        x1 = int(box.x - box.w / 2)
        y1 = int(box.y - box.h / 2)
        x2 = int(box.x + box.w / 2)
        y2 = int(box.y + box.h / 2)

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.shape[1], x2)
        y2 = min(image.shape[0], y2)

        cropped = image[y1:y2, x1:x2]
        cropped_images.append(cropped)

    return cropped_images


def grayscale_image(image: np.ndarray) -> np.ndarray:
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image_gray


def thresh_binary_image(image: np.ndarray, config: UnknownSearchConfig) -> np.ndarray:
    _, image_binary = cv2.threshold(image, config.thresh_value, 255, cv2.THRESH_BINARY)
    return image_binary


def remove_lines_from_image(image: np.ndarray, config: UnknownSearchConfig) -> np.ndarray:
    negative_image = 255 - image

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (config.line_length, 1))
    horizontal_lines = cv2.morphologyEx(negative_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, config.line_length))
    vertical_lines = cv2.morphologyEx(negative_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    lines = cv2.bitwise_or(horizontal_lines, vertical_lines)
    image_no_lines = cv2.bitwise_or(image, lines)

    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (config.line_repair_kernel_size, config.line_repair_kernel_size))
    image_no_lines = cv2.morphologyEx(image_no_lines, cv2.MORPH_OPEN, repair_kernel, iterations=1)

    return image_no_lines


def remove_lines_from_image_modified(image: np.ndarray, is_horizontal: bool, config: UnknownSearchConfig) -> np.ndarray:

    result = image.copy()
    height, width = result.shape
    dim1, dim2 = (height, width) if is_horizontal else (width, height)

    # Преобразуем изображение в бинарное (True = черный пиксель)
    binary_image = (result == 0)

    for d1 in range(dim1):
        line = binary_image[d1, :] if is_horizontal else binary_image[:, d1]

        # Находим индексы черных пикселей
        black_indices = np.where(line)[0]
        if len(black_indices) == 0:
            continue

        # Находим границы черных сегментов
        gaps = np.diff(black_indices)
        split_indices = np.where(gaps > config.max_line_gap)[0]  # Разрывы больше max_line_gap
        segments = np.split(black_indices, split_indices + 1)

        for segment in segments:
            if len(segment) >= config.min_line_length:
                if is_horizontal:
                    result[d1, segment] = 255
                else:
                    result[segment, d1] = 255

    return result


def remove_all_lines_from_image(image: np.ndarray, config: UnknownSearchConfig) -> np.ndarray:
    image_height, image_width = image.shape
    result = image.copy()
    if image_height * image_width < config.max_pixel_count_to_use_remove_lines_modified:
        result = remove_lines_from_image_modified(result, True, config)
        result = remove_lines_from_image_modified(result, False, config)
    result = remove_lines_from_image(result, config)
    return result


def erode_image(image: np.ndarray, config: UnknownSearchConfig) -> np.ndarray:
    kernel = np.ones((config.erode_kernel_size, config.erode_kernel_size), np.uint8)
    image_erode = cv2.erode(image, kernel, iterations=config.erode_iterations)
    return image_erode


def dilate_image(image: np.ndarray, config: UnknownSearchConfig) -> np.ndarray:
    kernel = np.ones((config.dilate_kernel_size, config.dilate_kernel_size), np.uint8)
    image_dilate = cv2.dilate(image, kernel, iterations=config.dilate_iterations)
    return image_dilate
