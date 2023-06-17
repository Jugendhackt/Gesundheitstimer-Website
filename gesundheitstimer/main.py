from flask import Flask
import gesundheitstimer.database as db

app = Flask(__name__)


@app.route("/api/new_data")
def test():
    return "hi"


def main():
    db.database.create_tables([db.Measurement])
    app.run(host="0.0.0.0")


