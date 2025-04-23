from typing import List, Optional
from database_module.database.tables.cluster import Cluster
from database_module.database.views.cluster_view import ClusterView


def create_cluster(name: str) -> int:
    cluster = Cluster.create(name=name)
    return cluster.id

def get_cluster_by_id(cluster_id: int) -> Optional[ClusterView]:
    cluster = Cluster.get_or_none(Cluster.id == cluster_id)
    if cluster:
        return cluster.to_user()
    return None

def get_all_clusters() -> List[ClusterView]:
    return [cluster.to_user() for cluster in Cluster.select()]

def update_cluster(cluster_id: int, name: Optional[str] = None) -> bool:
    cluster = Cluster.get_or_none(Cluster.id == cluster_id)
    if cluster:
        if name is not None:
            cluster.name = name
        cluster.save()
        return True
    return False

def delete_cluster(cluster_id: int) -> bool:
    cluster = Cluster.get_or_none(Cluster.id == cluster_id)
    if cluster:
        cluster.delete_instance()
        return True
    return False
