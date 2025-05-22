import torch
from torchvision import transforms
from sklearn.preprocessing import StandardScaler
import timm
import hdbscan
import numpy as np
from typing import List


MIN_CLUSTER_LENGTH = 10


# Инициализация модели для извлечения признаков
model = timm.create_model("vit_base_patch16_224.dino", pretrained=True, num_classes=0)
model.eval()


# Функция для извлечения признаков из изображения
def extract_features(img_array: np.ndarray) -> np.ndarray:
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    img = transform(img_array).unsqueeze(0)
    with torch.no_grad():
        features = model(img)
    return features.squeeze().numpy().flatten()


# Функция для кластеризации массива изображений
def cluster_images(features: np.ndarray) -> List[int]:
    # Нормализация данных
    scaler = StandardScaler()
    feature_vectors = scaler.fit_transform(features)

    # Кластеризация с HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=MIN_CLUSTER_LENGTH, min_samples=MIN_CLUSTER_LENGTH, cluster_selection_method='eom')
    labels = clusterer.fit_predict(feature_vectors)

    return labels.tolist()
