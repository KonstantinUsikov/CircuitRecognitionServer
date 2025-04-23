from database_module.database.core import db_reports
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.unknown_component import UnknownComponent


def create_circuit():
    db_reports.create_tables([Circuit])

def create_cluster():
    db_reports.create_tables([Cluster])

def create_unknown_component():
    db_reports.create_tables([UnknownComponent])

def create_all_tables():
    create_circuit()
    create_cluster()
    create_unknown_component()
