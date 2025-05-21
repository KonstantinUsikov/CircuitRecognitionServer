import hashlib
from typing import List, Optional
import cv2
import numpy as np

from database_module.database.tables.circuit import Circuit
from database_module.database.views.circuit_view import CircuitView


def resize_image(image_bytes: bytes, max_size: int = 2000) -> bytes:
    # Декодирование байтов изображения в numpy-массив
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # Поддерживает альфа-канал

    if img is None:
        raise ValueError("Не удалось декодировать изображение")

    # Получаем текущие размеры
    height, width = img.shape[:2]

    # Вычисляем масштаб (по большей стороне)
    scale = max_size / max(width, height)
    new_width = int(round(width * scale))
    new_height = int(round(height * scale))

    # Ресайз с сохранением пропорций (уменьшение или увеличение)
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

    # Кодируем в PNG (без потерь)
    success, encoded_img = cv2.imencode('.png', resized_img)
    if not success:
        raise ValueError("Ошибка при кодировании изображения")

    return encoded_img.tobytes()



def create_circuit(image: bytes) -> int:
    resized_image = resize_image(image)
    circuit = Circuit.create(image=image, resized_image=resized_image)
    return circuit.id

def get_circuit_by_id(circuit_id: int) -> Optional[CircuitView]:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        return circuit.to_user()
    return None

def get_all_circuits() -> List[CircuitView]:
    return [circuit.to_user() for circuit in Circuit.select()]

def get_circuits_by_image(image_bytes: bytes) -> List[CircuitView]:
    circuit_image_hash = get_image_hash(image_bytes)
    all_circuits = get_all_circuits()
    circuits = []
    for circuit in all_circuits:
        if get_image_hash(circuit.image) == circuit_image_hash:
            circuits.append(circuit)
    return circuits

def update_circuit(circuit_id: int, image: Optional[bytes] = None) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        if image is not None:
            circuit.circuit_data = image
        circuit.save()
        return True
    return False

def delete_circuit(circuit_id: int) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        circuit.delete_instance()
        return True
    return False

def delete_circuits(circuit_ids: List[int]) -> int:
    deleted_count = Circuit.delete().where(Circuit.id.in_(circuit_ids)).execute()
    return deleted_count

def get_image_hash(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()
