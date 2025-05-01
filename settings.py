class BackendHosts:
    def __init__(self):
        self.database_host = "localhost"
        self.predict_host = "localhost"
        self.report_host = "localhost"
        self.database_port = 8000
        self.predict_port = 8001
        self.report_port = 8002
        self.database_url = f"http://{self.database_host}:{self.database_port}"
        self.predict_url = f"http://{self.predict_host}:{self.predict_port}"
        self.report_url = f"http://{self.report_host}:{self.report_port}"

backend_hosts = BackendHosts()
