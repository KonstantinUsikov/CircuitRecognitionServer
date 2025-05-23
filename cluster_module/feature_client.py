import httpx
import numpy as np
import cv2
from io import BytesIO
import base64
import time

from cluster_module import cluster_lib
from settings import backend_hosts


def update_features(limit: int = 10) -> int:
    response_get = httpx.get(
        f"{backend_hosts.database_url}/api/db/get_unknown_components_without_features",
        params={"limit": limit},
        timeout=10.0
    )
    if response_get.status_code != 200:
        return 0

    data_get = response_get.json()
    components = data_get.get("unknown_components", [])
    if not components:
        return 0

    unknown_components_to_update = []
    for comp in components:
        image_bytes = BytesIO(base64.b64decode(comp["image"]))
        image_data = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
        unknown_components_to_update.append({
            "id": comp["id"],
            "features": cluster_lib.extract_features(image_data).tolist()
        })

    payload_update = {"unknown_components": unknown_components_to_update}
    response_update = httpx.put(
        f"{backend_hosts.database_url}/api/db/update_unknown_components_features",
        json=payload_update,
        timeout=10.0
    )
    if response_update.status_code != 200:
        return 0

    data_update = response_update.json()
    count = data_update.get("count")
    return count


SLEEP_SECONDS = 10
LIMIT = 20
def run_feature_loop():
    while True:
        try:
            start_time = time.time()
            count = update_features(limit=LIMIT)
            elapsed_time = time.time() - start_time
        except Exception as e:
            print(f"Ошибка при подключении: {e}")

        if count != 0:
            print(f"Updated features for {count} components in {elapsed_time:.2f} seconds.")
        else:
            time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    run_feature_loop()