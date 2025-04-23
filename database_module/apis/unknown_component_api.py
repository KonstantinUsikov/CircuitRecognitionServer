import base64
import traceback
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from database_module.repositories import unknown_component_repository
from base64 import b64encode
from fastapi import APIRouter

router = APIRouter()


class UnknownComponentView(BaseModel):
    id: int
    circuit_id: int
    cluster_id: int | None = None
    x: float
    y: float
    w: float
    h: float
    image: str
    features: List[float]

@router.get("/api/db/unknown_components", response_model=List[UnknownComponentView], responses={500: {"description": "Internal Server Error"}})
async def get_all_unknown_components():
    try:
        components = unknown_component_repository.get_all_unknown_components()
        result = [
            UnknownComponentView(
                id=component.id,
                circuit_id=component.circuit_id,
                cluster_id=component.cluster_id,
                x=component.x,
                y=component.y,
                w=component.w,
                h=component.h,
                image=b64encode(component.image).decode('utf-8'),
                features=component.features,
            )
            for component in components
        ]
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class UpdateUnknownComponentRequest(BaseModel):
    id: int
    circuit_id: int | None = None
    cluster_id: int | None = None
    x: float | None = None
    y: float | None = None
    w: float | None = None
    h: float | None = None
    image: str | None = None
    features: List[float]

class UpdateUnknownComponentResponse(BaseModel):
    success: bool

@router.put("/api/db/unknown_component", response_model=UpdateUnknownComponentResponse, responses={500: {"description": "Internal Server Error"}})
async def update_unknown_component(update_data: UpdateUnknownComponentRequest):
    try:
        image_data = base64.b64decode(update_data.image) if update_data.image else None
        success = unknown_component_repository.update_unknown_component(
            component_id=update_data.id,
            circuit_id=update_data.circuit_id,
            cluster_id=update_data.cluster_id,
            x=update_data.x,
            y=update_data.y,
            w=update_data.w,
            h=update_data.h,
            image=image_data,
            features=update_data.features)
        return {"success": success}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class UpdateUnknownComponentsRequest(BaseModel):
    id: int
    circuit_id: int | None = None
    cluster_id: int | None = None
    x: float | None = None
    y: float | None = None
    w: float | None = None
    h: float | None = None
    image: str | None = None
    features: List[float]

class UpdateUnknownComponentsResponse(BaseModel):
    success: bool

@router.put("/api/db/unknown_components", response_model=UpdateUnknownComponentResponse, responses={500: {"description": "Internal Server Error"}})
async def update_multiple_unknown_components(update_datas: List[UpdateUnknownComponentRequest]):
    try:
        for update_data in update_datas:
            image_data = base64.b64decode(update_data.image) if update_data.image else None
            success = unknown_component_repository.update_unknown_component(
                component_id=update_data.id,
                circuit_id=update_data.circuit_id,
                cluster_id=update_data.cluster_id,
                x=update_data.x,
                y=update_data.y,
                w=update_data.w,
                h=update_data.h,
                image=image_data,
                features=update_data.features)
        return {"success": success}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
