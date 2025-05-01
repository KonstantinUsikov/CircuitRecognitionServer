from typing import List, Optional
from database_module.database.tables.unknown_component import UnknownComponent
from database_module.database.views.unknown_component_view import UnknownComponentView


def create_unknown_component(circuit_id: int, cluster_id: Optional[int], x: float, y: float, w: float, h: float, image: bytes, features: List[float]) -> int:
    component = UnknownComponent.create(
        circuit=circuit_id,
        cluster=cluster_id,
        x=x,
        y=y,
        w=w,
        h=h,
        image=image,
        features=features
    )
    return component.id

def get_unknown_component_by_id(component_id: int) -> Optional[UnknownComponentView]:
    component = UnknownComponent.get_or_none(UnknownComponent.id == component_id)
    if component:
        return component.to_user()
    return None

def get_unknown_components_by_circuit_id(circuit_id: int) -> List[UnknownComponentView]:
    unknown_components = UnknownComponent.select().where(UnknownComponent.circuit_id == circuit_id)
    return [component.to_user() for component in unknown_components]

def get_all_unknown_components() -> List[UnknownComponentView]:
    return [component.to_user() for component in UnknownComponent.select()]

def update_unknown_component(component_id: int, circuit_id: Optional[int] = None, cluster_id: Optional[int] = None, x: Optional[float] = None, y: Optional[float] = None, w: Optional[float] = None, h: Optional[float] = None, image: Optional[bytes] = None, features: Optional[List[float]] = None) -> bool:
    component = UnknownComponent.get_or_none(UnknownComponent.id == component_id)
    if component:
        if circuit_id is not None:
            component.circuit = circuit_id
        if cluster_id is not None:
            component.cluster = cluster_id
        if x is not None:
            component.x = x
        if y is not None:
            component.y = y
        if w is not None:
            component.w = w
        if h is not None:
            component.h = h
        if image is not None:
            component.circuit_data = image
        if features is not None:
            component.features = features
        component.save()
        return True
    return False

def delete_unknown_component(component_id: int) -> bool:
    component = UnknownComponent.get_or_none(UnknownComponent.id == component_id)
    if component:
        component.delete_instance()
        return True
    return False

def delete_unknown_components_by_circuit_id(circuit_id: int) -> int:
    query = UnknownComponent.delete().where(UnknownComponent.circuit_id == circuit_id)
    deleted_count = query.execute()
    return deleted_count

def update_clusters_for_components(component_ids: List[int], cluster_id: int) -> int:
    if not component_ids:
        return 0
    updated_count = (UnknownComponent
                     .update({UnknownComponent.cluster: cluster_id})
                     .where(UnknownComponent.id.in_(component_ids))
                     .execute())
    return updated_count
