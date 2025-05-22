from database_module.database.create import create_all_tables
from database_module.database.drop import drop_all_tables
from database_module.repositories.unknown_component_repository import get_all_unknown_components, update_unknown_component, get_unknown_components_without_features, update_unknown_components_features
from database_module.repositories.recognized_component_repository import get_all_recognized_components

# drop_all_tables()
# create_all_tables()

# components = get_all_unknown_components()
# for component in components:
#     update_unknown_component(component_id=component.id, cluster_id=None)

components = get_all_unknown_components()
update_data = {
    "unknown_components": [
        {"id": component.id, "features": []} for component in components
    ]
}
update_unknown_components_features(update_data)

components = get_all_unknown_components()
for component in components:
    print(component.features)
