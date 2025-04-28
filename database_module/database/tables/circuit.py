from peewee import Model, AutoField, BlobField
from database_module.database.core import db
from database_module.database.views.circuit_view import CircuitView


class Circuit(Model):
    id = AutoField()
    image = BlobField(null=False)

    class Meta:
        database = db
        table_name = 'circuit'

    def to_user(self):
        return CircuitView(
            circuit_id=self.id,
            image=bytes(self.image),
        )
