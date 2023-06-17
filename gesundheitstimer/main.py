from uuid import uuid4

from flask import Flask, render_template, request, Response
import gesundheitstimer.database as db

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def main():
    db.database.create_tables([db.Measurement])
    app.run(host="0.0.0.0")


