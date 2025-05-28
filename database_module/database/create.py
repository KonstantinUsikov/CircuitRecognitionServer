from database_module.database.core import db
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.recognized_component import RecognizedComponent
from database_module.database.tables.unknown_component import UnknownComponent


def create_circuit_table():
    db.create_tables([Circuit])

def create_cluster_table():
    db.create_tables([Cluster])

def create_unknown_component_table():
    db.create_tables([UnknownComponent])

def create_recognized_component_table():
    db.create_tables([RecognizedComponent])

def create_all_tables():
    create_circuit_table()
    create_cluster_table()
    create_unknown_component_table()
    create_recognized_component_table()


if __name__ == '__main__':
    create_all_tables()