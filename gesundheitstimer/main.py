from uuid import uuid4
import socket
import logging
from time import time, ctime, sleep

from flask import Flask, render_template, request, Response, redirect

import gesundheitstimer.database as db
from gesundheitstimer.log import log

app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True


@app.route("/", methods=["GET"])
def index():
    log.debug("Zeige webpage")

    measurements = list(db.Measurement.select().order_by(db.Measurement.time.desc()).limit(30).dicts())

    # Target hardcoded for now
    remaining, drunk = calculate_remaining_drunk(1000)

    bottle_mass_setting = db.Setting.get(db.Setting.key == "bottle_mass")
    weight = float(bottle_mass_setting.value)

    if len(measurements) > 0:
        current = measurements[0]["weight"]
        if current == 0:
            current = measurements[1]["weight"]
        current = max(0, current - weight)
    else:
        current = None

    return render_template("index.html", measurements=measurements, drunk=drunk, remaining=remaining, current=current)


def calculate_remaining_drunk(goal: int):
    drunk = 0
    max_values = []
    prev_1_value = -100
    prev_2_value = -100
    last_time = 0

    measurements = db.Measurement.select().order_by(db.Measurement.time)
    for measurement in measurements:
        if prev_1_value > prev_2_value and prev_1_value > measurement.weight:
            max_values.append(prev_1_value)

        prev_2_value = prev_1_value
        prev_1_value = measurement.weight
        last_time = measurement.time

    now = time()
    if (now - last_time) > 1 and last_time != 0:
        max_values.append(prev_1_value)

    for i in range(1, len(max_values)):
        if (max_values[i] < max_values[i-1]) and max_values[i] > 5:
            drunk += max_values[i-1] - max_values[i]

    remaining = max(goal - drunk, 0)

    return remaining, drunk


last_value = 0


@app.route("/api/datengeandert", methods=["POST"])
def data_change():
    global last_value

    weight = float(request.form.get("gewicht", 0))

    # Skip same values
    if abs(last_value - weight) < 5:
        return Response(), 200
    last_value = weight

    # Special 0 values
    if abs(weight) < 1:
        weight = 0
    if weight < 0:
        weight = 0

    db.Measurement.create(weight=weight, id=str(uuid4()), time=time())

    log.debug(f"Gewicht {weight} von client {request.remote_addr}")
    return Response(), 200


@app.template_filter('ctime')
def timectime(s):
    return ctime(s)


@app.route("/api/alarm", methods=["POST"])
def alert():
    log.debug("Alarm gesetzt")

    alarm_setting = db.Setting.get(db.Setting.key == "alarm")
    alarm_setting.value = 1
    alarm_setting.save()

    return Response(), 200


@app.route("/api/menge", methods=["POST"])
def menge():
    goal_setting = db.Setting.get(db.Setting.key == "goal")

    log.debug(f"Menge auf {request.form.get('menge_ml', 0)} gesetz")

    goal_setting.value = str(request.form.get("menge_ml", 0))
    goal_setting.save()

    return Response(), 200


@app.route("/settings.html", methods=["GET"])
def settings():
    # TODO: show current value
    return render_template("settings.html")


@app.route("/set_weight", methods=["POST"])
def set_weight():
    weight = request.form.get("weight", 0)
    bottle_mass_setting = db.Setting.get(db.Setting.key == "bottle_mass")
    bottle_mass_setting.value = weight
    bottle_mass_setting.save()

    log.info(f"Setze Flaschen Inhalt auf {weight}")
    return redirect("/settings.html")


def get_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    log.info(f"Starte Server auf {get_ip()}:5000")

    db.database.create_tables([db.Measurement, db.Setting])
    sleep(1)

    if not db.Setting.select().where(db.Setting.key == "goal").exists():
        db.Setting.create(key="goal", value=1000)
    if not db.Setting.select().where(db.Setting.key == "bottle_mass").exists():
        db.Setting.create(key="bottle_mass", value=0)
    if not db.Setting.select().where(db.Setting.key == "alarm").exists():
        db.Setting.create(key="alarm", value=0)

    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
