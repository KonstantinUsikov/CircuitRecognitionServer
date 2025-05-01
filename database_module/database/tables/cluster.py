from peewee import Model, TextField, AutoField, IntegerField
from database_module.database.core import db
from database_module.database.views.cluster_view import ClusterView


class Cluster(Model):
    id = AutoField()
    name = TextField(null=False)
    label = IntegerField(null=False)

    class Meta:
        database = db
        table_name = 'cluster'

    def to_user(self):
        return ClusterView(
            cluster_id=self.id,
            name=self.name,
            label=self.label,
        )
