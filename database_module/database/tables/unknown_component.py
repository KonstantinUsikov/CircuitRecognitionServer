# noinspection PyUnresolvedReferences
from playhouse.postgres_ext import ArrayField
from peewee import Model, AutoField, ForeignKeyField, FloatField, BlobField
from database_module.database.core import db_reports
from database_module.database.views.unknown_component_view import UnknownComponentView
from database_module.database.tables.circuit import Circuit
from database_module.database.tables.cluster import Cluster


class UnknownComponent(Model):
    id = AutoField()
    circuit = ForeignKeyField(Circuit, backref='unknown_components', on_delete='CASCADE', column_name='circuit_id', null=False)
    cluster = ForeignKeyField(Cluster, backref='unknown_components', on_delete='SET NULL', column_name='cluster_id',null=True)
    x = FloatField(null=False)
    y = FloatField(null=False)
    w = FloatField(null=False)
    h = FloatField(null=False)
    image = BlobField(null=False)
    features = ArrayField(FloatField, null=False)

    class Meta:
        database = db_reports
        table_name = 'unknown_component'

    def to_user(self):
        return UnknownComponentView(
            component_id=self.id,
            circuit_id=self.circuit_id,
            cluster_id=self.cluster_id,
            x=self.x,
            y=self.y,
            w=self.w,
            h=self.h,
            image=bytes(self.image),
            features=self.features or []
        )
