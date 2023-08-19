import json
from flask import Flask, render_template, request
from sqlalchemy.orm import scoped_session
from database import SessionLocal, engine
from models.family import Family
import pathlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import calendar
from utils import get_all_records, count_unique_species

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beetles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.session = scoped_session(SessionLocal)


@app.route("/")
def index():
    modtime = (
        datetime.fromtimestamp(pathlib.Path("beetles.db").stat().st_mtime)
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("US/Eastern"))
    )
    mtime = f"{calendar.month_name[modtime.month]} {modtime.day}, {modtime.year}"

    records = 3669
    species = 3329
    families = 96

    records = len(get_all_records(request.args))
    species = count_unique_species(request.args)
    families = len({record[0] for record in app.session.query(Family.name).all()})

    return render_template(
        "server_table.html",
        title="MassBeetles",
        records=records,
        species=species,
        families=families,
        mtime=mtime,
    )


@app.route("/api/data")
def data():
    total_records = len(get_all_records())
    species_records = get_all_records(request.args)
    total_filtered = len(species_records)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)

    return {
        "data": species_records,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_records,
        "draw": request.args.get("draw", type=int),
    }


if __name__ == "__main__":
    app.run()
