from peewee import Model, TextField, AutoField, ForeignKeyField, FloatField, BlobField
from database_module.database.core import db
from database_module.database.views.recognized_component_view import RecognizedComponentView
from database_module.database.tables.circuit import Circuit


class RecognizedComponent(Model):
    id = AutoField()
    circuit = ForeignKeyField(Circuit, backref='unknown_components', on_delete='CASCADE', column_name='circuit_id', null=False)
    x = FloatField(null=False)
    y = FloatField(null=False)
    w = FloatField(null=False)
    h = FloatField(null=False)
    image = BlobField(null=False)
    class_name = TextField(null=False)
    confidence = FloatField(null=False)

    class Meta:
        database = db
        table_name = 'recognized_component'

    def to_user(self):
        return RecognizedComponentView(
            component_id=self.id,
            circuit_id=self.circuit_id,
            x=self.x,
            y=self.y,
            w=self.w,
            h=self.h,
            image=bytes(self.image),
            class_name=self.class_name,
            confidence=self.confidence
        )
