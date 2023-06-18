import atexit

from peewee import Model, IntegerField, TextField, FloatField
from playhouse.sqliteq import SqliteQueueDatabase

# TODO: special sqlite connection
database = SqliteQueueDatabase(
    '../database.db',
    pragmas={"jurnal_mode": "wal"},
)
atexit.register(lambda: database.stop())


class BaseModel(Model):
    class Meta:
        database = database


class Measurement(BaseModel):
    id = TextField(primary_key=True)
    time = FloatField()
    weight = FloatField()


class Setting(BaseModel):
    key = TextField(primary_key=True)
    value = TextField()
