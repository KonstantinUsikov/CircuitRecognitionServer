class __backends__:
    def __init__(self):
        self.database = "http://localhost:8000"
        self.predict = "http://localhost:8001"
        self.report = "http://localhost:8002"
Backends = __backends__()
