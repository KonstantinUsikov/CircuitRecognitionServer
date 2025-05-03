class BackendHosts:
    def __init__(self):
        self.database_host = "localhost"
        self.predict_host = "localhost"
        self.cluster_host = "localhost"
        self.database_port = 8000
        self.predict_port = 8001
        self.cluster_port = 8002
        self.database_url = f"http://{self.database_host}:{self.database_port}"
        self.predict_url = f"http://{self.predict_host}:{self.predict_port}"
        self.cluster_url = f"http://{self.cluster_host}:{self.cluster_port}"

backend_hosts = BackendHosts()
