import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
import hdbscan
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List


MIN_CLUSTER_LENGTH = 10


# Инициализация ResNet50 для извлечения признаков
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model = torch.nn.Sequential(*(list(model.children())[:-1]))  # Убираем последний слой
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

    # Определяем точки, которые НЕ являются шумом (-1)
    mask_valid = labels != -1
    valid_points = feature_vectors[mask_valid]  # Используем нормализованные признаки
    valid_labels = labels[mask_valid]  # Их кластеры

    if len(valid_labels) > 0:
        # Обучаем k-NN
        knn = KNeighborsClassifier(n_neighbors=20, metric='cosine', weights='distance')
        knn.fit(valid_points, valid_labels)

        # Перераспределение шумовых точек
        for i in range(len(labels)):
            if labels[i] == -1:
                probs = knn.predict_proba(feature_vectors[i].reshape(1, -1))
                max_prob = np.max(probs)
                predicted_cluster = knn.predict(feature_vectors[i].reshape(1, -1))[0]

                # Проверяем среднее расстояние до ближайших соседей
                distances, _ = knn.kneighbors(feature_vectors[i].reshape(1, -1))
                mean_distance = np.mean(distances)

                if max_prob > 0.8 and mean_distance < 0.7:
                    labels[i] = predicted_cluster

    return labels.tolist()
