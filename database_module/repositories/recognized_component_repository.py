from typing import List, Optional
from database_module.database.tables.recognized_component import RecognizedComponent
from database_module.database.views.recognized_component_view import RecognizedComponentView


def create_recognized_component(circuit_id: int, x: float, y: float, w: float, h: float, image: bytes, class_name: str, confidence: float) -> int:
    component = RecognizedComponent.create(
        circuit=circuit_id,
        x=x,
        y=y,
        w=w,
        h=h,
        image=image,
        class_name=class_name,
        confidence=confidence
    )
    return component.id

def get_recognized_component_by_id(component_id: int) -> Optional[RecognizedComponentView]:
    component = RecognizedComponent.get_or_none(RecognizedComponent.id == component_id)
    if component:
        return component.to_user()
    return None

def get_recognized_components_by_circuit_id(circuit_id: int) -> List[RecognizedComponentView]:
    recognized_components = RecognizedComponent.select().where(RecognizedComponent.circuit_id == circuit_id)
    return [component.to_user() for component in recognized_components]

def get_all_recognized_components() -> List[RecognizedComponentView]:
    return [component.to_user() for component in RecognizedComponent.select()]

def update_recognized_component(component_id: int, x: Optional[float] = None, y: Optional[float] = None, w: Optional[float] = None, h: Optional[float] = None, image: Optional[bytes] = None, class_name: Optional[str] = None, confidence: Optional[float] = None) -> bool:
    component = RecognizedComponent.get_or_none(RecognizedComponent.id == component_id)
    if component:
        if x is not None:
            component.x = x
        if y is not None:
            component.y = y
        if w is not None:
            component.w = w
        if h is not None:
            component.h = h
        if image is not None:
            component.image = image
        if class_name is not None:
            component.class_name = class_name
        if confidence is not None:
            component.confidence = confidence
        component.save()
        return True
    return False

def delete_recognized_component(component_id: int) -> bool:
    component = RecognizedComponent.get_or_none(RecognizedComponent.id == component_id)
    if component:
        component.delete_instance()
        return True
    return False

def delete_recognized_components_by_circuit_id(circuit_id: int) -> bool:
    query = RecognizedComponent.delete().where(RecognizedComponent.circuit_id == circuit_id)
    deleted_count = query.execute()
    return deleted_count > 0
