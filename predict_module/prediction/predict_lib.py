import tensorflow as tf
import cv2
import numpy as np
import os
from typing import List, Tuple


image_size = 64
class_names = ["Unknown", "ACB_1", "ACB_2", "KM_1", "SW", "SW_2", "ACB_MO1", "ACB_PC1"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "Models", "best_8_876.h5")
model = tf.keras.models.load_model(model_path)


def preprocess_image(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    image = image.astype(np.float32) / 255.0
    image = image.reshape(1, image_size, image_size, 1)
    return image


def predict_classes(images: List[np.ndarray], batch_size: int = 512) -> Tuple[List[str], List[float]]:
    if not images:
        return [], []

    class_results = []
    confidence_scores = []
    for i in range(0, len(images), batch_size):
        batch_imgs = images[i:i + batch_size]
        preprocessed = [preprocess_image(img) for img in batch_imgs]
        batch = np.vstack(preprocessed)
        preds = model.predict(batch)
        for pred in preds:
            class_idx = np.argmax(pred)
            class_results.append(class_names[class_idx])
            confidence_scores.append(float(pred[class_idx]))

    return class_results, confidence_scores


def predict_labels(images: List[np.ndarray], batch_size: int = 512) -> Tuple[List[int], List[float]]:
    if not images:
        return [], []

    label_results = []
    confidence_scores = []
    for i in range(0, len(images), batch_size):
        batch_imgs = images[i:i + batch_size]
        preprocessed = [preprocess_image(img) for img in batch_imgs]
        batch = np.vstack(preprocessed)
        preds = model.predict(batch)
        for pred in preds:
            class_idx = int(np.argmax(pred))
            label_results.append(class_idx)
            confidence_scores.append(float(pred[class_idx]))

    return label_results, confidence_scores
