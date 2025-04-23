import uvicorn
import threading


def run_app(app, port):
    try:
        print(f"Starting app on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Failed to start app on port {port}: {e}")


if __name__ == "__main__":
    import database_module.api
    import predict_module.api
    import report_module.api

    threading.Thread(target=run_app, args=(database_module.api.app, 8000), daemon=True).start()
    threading.Thread(target=run_app, args=(predict_module.api.app, 8001), daemon=True).start()
    threading.Thread(target=run_app, args=(report_module.api.app, 8002), daemon=True).start()

    # чтобы главный поток не завершался сразу
    threading.Event().wait()
