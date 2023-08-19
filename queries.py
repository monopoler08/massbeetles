from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import Session, aliased
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
import pandas as pd
import json

engine = create_engine("sqlite:///beetles.db")

with Session(engine) as session:
    #    species_records = (
    #        session.query(Record)
    #        .join(Record.species)
    #        .join(Species.genus)
    #        .join(Species.common_names, isouter=True)
    #        .join(Species.synonyms, isouter=True)
    #        .join(Genus.family)
    #        .join(Record.source)
    #        .join(Record.county, isouter=True)
    #        .order_by(Genus.name, Species.name)
    #    )

    record_county_subq = (
        select(
            Record.county_id.label("county_id"), Record.species_id.label("species_id")
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
                        Source.name,
                        "person",
                        Source.person,
                        "year",
                        Source.year,
                        "url",
                        Source.url,
                        "journal",
                        Source.journal,
                        "volume",
                        Source.volume,
                    )
                ),
            ).label("county_records")
        )
        .group_by(Record.species_id, Record.county_id)
    ).subquery()

    species_query = (
        select(Species.scientific_name())
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
    )

    for x in session.execute(species_query):
        print(x)
#        print(x[0].scientific_name(), json.dumps(json.loads(x[1]), indent=2))

#        print(
#            x.species.scientific_name(),
#            [cr.keys() for cr in json.loads(x.county_records)],
#        )
