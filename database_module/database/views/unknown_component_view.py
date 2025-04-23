from typing import Optional, List


class UnknownComponentView:
    def __init__(self, component_id: int, circuit_id: int, cluster_id: Optional[int],
                 x: float, y: float, w: float, h: float, image: bytes, features: List[float]):
        self.id: int = component_id
        self.circuit_id: int = circuit_id
        self.cluster_id: Optional[int] = cluster_id
        self.x: float = x
        self.y: float = y
        self.w: float = w
        self.h: float = h
        self.image: bytes = image
        self.features: List[float] = features
