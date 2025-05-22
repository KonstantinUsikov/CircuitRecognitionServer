import fitz
from unknown_search.unknown_lib import get_unknown_boxes_from_pdf
from unknown_search.unknown_search_config import UnknownSearchConfig


doc = fitz.open(r"C:\Users\usiko\Desktop\Схемы pdf\01\01_01.pdf")
get_unknown_boxes_from_pdf(doc, [], UnknownSearchConfig())

# import asyncio
# import httpx
# import base64
# import time
# import json
# from pathlib import Path
#
# # Адрес FastAPI сервера
# API_URL = "http://localhost:8001/api/predict/run_prediction"
#
# # Пример схемы (загрузи свой PDF или JPG файл и закодируй в base64)
# def load_circuit_base64(path: str) -> str:
#     file_path = Path(path)
#     mime = "application/pdf" if file_path.suffix == ".pdf" else "image/jpeg"
#     with open(file_path, "rb") as f:
#         encoded = base64.b64encode(f.read()).decode("utf-8")
#     return f"data:{mime};base64,{encoded}"
#
# # Тело запроса (можно модифицировать параметры конфигурации)
# def build_request_payload(base64_str: str) -> dict:
#     return {
#         "circuit_data": base64_str,
#         "config": {
#             "thresh_value": 250,
#             "line_length": 35,
#             "min_line_length": 150,
#             "max_line_gap": 100,
#             "line_repair_kernel_size": 7,
#             "dilate_kernel_size": 3,
#             "dilate_iterations": 1,
#             "erode_kernel_size": 7,
#             "erode_iterations": 1,
#             "component_min_area": 1300,
#             "component_min_width": 25,
#             "component_min_height": 25,
#             "component_max_area": 10000,
#             "component_max_width": 500,
#             "component_max_height": 500,
#             "component_max_side_multiplier": 3.5,
#             "contour_min_width": 10,
#             "contour_min_height": 10,
#             "contour_max_area": 350000,
#             "max_pixel_count_to_use_remove_lines_modified": 500000000,
#             "min_multiplier_to_count_as_component_part": 10,
#             "max_threshold_to_merge_boxes": 0.5,
#             "box_increase_factor": 0.1
#         }
#     }
#
# async def send_request(client: httpx.AsyncClient, base64_data: str, request_id: int):
#     payload = build_request_payload(base64_data)
#     start = time.perf_counter()
#     try:
#         response = await client.post(API_URL, json=payload, timeout=120)
#         duration = time.perf_counter() - start
#         print(f"[Request #{request_id}] Status: {response.status_code}, Time: {duration:.2f}s")
#         if response.status_code == 200:
#             json_resp = response.json()
#             print(f"[Request #{request_id}] Circuit ID: {json_resp.get('circuit_id')}, "
#                   f"Recognized: {len(json_resp['recognized_components'])}, "
#                   f"Unknown: {len(json_resp['unknown_components'])}")
#         else:
#             print(f"[Request #{request_id}] Error response: {response.text}")
#     except Exception as e:
#         duration = time.perf_counter() - start
#         print(f"[Request #{request_id}] EXCEPTION after {duration:.2f}s: {str(e)}")
#
# async def run_concurrent_tests():
#     base64_data = load_circuit_base64(r"C:\Users\usiko\Desktop\Схемы pdf\01\01_01.pdf")  # ← Замени на свой файл
#     concurrent_requests = 5  # Кол-во одновременных запросов
#
#     async with httpx.AsyncClient() as client:
#         tasks = [
#             send_request(client, base64_data, i + 1)
#             for i in range(concurrent_requests)
#         ]
#         await asyncio.gather(*tasks)
#
# if __name__ == "__main__":
#     asyncio.run(run_concurrent_tests())
