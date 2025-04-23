import base64
from io import BytesIO
import cv2
import fitz
import httpx
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException
import settings
from predict_module.predict_lib import predict_classes
from predict_module.unknown_search.lib_unknown import get_unknown_boxes_from_pdf, get_unknown_boxes_from_image
from predict_module.unknown_search.pdf_operations import convert_pdf_to_image_by_dpi, \
    convert_pdf_to_image_by_pixel_count
from predict_module.unknown_search.unknown_search_config import UnknownSearchConfig

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class predict_entity_input(BaseModel):
    image: str

class predict_entity_output(BaseModel):
    class box(BaseModel):
        id: int
        majorClass: str
        minorDescription: str
        confidence: float
        detectedText: str
        connection: int | str
        article: str
        x: float
        y: float
        w: float
        h: float
    boxes: List[box]
    class rp_shp(BaseModel):
        cls: str
        score: float
        x: float
        y: float
        w: float
        h: float
    unknowns: List[rp_shp]


@app.post("/api/predict/predict", response_model=predict_entity_output, responses={500: {"description": "str"}})
async def predict(input_model:predict_entity_input):
    try:
        is_pdf = input_model.image.split(",")[0].__contains__("application/pdf")

        if is_pdf:
            pdf_str = input_model.image
            base64str = pdf_str.split(",")[1]

            # Decode the base64 string to binary data
            image_data = base64.b64decode(base64str)

            # Create a BytesIO object from the binary data
            pdf_bytes = BytesIO(image_data)
            doc = fitz.Document(stream=pdf_bytes, filetype="pdf")
            image = convert_pdf_to_image_by_dpi(doc)
        else:
            image_str = input_model.image
            base64str = image_str.split(",")[1]

            # Decode the base64 string to binary data
            image_data = base64.b64decode(base64str)

            # Create a BytesIO object from the binary data
            image_bytes = BytesIO(image_data)

            image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        if is_pdf:
            pdf_str = input_model.image
            base64str = pdf_str.split(",")[1]

            # Decode the base64 string to binary data
            image_data = base64.b64decode(base64str)

            # Create a BytesIO object from the binary data
            pdf_bytes = BytesIO(image_data)
            doc = fitz.Document(stream=pdf_bytes, filetype="pdf")
            unknowns_pred, images = get_unknown_boxes_from_pdf(doc, [], UnknownSearchConfig())
        else:
            unknowns_pred, images = get_unknown_boxes_from_image(image, [], UnknownSearchConfig())

        classes = predict_classes(images)
        unknowns = []
        for u, cls in zip(unknowns_pred, classes):
            unknowns.append(predict_entity_output.rp_shp(cls=cls, score=0, x=u.x,y=u.y,w=u.w,h=u.h))
        result = {"boxes": [], "unknowns": unknowns}

        if is_pdf:
            pdf_str = input_model.image
            base64str = pdf_str.split(",")[1]

            # Decode the base64 string to binary data
            image_data = base64.b64decode(base64str)

            # Create a BytesIO object from the binary data
            pdf_bytes = BytesIO(image_data)
            doc = fitz.Document(stream=pdf_bytes, filetype="pdf")
            image = convert_pdf_to_image_by_pixel_count(doc)
        else:
            image_str = input_model.image
            base64str = image_str.split(",")[1]

            # Decode the base64 string to binary data
            image_data = base64.b64decode(base64str)

            # Create a BytesIO object from the binary data
            image_bytes = BytesIO(image_data)

            image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        shapes = []
        for shape in unknowns:
            shapes.append({
                "cls": "-",
                "score":0,
                "x": shape.x * image.shape[1],
                "y": shape.y * image.shape[0],
                "w": shape.w * image.shape[1],
                "h": shape.h * image.shape[0]
            })

        _, img_str = cv2.imencode(".jpg", image)
        httpx.post(
            f"{settings.Backends.report}/api/report/report", json={
                "clean": base64.b64encode(img_str).decode("utf-8"),
                "shapes": shapes
            }, timeout=999)

        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)