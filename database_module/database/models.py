from typing import List, Optional


class ReportedShape:
    def __init__(self, img: str, cls: str, score: float, x: float, y: float, w: float, h: float, cluster_id: Optional[int] = None):
        self.img: str = img
        self.cls: str = cls
        self.score: float = score
        self.x: float = x
        self.y: float = y
        self.w: float = w
        self.h: float = h
        self.cluster_id: Optional[int] = cluster_id

class ReportView:
    def __init__(self, field_id: int, circuit_image_clean: bytes, reported_shapes: List[ReportedShape], unique_cluster_count: int):
        self.id: int = field_id
        self.circuit_image_clean: bytes = circuit_image_clean
        self.reported_shapes: List[ReportedShape] = reported_shapes
        self.unique_cluster_count: int = unique_cluster_count
