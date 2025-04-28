from database_module.database.core import db
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.recognized_component import RecognizedComponent
from database_module.database.tables.unknown_component import UnknownComponent


def create_circuit():
    db.create_tables([Circuit])

def create_cluster():
    db.create_tables([Cluster])

def create_unknown_component():
    db.create_tables([UnknownComponent])

def create_recognized_component():
    db.create_tables([RecognizedComponent])

def create_all_tables():
    create_circuit()
    create_cluster()
    create_unknown_component()
    create_recognized_component()
