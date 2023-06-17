from uuid import uuid4
import socket
import logging
from time import time, ctime

from flask import Flask, render_template, request, Response

import gesundheitstimer.database as db
from gesundheitstimer.log import log

app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True


@app.route("/", methods=["GET"])
def index():
    log.debug("Zeige webpage")

    measurements = list(db.Measurement.select().order_by(db.Measurement.time.desc()).limit(30).dicts())

    remaining, drunk = calculate_remaining_drunk(1000)

    return render_template("index.html", measurements=measurements, drunk=drunk, remaining=remaining)


def calculate_remaining_drunk(goal: int):
    drunk = 0
    prev = -100

    for measurement in db.Measurement.select().order_by(db.Measurement.time.desc()):
        # Skip only small changes
        if abs(measurement.weight - prev) < 1:
            continue

        if measurement.weight < prev:
            drunk += (prev - measurement.weight)

        prev = measurement.weight

    remaining = max(goal - drunk, 0)

    return remaining, drunk


@app.route("/api/datengeandert", methods=["POST"])
def data_change():
    log.debug(f"Ändere Daten von {request.remote_addr}")

    weight = float(request.form.get("gewicht", 0))

    if abs(weight) < 1:
        return Response(), 200
    if weight < 0:
        return Response(), 200

    db.Measurement.create(weight=weight, id=str(uuid4()), time=round(time(), 0))

    return Response(), 200


@app.template_filter('ctime')
def timectime(s):
    return ctime(s)


@app.route("/settings", methods=["GET"])
@app.route("/settings.html", methods=["GET"])
def settings():
    return render_template("settings.html")


def get_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    log.info(f"Starte Server auf {get_ip()}:5000")
    db.database.create_tables([db.Measurement])
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
