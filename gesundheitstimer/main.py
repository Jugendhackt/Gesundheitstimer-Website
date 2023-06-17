from uuid import uuid4
import socket
import logging

from flask import Flask, render_template, request, Response

import gesundheitstimer.database as db
from gesundheitstimer.log import log

app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True


@app.route("/", methods=["GET"])
def index():
    log.debug("Zeige webpage")
    measurements = list(db.Measurement.select().limit(10).dicts())
    return render_template("index.html", measurements=measurements)


@app.route("/api/datengeandert", methods=["POST"])
def data_change():
    log.debug(f"Ändere Daten von {request.remote_addr}")

    weight = request.form.get("gewicht")
    time = request.form.get("zeit")
    db.Measurement.create(weight=weight, id=str(uuid4()), time=time)

    return Response(), 200


def get_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    log.info(f"Starte Server auf {get_ip()}:5000")
    db.database.create_tables([db.Measurement])
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
