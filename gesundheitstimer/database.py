from peewee import SqliteDatabase, Model, IntegerField, TextField

database = SqliteDatabase('../database.db')


class BaseModel(Model):
    class Meta:
        database = database


class Measurement(BaseModel):
    id = TextField(primary_key=True)
    weight = IntegerField()
    time = IntegerField()
