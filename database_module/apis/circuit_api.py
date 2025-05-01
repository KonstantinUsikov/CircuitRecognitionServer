from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
import traceback
import base64
from typing import List

from database_module.repositories.circuit_repository import get_circuits_by_image, delete_circuits, get_all_circuits


router = APIRouter()


class GetCircuitsResponse(BaseModel):
    class Circuit(BaseModel):
        circuit_id: int
        circuit_image: str
    circuits: List[Circuit]

@router.get("/api/db/get_circuits", response_model=GetCircuitsResponse)
async def get_circuits():
    try:
        all_circuits = get_all_circuits()
        circuits = []
        for circuit in all_circuits:
            circuits.append(GetCircuitsResponse.Circuit(circuit_id=circuit.id,
                                                        circuit_image=base64.b64encode(circuit.image).decode('utf-8')))

        return GetCircuitsResponse(circuits=circuits)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetCircuitsByImageRequest(BaseModel):
    circuit_image: str

class GetCircuitsByImageResponse(BaseModel):
    circuit_ids: List[int]
    circuit_image: str

@router.post("/api/db/get_circuits_by_image", response_model=GetCircuitsByImageResponse)
async def circuit_exists(request: GetCircuitsByImageRequest):
    try:
        circuit_image_bytes = base64.b64decode(request.circuit_image)
        circuits = get_circuits_by_image(image_bytes=circuit_image_bytes)

        circuit_ids = []
        for circuit in circuits:
            circuit_ids.append(circuit.id)

        return GetCircuitsByImageResponse(circuit_ids=circuit_ids, circuit_image=request.circuit_image)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class DeleteCircuitsByImageRequest(BaseModel):
    circuit_image: str

class DeleteCircuitsByImageResponse(BaseModel):
    count: int

@router.post("/api/db/delete_circuits_by_image", response_model=DeleteCircuitsByImageResponse)
async def circuit_exists(request: GetCircuitsByImageRequest):
    try:
        circuit_image_bytes = base64.b64decode(request.circuit_image)
        circuits = get_circuits_by_image(image_bytes=circuit_image_bytes)

        circuit_ids = []
        for circuit in circuits:
            circuit_ids.append(circuit.id)

        count = delete_circuits(circuit_ids=circuit_ids)

        return DeleteCircuitsByImageResponse(count=count)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
