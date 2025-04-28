from database_module.database.core import db
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.recognized_component import RecognizedComponent
from database_module.database.tables.unknown_component import UnknownComponent

def drop_circuit():
    db.drop_tables([Circuit])

def drop_cluster():
    db.drop_tables([Cluster])

def drop_unknown_component():
    db.drop_tables([UnknownComponent])

def drop_recognized_component():
    db.drop_tables([RecognizedComponent])

def drop_all_tables():
    drop_unknown_component()
    drop_cluster()
    drop_circuit()
