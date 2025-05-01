import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database_module.apis.circuit_api
import database_module.apis.component_api
import database_module.apis.cluster_api
from settings import backend_hosts


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(database_module.apis.circuit_api.router)
app.include_router(database_module.apis.component_api.router)
app.include_router(database_module.apis.cluster_api.router)


if __name__ == "__main__":
    uvicorn.run(app, host=backend_hosts.database_host, port=backend_hosts.database_port)
