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
    query = (
        session.query(Species)
        .join(Species.genus)
        .join(Species.records)
        .outerjoin(Species.synonyms)
        .outerjoin(Species.common_names)
        .outerjoin(Record.county)
        .outerjoin(Record.source)
        .join(Genus.family)
        .outerjoin(Species.publications_species)
        .outerjoin(PublicationsSpecies.publication)
        .outerjoin(Publication.author)
        .group_by(Species)
    )
    total_records = query.count()

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            or_(
                Species.name.like(f"%{search}%"),
                Genus.name.like(f"%{search}%"),
                Source.name.like(f"%{search}%"),
                County.name.like(f"%{search}%"),
                Family.name.like(f"%{search}%"),
                Synonym.name.like(f"%{search}%"),
                Source.name.like(f"%{search}%"),
                Species.notes.like(f"%{search}%"),
                CommonName.name.like(f"%{search}%"),
            )
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col = []
        col_index = request.args.get(f"order[{i}][column]")
        if col_index is None:
            if not order:
                col.append(getattr(Genus, "name"))
                col.append(getattr(Species, "name"))
            break
        col_name = request.args.get(f"columns[{col_index}][data]")
        if col_name not in ["species", "genus", "family", "author"]:
            col_name = "scientific_name"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        if col_name == "scientific_name":
            col.append(getattr(Genus, "name"))
            col.append(getattr(Species, "name"))
        elif col_name == "genus":
            col.append(getattr(Genus, "name"))
        elif col_name == "family":
            col.append(getattr(Family, "name"))

        if descending:
            col = [c.desc() for c in col]
        order.extend(col)
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
