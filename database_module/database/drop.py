from database_module.database.core import db_reports
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster
from database_module.database.tables.unknown_component import UnknownComponent

def drop_circuit():
    db_reports.drop_tables([Circuit])

def drop_cluster():
    db_reports.drop_tables([Cluster])

def drop_unknown_component():
    db_reports.drop_tables([UnknownComponent])

def drop_all_tables():
    drop_unknown_component()
    drop_cluster()
    drop_circuit()
