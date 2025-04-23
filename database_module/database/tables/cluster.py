from peewee import Model, TextField, AutoField
from database_module.database.core import db_reports
from database_module.database.views.cluster_view import ClusterView


class Cluster(Model):
    id = AutoField()
    name = TextField(null=False)

    class Meta:
        database = db_reports
        table_name = 'cluster'

    def to_user(self):
        return ClusterView(
            cluster_id=self.id,
            name=self.name,
        )
