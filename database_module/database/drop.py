from database_module.database.core import db
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.recognized_component import RecognizedComponent
from database_module.database.tables.unknown_component import UnknownComponent


def drop_circuit_table():
    db.drop_tables([Circuit])

def drop_cluster_table():
    db.drop_tables([Cluster])

def drop_unknown_component_table():
    db.drop_tables([UnknownComponent])

def drop_recognized_component_table():
    db.drop_tables([RecognizedComponent])

def drop_all_tables():
    drop_unknown_component_table()
    drop_recognized_component_table()
    drop_cluster_table()
    drop_circuit_table()
