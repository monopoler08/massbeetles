from flask import Flask, render_template, request, url_for
from sqlalchemy import or_, func
from models.base import Session
from models.author import Author
from models.county import County
from models.family import Family
from models.genus import Genus
from models.publication import Publication, PublicationsSpecies
from models.record import Record
from models.source import Source
from models.species import Species
from models.state import State
from models.super_family import SuperFamily
from models.sub_order import SubOrder
from models.synonym import Synonym
from models.common_name import CommonName

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beetles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

session = Session()


@app.route("/")
def index():
    records = len(all_record_query().all())
    species = len({record[0] for record in session.query(Species.name).all()})
    families = len({record[0] for record in session.query(Family.name).all()})

    return render_template(
        "server_table.html",
        title="MassBeetles",
        records=records,
        species=species,
        families=families,
    )


def all_record_query():
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
    return query


@app.route("/api/data")
def data():
    query = all_record_query()
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

        col = [func.lower(c) for c in col]
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
