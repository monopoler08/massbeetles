from sqlalchemy import select, func, create_engine
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
import pandas as pd
import json

engine = create_engine("sqlite:///beetles.db")

csv = pd.read_csv("beetles.csv")

for row in csv[["Species", "Genus"]].drop_duplicates().to_dict("records"):
    with Session(engine) as session:
        species = (
            session.query(Species)
            .join(Species.genus)
            .where(Species.name == row["Species"])
            .where(Genus.name == row["Genus"])
        ).all()
        if not species:
            print(row["Genus"], row["Species"])

with Session(engine) as session:
    all_species = {x.scientific_name() for x in session.query(Species).all()}

    species_records = (
        session.query(Record)
        .join(Record.species)
        .join(Species.genus)
        .join(Species.common_names, isouter=True)
        .join(Species.synonyms, isouter=True)
        .join(Genus.family)
        .join(Record.source)
        .join(Record.county, isouter=True)
        .order_by(Genus.name, Species.name)
    )

    species_data = dict()
    for r in species_records:
        species = species_data.get(
            r.species.scientific_name(),
            {
                "name": r.species.scientific_name(),
                "genus": r.species.genus.name,
                "family": r.species.genus.family.name,
                "common_names": [cn.name for cn in r.species.common_names],
                "synonyms": [sn.name for sn in r.species.synonyms],
                "county_records": dict(),
            },
        )
        if not r.county or r.county.name == "null":
            county_name = "Statewide"
        else:
            county_name = r.county.name

        county_records = species["county_records"].get(county_name, [])
        county_records.append(
            {
                "name": r.source.name,
                "person": r.source.person,
                "year": r.source.year,
                "url": r.source.url,
                "journal": r.source.journal,
                "volume": r.source.volume,
            }
        )
        species["county_records"][county_name] = county_records
        species_data[r.species.scientific_name()] = species

    for s, d in species_data.items():
        if len(d["county_records"].keys()) > 1:
            print(s, d["county_records"])

        #    for i in all_species:
        #        if i not in species_data.keys():
        #            print(i)

#    mapped_species = {i for i in species_data.keys()}

#    print(len(mapped_species))
#    print(len(all_species))

#    for i in all_species:
#        if i not in mapped_species:
#            print(i)
