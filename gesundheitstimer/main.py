from uuid import uuid4

from flask import Flask, render_template, request, Response
import gesundheitstimer.database as db

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    measurements = list(db.Measurement.select().limit(10).dicts())
    return render_template("index.html", measurements=measurements)


@app.route("/api/datengeaendert", methods=["POST"])
def data_change():
    weight = request.form.get("gewicht")
    time = request.form.get("zeit")
    db.Measurement.create(weight=weight, id=str(uuid4()), time=time)

    return Response(), 200


def main():
    db.database.create_tables([db.Measurement])
    app.run(host="0.0.0.0")
