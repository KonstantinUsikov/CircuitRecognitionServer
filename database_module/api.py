from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import database_module.apis.cluster_api
import database_module.apis.unknown_component_api
import database_module.apis.report_api


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(database_module.apis.cluster_api.router)
app.include_router(database_module.apis.unknown_component_api.router)
app.include_router(database_module.apis.report_api.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)