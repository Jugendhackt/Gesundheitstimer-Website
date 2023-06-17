from peewee import SqliteDatabase, Model, IntegerField, TextField, FloatField

database = SqliteDatabase('../database.db')


class BaseModel(Model):
    class Meta:
        database = database


class Measurement(BaseModel):
    id = TextField(primary_key=True)
    time = IntegerField()
    weight = FloatField()
