class CircuitView:
    def __init__(self, circuit_id: int, image: bytes, resized_image: bytes):
        self.id: int = circuit_id
        self.image: bytes = image
        self.resized_image: bytes = resized_image
