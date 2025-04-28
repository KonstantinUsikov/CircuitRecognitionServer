from database_module.database.create import create_all_tables
from database_module.database.drop import drop_all_tables
from database_module.repositories.unknown_component_repository import get_all_unknown_components

drop_all_tables()
create_all_tables()

components = get_all_unknown_components()
for component in components:
    print(component)
