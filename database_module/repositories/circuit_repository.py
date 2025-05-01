import hashlib
from typing import List, Optional
from database_module.database.tables.circuit import Circuit
from database_module.database.views.circuit_view import CircuitView


def create_circuit(image: bytes) -> int:
    circuit = Circuit.create(image=image)
    return circuit.id

def get_circuit_by_id(circuit_id: int) -> Optional[CircuitView]:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        return circuit.to_user()
    return None

def get_all_circuits() -> List[CircuitView]:
    return [circuit.to_user() for circuit in Circuit.select()]

def get_circuits_by_image(image_bytes: bytes) -> List[CircuitView]:
    circuit_image_hash = get_image_hash(image_bytes)
    all_circuits = get_all_circuits()
    circuits = []
    for circuit in all_circuits:
        if get_image_hash(circuit.image) == circuit_image_hash:
            circuits.append(circuit)
    return circuits

def update_circuit(circuit_id: int, image: Optional[bytes] = None) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        if image is not None:
            circuit.circuit_data = image
        circuit.save()
        return True
    return False

def delete_circuit(circuit_id: int) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        circuit.delete_instance()
        return True
    return False

def delete_circuits(circuit_ids: List[int]) -> int:
    deleted_count = Circuit.delete().where(Circuit.id.in_(circuit_ids)).execute()
    return deleted_count

def get_image_hash(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()
