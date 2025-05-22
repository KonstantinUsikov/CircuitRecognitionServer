import uvicorn
import threading
from settings import backend_hosts


def run_app(app, host, port):
    try:
        print(f"Starting app on port {port}")
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print(f"Failed to start app on port {port}: {e}")


if __name__ == "__main__":
    import database_module.api
    import predict_module.api
    import cluster_module.api
    from cluster_module.feature_client import run_feature_loop

    threading.Thread(target=run_app, args=(database_module.api.app, backend_hosts.database_host, backend_hosts.database_port), daemon=True).start()
    threading.Thread(target=run_app, args=(predict_module.api.app, backend_hosts.predict_host, backend_hosts.predict_port), daemon=True).start()
    threading.Thread(target=run_app, args=(cluster_module.api.app, backend_hosts.cluster_host, backend_hosts.cluster_port), daemon=True).start()
    threading.Thread(target=run_feature_loop, daemon=True).start()

    threading.Event().wait()
