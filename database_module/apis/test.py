import base64
import httpx

BASE_URL = "http://localhost:8000"

def test_get_and_update_unknown_components():
    # 1. Получаем компоненты с пустыми features (лимит 2)
    response_get = httpx.get(
        f"{BASE_URL}/api/db/get_unknown_components_without_features",
        params={"limit": 50},
        timeout=10.0
    )
    print("GET status:", response_get.status_code)
    assert response_get.status_code == 200, f"GET failed: {response_get.text}"

    data_get = response_get.json()
    components = data_get.get("unknown_components", [])
    print(f"Fetched {len(components)} components with empty features")

    if not components:
        print("No components to update")
        return

    # 2. Формируем payload для обновления — например, добавим фиктивные features
    unknown_components_to_update = []
    for comp in components:
        unknown_components_to_update.append({
            "id": comp["id"],
            "features": [0.1, 0.2, 0.9, 0.9]  # или любая логика генерации признаков
        })

    payload_update = {"unknown_components": unknown_components_to_update}

    # 3. Отправляем обновление
    response_update = httpx.put(
        f"{BASE_URL}/api/db/update_unknown_components_features",
        json=payload_update,
        timeout=10.0
    )
    print("PUT status:", response_update.status_code)
    assert response_update.status_code == 200, f"PUT failed: {response_update.text}"

    data_update = response_update.json()
    print("Updated count:", data_update.get("count"))


test_get_and_update_unknown_components()