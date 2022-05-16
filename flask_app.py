from flask import Flask, render_template, request
from sqlalchemy import or_, func
from base import Session
from author import Author
from county import County
from family import Family
from genus import Genus
from publication import Publication, PublicationsSpecies
from record import Record
from source import Source
from species import Species
from state import State
from super_family import SuperFamily
from sub_order import SubOrder
from synonym import Synonym
from common_name import CommonName

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beetles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

session = Session()


@app.route("/")
def index():
    return render_template("server_table.html", title="MassBeetles")


@app.route("/api/data")
def data():
    total_records = session.query(Species).count()
    query = (
        session.query(Species)
        .join(Species.genus)
        .join(Species.records)
        .join(Genus.family)
    )

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            or_(
                Species.name.like(f"%{search}%"),
                Genus.name.like(f"%{search}%"),
                Source.name.like(f"%{search}%"),
                County.name.like(f"%{search}%"),
            )
        )
    total_filtered = query.group_by(Genus.name, Species.name).count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f"order[{i}][column]")
        if col_index is None:
            break
        col_name = request.args.get(f"columns[{col_index}][data]")
        if col_name not in ["species", "source", "state", "county"]:
            col_name = "species"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        if col_name == "species":
            col = getattr(Species, "name")
        elif col_name == "source":
            col = getattr(Source, "name")
        elif col_name == "county":
            col = getattr(County, "name")

        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        "data": [record.to_dict() for record in query],
        "recordsFiltered": total_filtered,
        "recordsTotal": total_records,
        "draw": request.args.get("draw", type=int),
    }


if __name__ == "__main__":
    app.run()
