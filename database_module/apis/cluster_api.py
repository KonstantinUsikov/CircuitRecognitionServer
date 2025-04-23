import traceback
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from database_module.repositories import cluster_repository
from fastapi import APIRouter

router = APIRouter()


class GetClustersResponse(BaseModel):
    id: int
    name: str

@router.get("/api/db/clusters", response_model=List[GetClustersResponse], responses={500: {"description": "Internal Server Error"}})
async def get_all_clusters():
    try:
        clusters = cluster_repository.get_all_clusters()
        result = []
        for cluster in clusters:
            result.append({
                "id": cluster.id,
                "name": cluster.name,
            })
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class CreateClusterRequest(BaseModel):
    names: List[str]

class CreateClusterResponse(BaseModel):
    ids: List[int]

@router.post("/api/db/clusters", response_model=CreateClusterResponse, responses={500: {"description": "Internal Server Error"}})
async def create_multiple_clusters(data: CreateClusterRequest):
    try:
        cluster_ids = []
        for name in data.names:
            cluster_id = cluster_repository.create_cluster(name=name)
            cluster_ids.append(cluster_id)
        return {"ids": cluster_ids}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


class DeleteClustersResponse(BaseModel):
    success: bool

@router.delete("/api/db/clusters", response_model=DeleteClustersResponse, responses={500: {"description": "Internal Server Error"}})
async def delete_all_clusters():
    try:
        clusters = cluster_repository.get_all_clusters()
        for cluster in clusters:
            cluster_repository.delete_cluster(cluster.id)
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
