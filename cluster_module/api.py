import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
import traceback
import httpx
import numpy as np
import cv2
import base64
from io import BytesIO
from typing import List

from settings import backend_hosts
from cluster_module.cluster_lib import extract_features, cluster_images

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Component(BaseModel):
    id: int
    circuit_id: int
    x: float
    y: float
    w: float
    h: float
    image: str

class ClusterizationResponse(BaseModel):
    class Cluster(BaseModel):
        id: int
        name: str
        label: int
        components: List[Component]
    clusters: List[Cluster]
    unclustered_components: List[Component]

@app.post("/api/cluster/run_clusterization", response_model=ClusterizationResponse, responses={500: {"description": "Internal Server Error"}})
async def run_clusterization():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_hosts.database_url}/api/db/get_unknown_components")
            response.raise_for_status()
            get_unknown_components_result = response.json()
        unknown_components = get_unknown_components_result["unknown_components"]

        clustered_count = sum(1 for component in unknown_components if component.get("cluster_id") is not None)
        if clustered_count != len(unknown_components):
            features = []
            for unknown_component in unknown_components:
                if unknown_component["features"]:
                    features.append(unknown_component["features"])
                else:
                    image_bytes = BytesIO(base64.b64decode(unknown_component["image"]))
                    image_data = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
                    image_features = extract_features(image_data)
                    features.append(image_features)
            cluster_labels = cluster_images(np.array(features))

            cluster_components = {}
            for cluster_label, unknown_component in zip(cluster_labels, unknown_components):
                if cluster_label not in cluster_components:
                    cluster_components[cluster_label] = []
                cluster_components[cluster_label].append(unknown_component["id"])

            clusters_request = []
            for cluster_label, component_ids in cluster_components.items():
                clusters_request.append({
                    "name": f"Cluster {cluster_label}",
                    "label": cluster_label,
                    "component_ids": component_ids,
                })

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{backend_hosts.database_url}/api/db/recreate_clusters",
                    json={"clusters": clusters_request}
                )
                response.raise_for_status()
                recreate_clusters_result = response.json()

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_hosts.database_url}/api/db/get_clusters")
            response.raise_for_status()
            get_clusters_result = response.json()
        return ClusterizationResponse(**get_clusters_result)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(app, host=backend_hosts.cluster_host, port=backend_hosts.cluster_port)
