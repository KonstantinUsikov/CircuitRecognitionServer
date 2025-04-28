import base64
from typing import List, Optional
from peewee import DoesNotExist
from database_module.repositories.circuit_repository import create_circuit, get_circuit_by_id
from database_module.database.models import ReportedShape, ReportView
from database_module.repositories.recognized_component_repository import create_recognized_component, \
    get_recognized_components_by_circuit_id, delete_recognized_components_by_circuit_id
from database_module.repositories.unknown_component_repository import create_unknown_component, get_unknown_components_by_circuit_id, delete_unknown_components_by_circuit_id
from database_module.repositories.circuit_repository import get_last_circuit, get_all_circuits, delete_circuit, get_circuits_count
from database_module.image_helper import encode_image


def create_report(circuit_image: bytes, reported_shapes: List[ReportedShape]) -> int:
    circuit_id = create_circuit(image=circuit_image)
    for shape in reported_shapes:
        if shape.cls != "-":
            create_recognized_component(circuit_id=circuit_id,
                                        x=shape.x,
                                        y=shape.y,
                                        w=shape.w,
                                        h=shape.h,
                                        image=base64.b64decode(shape.img),
                                        class_name=shape.cls,
                                        confidence=shape.score)
        else:
            create_unknown_component(circuit_id=circuit_id,
                                     cluster_id=None,
                                     x=shape.x,
                                     y=shape.y,
                                     w=shape.w,
                                     h=shape.h,
                                     image=base64.b64decode(shape.img),
                                     features=[])
    return circuit_id


def get_report_by_circuit_id(circuit_id: int) -> Optional[ReportView]:
    try:
        circuit = get_circuit_by_id(circuit_id)

        recognized_components = get_recognized_components_by_circuit_id(circuit_id)
        unknown_components = get_unknown_components_by_circuit_id(circuit_id)

        reported_shapes = []
        for component in recognized_components:
            reported_shapes.append(ReportedShape(
                img=encode_image(component.image),
                cls=component.class_name,
                score=component.confidence,
                x=component.x,
                y=component.y,
                w=component.w,
                h=component.h,
                cluster_id=-1
            ))

        unique_cluster_ids = set()
        for component in unknown_components:
            reported_shapes.append(ReportedShape(
                img=encode_image(component.image),
                cls="-",
                score=0.0,
                x=component.x,
                y=component.y,
                w=component.w,
                h=component.h,
                cluster_id=component.cluster_id
            ))
            if component.cluster_id is not None and component.cluster_id > 0:
                unique_cluster_ids.add(component.cluster_id)

        return ReportView(
            field_id=circuit.id,
            circuit_image_clean=circuit.image,
            reported_shapes=reported_shapes,
            unique_cluster_count=len(unique_cluster_ids)
        )
    except DoesNotExist:
        return None


def get_last_report() -> Optional[ReportView]:
    last_circuit = get_last_circuit()
    if last_circuit:
        return get_report_by_circuit_id(last_circuit.id)
    return None


def get_all_reports() -> List[ReportView]:
    reports = []
    for circuit in get_all_circuits():
        report = get_report_by_circuit_id(circuit.id)
        if report:
            reports.append(report)
    return reports


def get_reports_count() -> int:
    return get_circuits_count()


def delete_report(circuit_id: int):
    try:
        delete_unknown_components_by_circuit_id(circuit_id)
        delete_recognized_components_by_circuit_id(circuit_id)

        delete_circuit(circuit_id)
        return True
    except DoesNotExist:
        return True
    except Exception:
        return False
