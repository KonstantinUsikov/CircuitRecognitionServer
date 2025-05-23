from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
import traceback
import base64
from collections import defaultdict
from typing import List

from database_module.repositories import circuit_repository
from database_module.repositories import cluster_repository
from database_module.repositories import unknown_component_repository


router = APIRouter()


class Component(BaseModel):
    id: int
    circuit_id: int
    x: float
    y: float
    w: float
    h: float
    image: str

class GetClustersResponse(BaseModel):
    class Cluster(BaseModel):
        id: int
        name: str
        label: int
        components: List[Component]
    clusters: List[Cluster]
    unclustered_components: List[Component]

@router.get("/api/db/get_clusters", response_model=GetClustersResponse,
            responses={500: {"description": "Internal Server Error"}})
async def get_clusters():
    try:
        clusters = cluster_repository.get_all_clusters()
        components = unknown_component_repository.get_all_unknown_components()

        cluster_components = defaultdict(list)
        unclustered_components = []
        for component in components:
            if component.cluster_id is not None:
                cluster_components[component.cluster_id].append(component)
            else:
                unclustered_components.append(Component(id=component.id,
                                                        circuit_id=component.circuit_id,
                                                        x=component.x,
                                                        y=component.y,
                                                        w=component.w,
                                                        h=component.h,
                                                        image=base64.b64encode(component.image).decode('utf-8')))

        response_clusters = []
        for cluster in clusters:
            components_in_cluster = cluster_components.get(cluster.id, [])
            components_in_cluster_response = []
            for component in components_in_cluster:
                components_in_cluster_response.append(Component(
                    id=component.id,
                    circuit_id=component.circuit_id,
                    x=component.x,
                    y=component.y,
                    w=component.w,
                    h=component.h,
                    image=base64.b64encode(component.image).decode("utf-8")
                ))
            if components_in_cluster:
                response_clusters.append(GetClustersResponse.Cluster(
                    id=cluster.id,
                    name=cluster.name,
                    label=cluster.label,
                    components=components_in_cluster_response
                ))

        return GetClustersResponse(clusters=response_clusters, unclustered_components=unclustered_components)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetClustersByCircuitIdResponse(BaseModel):
    class Cluster(BaseModel):
        id: int
        name: str
        label: int
        components: List[Component]
    clusters: List[Cluster]
    unclustered_components: List[Component]

@router.get("/api/db/get_clusters_by_circuit_id", response_model=GetClustersByCircuitIdResponse,
            responses={500: {"description": "Internal Server Error"}})
async def get_clusters_by_circuit_id(circuit_id: int):
    try:
        circuit = circuit_repository.get_circuit_by_id(circuit_id=circuit_id)
        if circuit is None:
            raise HTTPException(status_code=404, detail="Circuit not found")

        clusters = cluster_repository.get_all_clusters()
        components = unknown_component_repository.get_unknown_components_by_circuit_id(circuit_id=circuit_id)

        cluster_components = defaultdict(list)
        unclustered_components = []
        for component in components:
            if component.cluster_id is not None:
                cluster_components[component.cluster_id].append(component)
            else:
                unclustered_components.append(Component(id=component.id,
                                                        circuit_id=component.circuit_id,
                                                        x=component.x,
                                                        y=component.y,
                                                        w=component.w,
                                                        h=component.h,
                                                        image=base64.b64encode(component.image).decode('utf-8')))

        response_clusters = []
        for cluster in clusters:
            components_in_cluster = cluster_components.get(cluster.id, [])
            components_in_cluster_response = []
            for component in components_in_cluster:
                components_in_cluster_response.append(Component(
                    id=component.id,
                    circuit_id=component.circuit_id,
                    x=component.x,
                    y=component.y,
                    w=component.w,
                    h=component.h,
                    image=base64.b64encode(component.image).decode("utf-8")
                ))
            if components_in_cluster:
                response_clusters.append(GetClustersByCircuitIdResponse.Cluster(
                    id=cluster.id,
                    name=cluster.name,
                    label=cluster.label,
                    components=components_in_cluster_response
                ))

        return GetClustersByCircuitIdResponse(clusters=response_clusters, unclustered_components=unclustered_components)

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class RecreateClustersRequest(BaseModel):
    class Cluster(BaseModel):
        name: str
        label: int
        component_ids: List[int]
    clusters: List[Cluster]

class RecreateClustersResponse(BaseModel):
    cluster_ids: List[int]

@router.post("/api/db/recreate_clusters", response_model=RecreateClustersResponse,
          responses={500: {"description": "Internal Server Error"}})
async def recreate_clusters(request: RecreateClustersRequest):
    try:
        cluster_repository.delete_all_clusters()

        cluster_data = [{"name": cluster.name, "label": cluster.label} for cluster in request.clusters]
        cluster_ids = cluster_repository.create_clusters(clusters=cluster_data)

        for idx, cluster in enumerate(request.clusters):
            unknown_component_repository.update_clusters_for_components(component_ids=cluster.component_ids, cluster_id=cluster_ids[idx])

        return RecreateClustersResponse(cluster_ids=cluster_ids)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
