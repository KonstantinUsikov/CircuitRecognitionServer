class RecognizedComponentView:
    def __init__(self, component_id: int, circuit_id: int, x: float, y: float, w: float, h: float,
                 image: bytes, class_name: str, confidence: float):
        self.id: int = component_id
        self.circuit_id: int = circuit_id
        self.x: float = x
        self.y: float = y
        self.w: float = w
        self.h: float = h
        self.image: bytes = image
        self.class_name: str = class_name
        self.confidence: float = confidence
