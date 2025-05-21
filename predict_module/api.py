import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
import traceback
import httpx
import numpy as np
import fitz
import cv2
import base64
from io import BytesIO
from typing import List

from predict_module.unknown_search.unknown_search_config import UnknownSearchConfig
from settings import backend_hosts
from predict_module.unknown_search.pdf_operations import convert_pdf_to_image_by_pixel_count
from predict_module.unknown_search.unknown_lib import get_unknown_boxes_from_pdf, get_unknown_boxes_from_image, \
    crop_boxes_from_pdf, crop_boxes_from_image
from predict_module.prediction.predict_lib import predict_classes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    class ConfigModel(BaseModel):
        thresh_value: int = 250
        line_length: int = 35
        min_line_length: int = 150
        max_line_gap: int = 100
        line_repair_kernel_size: int = 7
        dilate_kernel_size: int = 3
        dilate_iterations: int = 1
        erode_kernel_size: int = 7
        erode_iterations: int = 1
        component_min_area: int = 1300
        component_min_width: int = 25
        component_min_height: int = 25
        component_max_area: int = 10000
        component_max_width: int = 500
        component_max_height: int = 500
        component_max_side_multiplier: float = 3.5
        contour_min_width: int = 10
        contour_min_height: int = 10
        contour_max_area: int = 350000
        max_pixel_count_to_use_remove_lines_modified: int = 500000000
        min_multiplier_to_count_as_component_part: float = 10
        max_threshold_to_merge_boxes: float = 0.5
        box_increase_factor: float = 0.1
    circuit_data: str
    config: ConfigModel

class PredictResponse(BaseModel):
    class RecognizedComponent(BaseModel):
        id: int
        x: float
        y: float
        w: float
        h: float
        image: str
        class_name: str
        confidence: float
    class UnknownComponent(BaseModel):
        id: int
        x: float
        y: float
        w: float
        h: float
        image: str
    circuit_id: int
    circuit_image: str
    recognized_components: List[RecognizedComponent]
    unknown_components: List[UnknownComponent]

@app.post("/api/predict/run_prediction", response_model=PredictResponse, responses={500: {"description": "str"}})
async def run_prediction(request: PredictRequest):
    try:
        circuit_header, circuit_base64_data = request.circuit_data.split(",", 1)
        if "application/pdf" in circuit_header:
            pdf_data = base64.b64decode(circuit_base64_data)
            pdf_bytes = BytesIO(pdf_data)
            circuit_pdf = fitz.Document(stream=pdf_bytes, filetype="pdf")
            circuit_image = convert_pdf_to_image_by_pixel_count(circuit_pdf, 0, 10_000_000)
        else:
            image_data = base64.b64decode(circuit_base64_data)
            image_bytes = BytesIO(image_data)
            circuit_image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        _, buffer = cv2.imencode(".jpg", circuit_image)
        circuit_image_to_add = base64.b64encode(buffer).decode("utf-8")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{backend_hosts.database_url}/api/db/delete_circuits_by_image", json={"circuit_image": circuit_image_to_add})
            response.raise_for_status()
            delete_circuits_by_image_result = response.json()

        search_config = UnknownSearchConfig(**request.config.dict())
        if "application/pdf" in circuit_header:
            component_boxes = get_unknown_boxes_from_pdf(circuit_pdf, [], search_config)
            component_images = crop_boxes_from_pdf(circuit_pdf, component_boxes)
            component_classes, confidence_scores = predict_classes(component_images)
        else:
            component_boxes = get_unknown_boxes_from_image(circuit_image, [], search_config)
            component_images = crop_boxes_from_image(circuit_image, component_boxes)
            component_classes, confidence_scores = predict_classes(component_images)

        recognized_components_to_add = []
        unknown_components_to_add = []
        for box, image, class_name, confidence in zip(component_boxes, component_images, component_classes, confidence_scores):
            _, buffer = cv2.imencode(".jpg", image)
            image_base64 = base64.b64encode(buffer).decode("utf-8")
            if class_name.lower() == "unknown":
                unknown_components_to_add.append({
                    "x": box.x,
                    "y": box.y,
                    "w": box.w,
                    "h": box.h,
                    "image": image_base64,
                })
            else:
                recognized_components_to_add.append({
                    "x": box.x,
                    "y": box.y,
                    "w": box.w,
                    "h": box.h,
                    "image": image_base64,
                    "class_name": class_name,
                    "confidence": confidence
                })

        add_components_json = {
            "circuit_image": circuit_image_to_add,
            "recognized_components": recognized_components_to_add,
            "unknown_components": unknown_components_to_add,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{backend_hosts.database_url}/api/db/add_circuit_and_components", json=add_components_json)
            response.raise_for_status()
            add_components_result = response.json()

        circuit_id = add_components_result["circuit_id"]
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_hosts.database_url}/api/db/get_components_by_circuit_id",
                                        params={"circuit_id": circuit_id})
            response.raise_for_status()
            get_components_result = response.json()
        return PredictResponse(**get_components_result)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=backend_hosts.predict_host, port=backend_hosts.predict_port)
