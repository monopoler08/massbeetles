from flask import Flask, render_template, request, url_for
from sqlalchemy import select, or_, func, create_engine
from sqlalchemy.orm import Session
from models.author import Author
from models.county import County
from models.family import Family
from models.genus import Genus
from models.publication import Publication
from models.publications_species import PublicationsSpecies
from models.record import Record
from models.source import Source
from models.species import Species
from models.state import State
from models.super_family import SuperFamily
from models.sub_order import SubOrder
from models.synonym import Synonym
from models.common_name import CommonName, common_names_species_association
import pathlib
from datetime import datetime
import calendar

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beetles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

engine = create_engine("sqlite:///beetles.db")
session = Session(engine)


@app.route("/")
def index():
    modtime = datetime.fromtimestamp(pathlib.Path("beetles.db").stat().st_mtime)
    mtime = f"{calendar.month_name[modtime.month]} {modtime.day}, {modtime.year}"

    records = 3669
    species = 3329
    families = 96

    #    records = len(get_all_records())
    #    species = count_unique_species()
    #    families = len({record[0] for record in session.query(Family.name).all()})

    return render_template(
        "server_table.html",
        title="MassBeetles",
        records=records,
        species=species,
        families=families,
        mtime=mtime,
    )


def get_all_records():
    engine = create_engine("sqlite:///beetles.db")
    with Session(engine) as session:
        species_records = (
            session.query(Record)
            .join(Record.species)
            .join(Species.genus)
            .outerjoin(Species.common_names)
            .outerjoin(Species.synonyms)
            .join(Genus.family)
            .join(Record.source)
            .join(Record.county)
        )
        search = request.args.get("search[value]")
        if search:
            species_records = species_records.filter(
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

    return convert_records_to_species(species_records.all())

    # sorting

    while True:
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
                col = [func.lower(c).desc() for c in col]
            order.extend(col)
            i += 1

        if order:
            species_records = species_records.order_by(*order)


def convert_records_to_species(species_records):
    species_data = dict()
    for r in species_records:
        species = species_data.get(
            r.species.scientific_name(),
            {
                "species_name": r.species.name,
                "scientific_name": r.species.scientific_name(),
                "genus_name": r.species.genus.name,
                "family_name": r.species.genus.family.name,
                "common_names": [cn.name for cn in r.species.common_names],
                "synonyms": [sn.name for sn in r.species.synonyms],
                "county_records": dict(),
            },
        )
        if not r.county or r.county.abbreviation == "null":
            county_abbrev = "MASS"
            county_name = "Massachusetts"
        else:
            county_abbrev = r.county.abbreviation
            county_name = r.county.name

        county_records = species["county_records"].get(
            county_abbrev, {"county": r.county.name, "sources": []}
        )
        county_records["sources"].append(
            {
                "county_name": county_name,
                "name": r.source.name if r.source.name else "",
                "person": r.source.person if r.source.person else "",
                "year": r.source.year if r.source.year else "",
                "url": r.source.url if r.source.url else "",
                "journal": r.source.journal if r.source.journal else "",
                "volume": r.source.volume if r.source.volume else "",
            }
        )
        species["county_records"][county_abbrev] = county_records
        species_data[r.species.scientific_name()] = species

    return species_data.values()


def count_unique_species():
    """Species with an epitewhatever beginning with a 'sp.' don't count unless there are no other records for a genus"""
    species_count_by_genus = dict()
    sp_in_genus = dict()
    for record in get_all_records():
        if record["species_name"] != "sp.":
            species_count_by_genus[record["genus_name"]] = (
                species_count_by_genus.get(record["genus_name"], 0) + 1
            )
        else:
            sp_in_genus[record["genus_name"]] = 1

    base_count = sum(species_count_by_genus.values())
    additional_sp_count = sum(
        [
            value
            for key, value in sp_in_genus.items()
            if key not in species_count_by_genus.keys()
        ]
    )

    return base_count + additional_sp_count


# @app.route_old("/api/data")
# def data():
#     query = all_record_query()


#     # sorting
#     order = []
#     i = 0
#     while True:
#         col = []
#         col_index = request.args.get(f"order[{i}][column]")
#         if col_index is None:
#             if not order:
#                 col.append(getattr(Genus, "name"))
#                 col.append(getattr(Species, "name"))
#             break
#         col_name = request.args.get(f"columns[{col_index}][data]")
#         if col_name not in ["species", "genus", "family", "author"]:
#             col_name = "scientific_name"
#         descending = request.args.get(f"order[{i}][dir]") == "desc"
#         if col_name == "scientific_name":
#             col.append(getattr(Genus, "name"))
#             col.append(getattr(Species, "name"))
#         elif col_name == "genus":
#             col.append(getattr(Genus, "name"))
#         elif col_name == "family":
#             col.append(getattr(Family, "name"))

#         col = [func.lower(c) for c in col]
#         if descending:
#             col = [func.lower(c).desc() for c in col]
#         order.extend(col)
#         i += 1
#     if order:
#         query = query.order_by(*order)

#     # pagination
#     start = request.args.get("start", type=int)
#     length = request.args.get("length", type=int)
#     query = query.offset(start).limit(length)


@app.route("/api/data")
def data():
    species_records = get_all_records()
    total_records = len(species_records)

    #    species_data = convert_records_to_species(species_records)
    species_data = species_records
    total_filtered = "TBD"
    # response
    return {
        "data": [
            {
                "scientific_name": r["scientific_name"],
                "family": r["family_name"],
                "genus": r["genus_name"],
                "common_names": r["common_names"],
                "sources": [
                    source["name"]
                    for county, source_list in r["county_records"].items()
                    for source in source_list["sources"]
                ],
                "counties": [
                    county for county in r["county_records"].keys() if county != "state"
                ],
                "synonyms": r["synonyms"],
                "notes": "",
                "county_records": [
                    source
                    for county, source_list in r["county_records"].items()
                    for source in source_list["sources"]
                ],
            }
            for r in species_data
        ],
        "recordsFiltered": total_filtered,
        "recordsTotal": total_records,
        "draw": request.args.get("draw", type=int),
    }


if __name__ == "__main__":
    app.run()
