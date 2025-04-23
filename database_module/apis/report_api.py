import base64
import traceback
from io import BytesIO
from typing import List, Optional, Dict

import cv2
import httpx
import numpy as np
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from database_module.repositories import reports_repository
from database_module.database.models import ReportedShape, ReportView


from fastapi import APIRouter

router = APIRouter()

class CreateReportRequest(BaseModel):
    img_str: bytes
    class rp_shp(BaseModel):
        img: str
        cls: str
        score: float
        x: float
        y: float
        w: float
        h: float
    shapes: List[rp_shp]

class CreateReportResponse(BaseModel):
    id: int

@router.post("/api/db/create_report", response_model=CreateReportResponse, responses={500: {"description": "Internal Server Error"}})
async def create_report(request: CreateReportRequest):
    try:
        shapes = []
        for shape in request.shapes:
            shapes.append(ReportedShape(img=shape.img, cls=shape.cls, score=shape.score, x=shape.x, y=shape.y, w=shape.w, h=shape.h))
        report_id= reports_repository.create_report(request.img_str, shapes)
        return {"id": report_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class ReportCountResponse(BaseModel):
    count: int

@router.get("/api/db/report_count", response_model=ReportCountResponse, responses={500: {"description": "Internal Server Error"}})
async def report_count():
    try:
        count = reports_repository.get_reports_count()
        return {"count": count}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class RandomReportResponse(BaseModel):
    class rp(BaseModel):
        class rp_shp(BaseModel):
            img: str
            cls: str
            score: float
            x: float
            y: float
            w: float
            h: float
            cluster_id: Optional[int]
        id: int
        circuit_image_clean: bytes
        reported_shapes: List[rp_shp]
        unique_cluster_count: int
    report: rp

@router.get("/api/db/random_report", response_model=RandomReportResponse, responses={500: {"description": "Internal Server Error"}})
async def random_report():
    try:
        report= reports_repository.get_last_report()
        return {"report": report}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class DeleteReportResponse(BaseModel):
    success: bool

@router.delete("/api/db/delete_report", response_model=DeleteReportResponse, responses={500: {"description": "Internal Server Error"}})
async def delete_report(id: int):
    try:
        success = reports_repository.delete_report(id)
        return {"success": success}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetReportByIdRequest(BaseModel):
    id: int

class GetReportByIdResponse(BaseModel):
    class rp(BaseModel):
        class rp_shp(BaseModel):
            img: str
            cls: str
            score: float
            x: float
            y: float
            w: float
            h: float
        id: int
        circuit_image_clean: str
        reported_shapes: List[rp_shp]
    report: rp

@router.post("/api/db/report", response_model=GetReportByIdResponse, responses={500: {"description": "Internal Server Error"}})
async def get_report_by_id(request: GetReportByIdRequest):
    try:
        report= reports_repository.get_report_by_circuit_id(request.id)
        return {"report": report}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class GetReportsResponse(BaseModel):
    class rp(BaseModel):
        class rp_shp(BaseModel):
            img: str
            cls: str
            score: float
            x: float
            y: float
            w: float
            h: float
        id: int
        circuit_image_clean: str
        reported_shapes: List[rp_shp]
    report: rp

@router.get("/api/db/report", response_model=GetReportsResponse, responses={500: {"description": "Internal Server Error"}})
async def get_reports():
    try:
        reports= reports_repository.get_all_reports()
        return {"reports": reports}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")









# class ClusterResponse(BaseModel):
#     id: int
#     name: str
#     images: List[str]
#
# @router.get("/api/report/get_clusters", response_model=List[ClusterResponse], responses={500: {"description": "Internal Server Error"}})
# async def get_clusters_report():
#     try:
#         unknown_components = httpx.get(f"{settings.Backends.database}/api/db/unknown_components", headers={"Authorization": auth}, timeout=999).json()
#
#         clustered_count = sum(1 for component in unknown_components if component.get("cluster_id") is not None)
#         if clustered_count == len(unknown_components):
#             clusters = httpx.get(f"{settings.Backends.database}/api/db/clusters", headers={"Authorization": auth}, timeout=999).json()
#
#             clusters_dict = {}
#             for unknown_component in unknown_components:
#                 if unknown_component['cluster_id'] not in clusters_dict:
#                     clusters_dict[unknown_component['cluster_id']] = Cluster(cluster_id=unknown_component['cluster_id'],
#                                                                              name=next((c["name"] for c in clusters if c["id"] == unknown_component['cluster_id']), None),
#                                                                              images=[])
#                 clusters_dict[unknown_component['cluster_id']].images.append(unknown_component['image'])
#             clusters = list(clusters_dict.values())
#
#             result = []
#             for cluster in clusters:
#                 result.append({
#                     "id": cluster.cluster_id,
#                     "name": cluster.name,
#                     "images": cluster.images,
#                 })
#             return result
#
#         features = []
#         updated_components = []
#         for unknown_component in unknown_components:
#             image_bytes = BytesIO(base64.b64decode(unknown_component["image"]))
#
#             image_data = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
#             if not unknown_component["features"]:
#                 new_features = extract_features(image_data)
#                 features.append(new_features)
#                 updated_components.append({
#                     "id": unknown_component["id"],
#                     "image": unknown_component["image"],
#                     "features": new_features.tolist(),
#                     "cluster_id": -1
#                 })
#             else:
#                 features.append(unknown_component["features"])
#                 updated_components.append({
#                     "id": unknown_component["id"],
#                     "image": unknown_component["image"],
#                     "features": unknown_component["features"],
#                     "cluster_id": -1
#                 })
#
#         cluster_ids = cluster_images(np.array(features))
#
#         httpx.delete(
#             f"{settings.Backends.database}/api/db/clusters",
#             timeout=999, headers={"Authorization": auth}
#         )
#
#         unique_cluster_ids = set(cluster_ids)
#
#         cluster_names = []
#         for cluster_id in unique_cluster_ids:
#             cluster_name = f"Cluster {cluster_id}"
#             cluster_names.append(cluster_name)
#
#         response = httpx.post(f"{settings.Backends.database}/api/db/clusters", json={"names": cluster_names}, timeout=999)
#         new_cluster_ids = response.json()['ids']
#
#         cluster_mapping = {}
#         for cluster_id, new_cluster_id in zip(unique_cluster_ids, new_cluster_ids):
#             cluster_mapping[cluster_id] = new_cluster_id
#
#         for component, cluster_id in zip(updated_components, cluster_ids):
#             component["cluster_id"] = cluster_mapping[cluster_id]
#
#         if updated_components:
#             httpx.put(
#                 f"{settings.Backends.database}/api/db/unknown_components",
#                 json=updated_components,
#                 timeout=999
#             )
#
#         clusters_dict = {}
#         for unknown_component, cluster_id in zip(unknown_components, cluster_ids):
#             if cluster_mapping[cluster_id] not in clusters_dict:
#                 clusters_dict[cluster_mapping[cluster_id]] = Cluster(cluster_id=cluster_mapping[cluster_id], name=f"Cluster {cluster_id}", images=[])
#             clusters_dict[cluster_mapping[cluster_id]].images.append(unknown_component['image'])
#         clusters = list(clusters_dict.values())
#
#         result = []
#         for cluster in clusters:
#             result.append({
#                 "id": cluster.cluster_id,
#                 "name": cluster.name,
#                 "images": cluster.images,
#             })
#         return result
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Internal Server Error")
