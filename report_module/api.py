import base64
from io import BytesIO
import cv2
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
from report_module.cluster_lib import extract_features, Cluster, cluster_images

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class report_entity_input(BaseModel):
    clean: str

    class rp_shp(BaseModel):
        cls: str
        score: float
        x: float
        y: float
        w: float
        h: float

    shapes: List[rp_shp]

class report_entity_output(BaseModel):
    success: bool

@app.post("/api/report/report", response_model=report_entity_output, responses={500: {"description": "str"}})
async def report(report: report_entity_input):
    try:
        image_str = report.clean
        base64str = image_str
        # Decode the base64 string to binary data
        image_data = base64.b64decode(base64str)

        # Create a BytesIO object from the binary data
        image_bytes = BytesIO(image_data)

        image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        shapes: List[Dict] = []
        for shape in report.shapes:
            sh_img = image[int(shape.y - (shape.h / 2)):int(shape.y + (shape.h / 2)),
                     int(shape.x - (shape.w / 2)):int(shape.x + (shape.w / 2))]
            _, sh_str = cv2.imencode(".jpg", sh_img)
            sh_str = base64.b64encode(sh_str).decode("utf-8")
            shapes.append(
                {"img": sh_str,
                 "cls": shape.cls,
                 "score": shape.score,
                 "x": shape.x,
                 "y": shape.y,
                 "w": shape.w,
                 "h": shape.h}
            )
        _, img_str = cv2.imencode(".jpg", image)
        img_str = base64.b64encode(img_str).decode("utf-8")
        async with httpx.AsyncClient(timeout=999.0) as client:
            response = await client.post(f"{settings.Backends.database}/api/db/create_report",
                                         json={"img_str": img_str, "shapes": shapes})

        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))





class get_report_entity_output(BaseModel):
    id: int
    clean: str
    class rp_shp(BaseModel):
        img: str
        cls: str
        score: float
        x: float
        y: float
        w: float
        h: float
        cluster_id: Optional[int]
    shapes: List[rp_shp]
    unique_cluster_count: int
@app.get("/api/report/get_report", response_model=get_report_entity_output, responses={500: {"description": "str"}})
async def get_report():
    try:
        async with httpx.AsyncClient(timeout=999.0) as client:
            reqs = await client.get(f"{settings.Backends.database}/api/db/report_count")
        count = reqs.json()["count"]
        if (count == 0):
            raise HTTPException(status_code=500, detail="No reports found")

        async with httpx.AsyncClient(timeout=999.0) as client:
            reqs = await client.get(f"{settings.Backends.database}/api/db/random_report")
        compo = reqs.json()["report"]
        main_img = cv2.imdecode(np.frombuffer(BytesIO(base64.b64decode(compo["circuit_image_clean"])).read(), np.uint8), cv2.IMREAD_COLOR)
        _, clean_img_str = cv2.imencode(".jpg", main_img)
        clean_img_str = base64.b64encode(clean_img_str).decode("utf-8")
        shapes = []
        for shape in compo["reported_shapes"]:
            shape.setdefault("cluster_id", None)
            if shape["cluster_id"] is not None and isinstance(shape["cluster_id"], str):
                shape["cluster_id"] = int(shape["cluster_id"])
            shapes.append(shape)
        return {"id": compo["id"], "clean": clean_img_str, "shapes": shapes, "unique_cluster_count": compo["unique_cluster_count"]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class delete_report_entity_input(BaseModel):
    id: int

class delete_report_entity_output(BaseModel):
    success: bool

@app.post("/api/report/delete_report", response_model=delete_report_entity_output, responses={500: {"description": "str"}})
async def delete_report(delete_report_entity: delete_report_entity_input):
    try:
        async with httpx.AsyncClient(timeout=999.0) as client:
            reqs = await client.delete(f"{settings.Backends.database}/api/db/delete_report", params={"id":delete_report_entity.id})
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class send_report_entity_input(BaseModel):
    id: int
    pr_name: str
class send_report_entity_output(BaseModel):
    success: bool

@app.post("/api/report/send_report", response_model=send_report_entity_output, responses={500: {"description": "str"}})
async def send_report(send_report_entity: send_report_entity_input):
    try:
        async with httpx.AsyncClient(timeout=999.0) as client:
            reqs = await client.post(f"{settings.Backends.database}/api/db/report", json={"id":send_report_entity.id})
        report = reqs.json()["report"]

        image_data = base64.b64decode(report["circuit_image_clean"])
        image_bytes = BytesIO(image_data)
        image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        _, img_str = cv2.imencode(".png", image)
        img_str = base64.b64encode(img_str).decode("utf-8")

        shapes = []
        for shape in report["reported_shapes"]:
            shapes.append(
                {
                    "cls": shape["cls"],
                    "score": shape["score"],
                    "x": shape["x"],
                    "y": shape["y"],
                    "w": shape["w"],
                    "h": shape["h"]
                }
            )

        await delete_report(delete_report_entity_input(id=send_report_entity.id))
        return {"success": True}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))





class ClusterResponse(BaseModel):
    id: int
    name: str
    images: List[str]

@app.get("/api/report/get_clusters", response_model=List[ClusterResponse], responses={500: {"description": "Internal Server Error"}})
async def get_clusters_report():
    try:
        unknown_components = httpx.get(f"{settings.Backends.database}/api/db/unknown_components", timeout=999).json()

        clustered_count = sum(1 for component in unknown_components if component.get("cluster_id") is not None)
        if clustered_count == len(unknown_components):
            clusters = httpx.get(f"{settings.Backends.database}/api/db/clusters", timeout=999).json()

            clusters_dict = {}
            for unknown_component in unknown_components:
                if unknown_component['cluster_id'] not in clusters_dict:
                    clusters_dict[unknown_component['cluster_id']] = Cluster(cluster_id=unknown_component['cluster_id'],
                                                                             name=next((c["name"] for c in clusters if c["id"] == unknown_component['cluster_id']), None),
                                                                             images=[])
                clusters_dict[unknown_component['cluster_id']].images.append(unknown_component['image'])
            clusters = list(clusters_dict.values())

            result = []
            for cluster in clusters:
                result.append({
                    "id": cluster.cluster_id,
                    "name": cluster.name,
                    "images": cluster.images,
                })
            return result

        features = []
        updated_components = []
        for unknown_component in unknown_components:
            image_bytes = BytesIO(base64.b64decode(unknown_component["image"]))

            image_data = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
            if not unknown_component["features"]:
                new_features = extract_features(image_data)
                features.append(new_features)
                updated_components.append({
                    "id": unknown_component["id"],
                    "image": unknown_component["image"],
                    "features": new_features.tolist(),
                    "cluster_id": -1
                })
            else:
                features.append(unknown_component["features"])
                updated_components.append({
                    "id": unknown_component["id"],
                    "image": unknown_component["image"],
                    "features": unknown_component["features"],
                    "cluster_id": -1
                })

        cluster_ids = cluster_images(np.array(features))

        httpx.delete(
            f"{settings.Backends.database}/api/db/clusters",
            timeout=999
        )

        unique_cluster_ids = set(cluster_ids)

        cluster_names = []
        for cluster_id in unique_cluster_ids:
            cluster_name = f"Cluster {cluster_id}"
            cluster_names.append(cluster_name)

        response = httpx.post(f"{settings.Backends.database}/api/db/clusters", json={"names": cluster_names}, timeout=999)
        new_cluster_ids = response.json()['ids']

        cluster_mapping = {}
        for cluster_id, new_cluster_id in zip(unique_cluster_ids, new_cluster_ids):
            cluster_mapping[cluster_id] = new_cluster_id

        for component, cluster_id in zip(updated_components, cluster_ids):
            component["cluster_id"] = cluster_mapping[cluster_id]

        if updated_components:
            httpx.put(
                f"{settings.Backends.database}/api/db/unknown_components",
                json=updated_components,
                timeout=999
            )

        clusters_dict = {}
        for unknown_component, cluster_id in zip(unknown_components, cluster_ids):
            if cluster_mapping[cluster_id] not in clusters_dict:
                clusters_dict[cluster_mapping[cluster_id]] = Cluster(cluster_id=cluster_mapping[cluster_id], name=f"Cluster {cluster_id}", images=[])
            clusters_dict[cluster_mapping[cluster_id]].images.append(unknown_component['image'])
        clusters = list(clusters_dict.values())

        result = []
        for cluster in clusters:
            result.append({
                "id": cluster.cluster_id,
                "name": cluster.name,
                "images": cluster.images,
            })
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")







if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)