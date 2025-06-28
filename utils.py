from sqlalchemy import select, func, or_
from sqlalchemy.orm import scoped_session
import json

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
from models.common_name import CommonName
from database import SessionLocal, engine

session = SessionLocal()


def county_sort(a):
    if a["county_name"] == "Massachusetts":
        return "ZZZZZZZZZZ"
    else:
        return a["county_name"]


def get_all_records(args=None):
    #    with SessionLocal as session:
    record_county_subq = (
        select(
            Record.county_id.label("county_id"),
            Record.species_id.label("species_id"),
        )
        .join(Record.source)
        .join(Record.county, isouter=True)
        .add_columns(
            func.json_object(
                County.abbreviation,
                func.json_group_array(
                    func.json_object(
                        "county_name",
                        County.name,
                        "name",
                        func.ifnull(Source.name, ""),
                        "long_name",
                        func.ifnull(Source.long_name, ""),
                        "person",
                        func.ifnull(Source.person, ""),
                        "year",
                        func.ifnull(Source.year, ""),
                        "url",
                        func.ifnull(Source.url, ""),
                        "journal",
                        func.ifnull(Source.journal, ""),
                        "volume",
                        func.ifnull(Source.volume, ""),
                    )
                ),
            ).label("county_records")
        )
        .group_by(Record.species_id, Record.county_id)
    ).subquery()

    species_records = (
        select(Species)
        .join(record_county_subq, record_county_subq.c.species_id == Species.id)
        .group_by(record_county_subq.c.species_id)
        .add_columns(
            ("[" + func.group_concat(record_county_subq.c.county_records) + "]").label(
                "county_records"
            )
        )
        .join(Species.genus)
        .join(Species.common_names, isouter=True)
        .join(Species.synonyms, isouter=True)
        .join(Genus.family)
    )

    sort_species = False
    sort_genus = False
    order = []
    if args:
        #                   Source.name.like(f"%{search}%"),
        #                   County.name.like(f"%{search}%"),
        if args.get("search[value]"):
            species_records = species_records.filter(
                or_(
                    Species.name.like(f"%{search}%"),
                    Genus.name.like(f"%{search}%"),
                    Family.name.like(f"%{search}%"),
                    Synonym.name.like(f"%{search}%"),
                    Source.name.like(f"%{search}%"),
                    Species.notes.like(f"%{search}%"),
                    CommonName.name.like(f"%{search}%"),
                )
            )

        # sorting
        i = 0
        while True:
            col = []
            col_index = args.get(f"order[{i}][column]")
            if col_index is None:
                if not order:
                    col.append(getattr(Genus, "name"))
                    col.append(getattr(Species, "name"))
                break
            col_name = args.get(f"columns[{col_index}][data]")

            if col_name not in ["species", "genus", "family", "author"]:
                col_name = "scientific_name"

            descending = args.get(f"order[{i}][dir]") == "desc"

            if col_name == "scientific_name":
                col.append(getattr(Genus, "name"))
                col.append(getattr(Species, "name"))
                sort_genus = True
                sort_species = True
            elif col_name == "genus":
                col.append(getattr(Genus, "name"))
                sort_genus = True
            elif col_name == "family":
                col.append(getattr(Family, "name"))

            col = [func.lower(c) for c in col]

            if descending:
                col = [func.lower(c).desc() for c in col]
            order.extend(col)
            i += 1

    if not sort_genus:
        order.append(func.lower(getattr(Genus, "name")))

    if not sort_species:
        order.append(func.lower(getattr(Species, "name")))

    species_records = species_records.order_by(*order)

    data = [
        {
            "scientific_name": row[0].scientific_name(),
            "scientific_name_display": row[0].italicized_sci_name_with_author(),
            "species": row[0].name,
            "genus": row[0].genus.name,
            "family": row[0].genus.family.name,
            "common_names": [cn.name for cn in row[0].common_names],
            "synonyms": [sn.name for sn in row[0].synonyms],
            "counties": list(
                {
                    county
                    for x in json.loads(row[1])
                    for county in x.keys()
                    if county != "MASS"
                }
            ),
            "sources": list(
                {
                    source["name"]
                    for county_sources in json.loads(row[1])
                    for sources in county_sources.values()
                    for source in sources
                }
            ),
            "county_records": [
                source
                for county_sources in json.loads(row[1])
                for sources in county_sources.values()
                for source in sources
            ],
            "notes": row[0].notes,
        }
        for row in session.execute(species_records)
    ]
    for row in data:
        if row["counties"]:
            row["counties"].sort()
        if row["sources"]:
            row["sources"].sort()
        # hack, FIXME. Remove duplicates from the query
        if row["county_records"]:
            temp = [dict(x) for x in {tuple(x.items()) for x in row["county_records"]}]
            row["county_records"] = temp
            row["county_records"].sort(key=lambda x: x["name"])
            row["county_records"].sort(key=county_sort)

    return data


def count_unique_species(args):
    """Species with an epitewhatever beginning with a 'sp.' don't count unless there are no other records for a genus"""
    species_count_by_genus = dict()
    sp_in_genus = dict()
    for record in get_all_records(args):
        if record["species"] != "sp.":
            species_count_by_genus[record["genus"]] = (
                species_count_by_genus.get(record["genus"], 0) + 1
            )
        else:
            sp_in_genus[record["genus"]] = 1

    base_count = sum(species_count_by_genus.values())
    additional_sp_count = sum(
        [
            value
            for key, value in sp_in_genus.items()
            if key not in species_count_by_genus.keys()
        ]
    )
