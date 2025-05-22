from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
import traceback
import base64
from collections import defaultdict
from typing import List, Optional

from database_module.repositories.circuit_repository import create_circuit, get_circuit_by_id, delete_circuit
from database_module.repositories.cluster_repository import get_all_clusters
from database_module.repositories.recognized_component_repository import create_recognized_component, \
    get_recognized_components_by_circuit_id, delete_recognized_components_by_circuit_id, get_all_recognized_components
from database_module.repositories.unknown_component_repository import create_unknown_component, \
    get_unknown_components_by_circuit_id, delete_unknown_components_by_circuit_id, get_all_unknown_components, \
    get_unknown_components_without_features, update_unknown_components_features


router = APIRouter()


class GetRecognizedComponentsResponse(BaseModel):
    class RecognizedComponent(BaseModel):
        id: int
        circuit_id: int
        x: float
        y: float
        w: float
        h: float
        image: str
        class_name: str
        confidence: float
    recognized_components: List[RecognizedComponent]

@router.get("/api/db/get_recognized_components", response_model=GetRecognizedComponentsResponse, responses={500: {"description": "Internal Server Error"}})
async def get_recognized_components():
    try:
        components = get_all_recognized_components()
        recognized_components = []
        for component in components:
            recognized_components.append(GetRecognizedComponentsResponse.RecognizedComponent(id=component.id,
                                                                                             circuit_id=component.circuit_id,
                                                                                             x=component.x,
                                                                                             y=component.y,
                                                                                             w=component.w,
                                                                                             h=component.h,
                                                                                             image=base64.b64encode(component.image).decode('utf-8'),
                                                                                             class_name=component.class_name,
                                                                                             confidence=component.confidence))
        return GetRecognizedComponentsResponse(recognized_components=recognized_components)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetUnknownComponentsResponse(BaseModel):
    class UnknownComponent(BaseModel):
        id: int
        circuit_id: int
        cluster_id: Optional[int]
        x: float
        y: float
        w: float
        h: float
        image: str
        features: List[float]
    unknown_components: List[UnknownComponent]

@router.get("/api/db/get_unknown_components", response_model=GetUnknownComponentsResponse, responses={500: {"description": "Internal Server Error"}})
async def get_unknown_components():
    try:
        components = get_all_unknown_components()
        unknown_components = []
        for component in components:
            unknown_components.append(GetUnknownComponentsResponse.UnknownComponent(id=component.id,
                                                                                    circuit_id=component.circuit_id,
                                                                                    cluster_id=component.cluster_id,
                                                                                    x=component.x,
                                                                                    y=component.y,
                                                                                    w=component.w,
                                                                                    h=component.h,
                                                                                    image=base64.b64encode(component.image).decode('utf-8'),
                                                                                    features=component.features))
        return GetUnknownComponentsResponse(unknown_components=unknown_components)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetUnknownComponentsWithoutFeaturesResponse(BaseModel):
    class UnknownComponent(BaseModel):
        id: int
        circuit_id: int
        cluster_id: Optional[int]
        x: float
        y: float
        w: float
        h: float
        image: str
        features: List[float]
    unknown_components: List[UnknownComponent]

@router.get("/api/db/get_unknown_components_without_features", response_model=GetUnknownComponentsWithoutFeaturesResponse, responses={500: {"description": "Internal Server Error"}})
async def get_unknown_components(limit: Optional[int] = None):
    try:
        components = get_unknown_components_without_features(limit=limit)
        unknown_components = []
        for component in components:
            unknown_components.append(GetUnknownComponentsWithoutFeaturesResponse.UnknownComponent(id=component.id,
                                                                                    circuit_id=component.circuit_id,
                                                                                    cluster_id=component.cluster_id,
                                                                                    x=component.x,
                                                                                    y=component.y,
                                                                                    w=component.w,
                                                                                    h=component.h,
                                                                                    image=base64.b64encode(component.image).decode('utf-8'),
                                                                                    features=component.features))
        return GetUnknownComponentsWithoutFeaturesResponse(unknown_components=unknown_components)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class UpdateFeaturesRequest(BaseModel):
    class UnknownComponent(BaseModel):
        id: int
        features: List[float]
    unknown_components: List[UnknownComponent]

class UpdateFeaturesResponse(BaseModel):
    count: int

@router.put("/api/db/update_unknown_components_features", response_model=UpdateFeaturesResponse, responses={500: {"description": "Internal Server Error"}})
async def get_unknown_components(request: UpdateFeaturesRequest):
    try:
        data_dict = request.dict()
        count = update_unknown_components_features(data_dict)
        return UpdateFeaturesResponse(count=count)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetComponentsByCircuitIdResponse(BaseModel):
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
        cluster_id: Optional[int]
        x: float
        y: float
        w: float
        h: float
        image: str
    circuit_id: int
    circuit_image: str
    recognized_components: List[RecognizedComponent]
    unknown_components: List[UnknownComponent]

@router.get("/api/db/get_components_by_circuit_id", response_model=GetComponentsByCircuitIdResponse,
            responses={404: {"description": "Not Found"},
                       500: {"description": "Internal Server Error"}})
async def get_components(circuit_id: int):
    try:
        circuit = get_circuit_by_id(circuit_id=circuit_id)
        if circuit is None:
            raise HTTPException(status_code=404, detail="Circuit not found")

        recognized_components = get_recognized_components_by_circuit_id(circuit_id=circuit.id)
        unknown_components = get_unknown_components_by_circuit_id(circuit_id=circuit.id)
        recognized_components_response = []
        unknown_components_response = []
        for component in recognized_components:
            recognized_components_response.append(GetComponentsByCircuitIdResponse.RecognizedComponent(id=component.id,
                                                                                                       x=component.x,
                                                                                                       y=component.y,
                                                                                                       w=component.w,
                                                                                                       h=component.h,
                                                                                                       image=base64.b64encode(component.image).decode('utf-8'),
                                                                                                       class_name=component.class_name,
                                                                                                       confidence=component.confidence))
        for component in unknown_components:
            unknown_components_response.append(GetComponentsByCircuitIdResponse.UnknownComponent(id=component.id,
                                                                                                 cluster_id=component.cluster_id,
                                                                                                 x=component.x,
                                                                                                 y=component.y,
                                                                                                 w=component.w,
                                                                                                 h=component.h,
                                                                                                 image=base64.b64encode(component.image).decode('utf-8')))
        return {
            "circuit_id": circuit.id,
            "circuit_image": base64.b64encode(circuit.image).decode('utf-8'),
            "recognized_components": recognized_components_response,
            "unknown_components": unknown_components_response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class Component(BaseModel):
    id: int
    x: float
    y: float
    w: float
    h: float
    image: str

class GetComponentsFullByCircuitIdResponse(BaseModel):
    class RecognizedComponent(BaseModel):
        id: int
        x: float
        y: float
        w: float
        h: float
        image: str
        class_name: str
        confidence: float
    class Cluster(BaseModel):
        id: int
        name: str
        label: int
        components: List[Component]
    circuit_id: int
    circuit_image: str
    recognized_components: List[RecognizedComponent]
    clusters: List[Cluster]
    unclustered_components: List[Component]

@router.get("/api/db/get_components_full_by_circuit_id", response_model=GetComponentsFullByCircuitIdResponse,
            responses={404: {"description": "Not Found"},
                       500: {"description": "Internal Server Error"}})
async def get_components_full_by_circuit_id(circuit_id: int):
    try:
        circuit = get_circuit_by_id(circuit_id=circuit_id)
        if circuit is None:
            raise HTTPException(status_code=404, detail="Circuit not found")

        recognized_components = get_recognized_components_by_circuit_id(circuit_id=circuit.id)
        recognized_components_response = [
            GetComponentsFullByCircuitIdResponse.RecognizedComponent(
                id=comp.id,
                x=comp.x,
                y=comp.y,
                w=comp.w,
                h=comp.h,
                image=base64.b64encode(comp.image).decode('utf-8'),
                class_name=comp.class_name,
                confidence=comp.confidence
            ) for comp in recognized_components
        ]

        clusters = get_all_clusters()
        components = get_unknown_components_by_circuit_id(circuit_id=circuit_id)

        cluster_components = defaultdict(list)
        unclustered_components_response = []
        for component in components:
            base_component = Component(
                id=component.id,
                x=component.x,
                y=component.y,
                w=component.w,
                h=component.h,
                image=base64.b64encode(component.image).decode("utf-8")
            )
            if component.cluster_id is not None:
                cluster_components[component.cluster_id].append(base_component)
            else:
                unclustered_components_response.append(base_component)

        clusters_response = []
        for cluster in clusters:
            components_in_cluster = cluster_components.get(cluster.id, [])
            if components_in_cluster:
                clusters_response.append(GetComponentsFullByCircuitIdResponse.Cluster(
                    id=cluster.id,
                    name=cluster.name,
                    label=cluster.label,
                    components=components_in_cluster
                ))

        return GetComponentsFullByCircuitIdResponse(
            circuit_id=circuit.id,
            circuit_image=base64.b64encode(circuit.image).decode("utf-8"),
            recognized_components=recognized_components_response,
            clusters=clusters_response,
            unclustered_components=unclustered_components_response
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class AddComponentsRequest(BaseModel):
    class RecognizedComponent(BaseModel):
        x: float
        y: float
        w: float
        h: float
        image: str
        class_name: str
        confidence: float
    class UnknownComponent(BaseModel):
        x: float
        y: float
        w: float
        h: float
        image: str
    circuit_image: str
    recognized_components: List[RecognizedComponent]
    unknown_components: List[UnknownComponent]

class AddComponentsResponse(BaseModel):
    circuit_id: int
    recognized_component_ids: List[int]
    unknown_component_ids: List[int]

@router.post("/api/db/add_circuit_and_components", response_model=AddComponentsResponse,
          responses={500: {"description": "Internal Server Error"}})
async def add_components(request: AddComponentsRequest):
    try:
        circuit_id = create_circuit(image=base64.b64decode(request.circuit_image))

        unknown_component_ids = []
        for component in request.unknown_components:
            component_id = create_unknown_component(circuit_id=circuit_id,
                                                 cluster_id=None,
                                                 x=component.x,
                                                 y=component.y,
                                                 w=component.w,
                                                 h=component.h,
                                                 image=base64.b64decode(component.image),
                                                 features=[])
            unknown_component_ids.append(component_id)

        recognized_component_ids = []
        for component in request.recognized_components:
            component_id = create_recognized_component(circuit_id=circuit_id,
                                                    x=component.x,
                                                    y=component.y,
                                                    w=component.w,
                                                    h=component.h,
                                                    image=base64.b64decode(component.image),
                                                    class_name=component.class_name,
                                                    confidence=component.confidence)
            recognized_component_ids.append(component_id)

        return {
            "circuit_id": circuit_id,
            "recognized_component_ids": recognized_component_ids,
            "unknown_component_ids": unknown_component_ids
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class DeleteComponentsRequest(BaseModel):
    circuit_id: int

class DeleteComponentsResponse(BaseModel):
    count: int

@router.post("/api/db/delete_components_by_circuit_id", response_model=DeleteComponentsResponse,
          responses={500: {"description": "Internal Server Error"}})
async def delete_components(request: DeleteComponentsRequest):
    try:
        count = 0

        count += delete_recognized_components_by_circuit_id(circuit_id=request.circuit_id)
        count += delete_unknown_components_by_circuit_id(circuit_id=request.circuit_id)
        delete_circuit(circuit_id=request.circuit_id)

        return DeleteComponentsResponse(count=count)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
