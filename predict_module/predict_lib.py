import tensorflow as tf
import cv2
import numpy as np
from typing import List


IMAGE_SIZE = 64
model_path = r"predict_module\best8_model_20250413_102824.h5"
classes = ["Unknown", "ACB_1", "ACB_2", "KM_1", "SW", "SW_2", "ACB_MO1", "ACB_PC1"]
model = tf.keras.models.load_model(model_path)


def preprocess_image(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    image = image.astype(np.float32) / 255.0
    image = image.reshape(1, IMAGE_SIZE, IMAGE_SIZE, 1)
    return image

def predict_classes(images: List[np.ndarray]) -> List[str]:
    if not images:
        return []
    preprocessed_images = [preprocess_image(img) for img in images]
    batch = np.vstack(preprocessed_images)
    predictions = model.predict(batch)
    result = [classes[np.argmax(pred)] for pred in predictions]
    return result

def predict_labels(images: List[np.ndarray], batch_size: int = 512) -> List[int]:
    if not images:
        return []

    results = []
    for i in range(0, len(images), batch_size):
        batch_imgs = images[i:i + batch_size]
        preprocessed = [preprocess_image(img) for img in batch_imgs]
        batch = np.vstack(preprocessed)
        preds = model.predict(batch)
        results.extend(np.argmax(preds, axis=1))

    return results
