from typing import List, Optional
from database_module.database.tables.circuit import Circuit
from database_module.database.views.circuit_view import CircuitView


def create_circuit(image: bytes) -> int:
    circuit = Circuit.create(image=image)
    return circuit.id

def get_circuits_count() -> int:
    count = Circuit.select().count()
    return count

def get_circuit_by_id(circuit_id: int) -> Optional[CircuitView]:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        return circuit.to_user()
    return None

def get_last_circuit() -> Optional[CircuitView]:
    last_circuit = Circuit.select().order_by(Circuit.id.desc()).get()
    if last_circuit:
        return last_circuit.to_user()
    return None

def get_all_circuits() -> List[CircuitView]:
    return [circuit.to_user() for circuit in Circuit.select()]

def update_circuit(circuit_id: int, image: Optional[bytes] = None) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        if image is not None:
            circuit.image = image
        circuit.save()
        return True
    return False

def delete_circuit(circuit_id: int) -> bool:
    circuit = Circuit.get_or_none(Circuit.id == circuit_id)
    if circuit:
        circuit.delete_instance()
        return True
    return False
