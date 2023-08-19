from sqlalchemy import select, func, create_engine, MetaData
from sqlalchemy.orm import Session
from models.base import Base
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
import pandas as pd
import numpy as np

engine = create_engine("sqlite:///beetles.db", echo=True)
Base.metadata.create_all(engine)

session = Session(engine)


def add_dict_to_session(data):
    [session.add(item) for item in data.values()]


df = pd.read_csv("beetles.csv")
sources_df = pd.read_csv("sources.csv")

ma = State(name="Massachusetts", abbreviation="MA")
session.add(ma)

counties = {
    county["name"]: County(
        name=county["name"], abbreviation=county["abbreviation"], state=ma
    )
    for county in County.ma_counties
}
counties["MASS"] = County(name="Massachusetts", abbreviation="MASS", state=ma)
null_county = counties["MASS"]
[session.add(county) for county in counties.values()]

# massage the author field and combine author+year for a source
df["AuthorSimple"] = df["Author"].str.replace(r"[()]", "", regex=True)

authors = {
    name: Author(name=name)
    for name in df["AuthorSimple"].dropna().drop_duplicates().values.tolist()
}
add_dict_to_session(authors)

publications = {
    (row["AuthorSimple"], row["Year"]): Publication(
        year=row["Year"], author=authors[row["AuthorSimple"]]
    )
    for row in df[["AuthorSimple", "Year"]]
    .dropna()
    .drop_duplicates()
    .to_dict("records")
}
add_dict_to_session(publications)

sub_orders = {
    name: SubOrder(name=name)
    for name in list(df["Suborder"].dropna().drop_duplicates().values)
}
add_dict_to_session(sub_orders)

null_suborder = SubOrder(name="NA")
null_super_family = SuperFamily(name="NA", sub_order=null_suborder)

super_families = {
    row["Superfamily"]: SuperFamily(
        name=row["Superfamily"] if row["Superfamily"] else null_super_family,
        sub_order=sub_orders.get(row["Suborder"], null_suborder),
    )
    for row in df[["Superfamily", "Suborder"]].drop_duplicates().to_dict("records")
    if row["Superfamily"] == row["Superfamily"]
}
add_dict_to_session(super_families)

families = {
    row["Family"]: Family(
        name=row["Family"],
        super_family=super_families.get(row["Superfamily"], null_super_family),
    )
    for row in df[["Family", "Superfamily"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(families)

genera = {
    row["Genus"]: Genus(
        name=row["Genus"],
        family=families[row["Family"]],
    )
    for row in df[["Genus", "Family"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(genera)

species = {
    (row["Genus"], row["Species"]): Species(
        name=row["Species"],
        notes=row["Notes"],
        genus=genera[row["Genus"]],
    )
    for row in df[["Species", "Genus", "Notes"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(species)

sources = {
    source.Abbreviation: Source(
        name=source.Abbreviation,
        long_name=source.LongName,
        year=source.Date,
        person=source.Author,
        url=source.URL,
        journal=source.Journal,
        volume=source.Vol,
    )
    for source in list(
        sources_df.rename(
            columns={
                "Source Name": "LongName",
                "Vol/Pages": "Vol",
                "URL for display": "URL",
                "Source Code": "Abbreviation",
            }
        ).itertuples(index=False)
    )
}
add_dict_to_session(sources)

ma_counties = [c["name"] for c in County.ma_counties]
# county data
for row in df[["Genus", "Species"] + ma_counties].drop_duplicates().to_dict("records"):
    for county in ma_counties:
        if str(row[county]) == row[county]:
            for code in str(row[county]).split(","):
                if code.strip():
                    session.add(
                        Record(
                            source=sources.get(
                                code.strip(),
                                Source(
                                    name=code,
                                    long_name=None,
                                    year=None,
                                    person=None,
                                    url=None,
                                    journal=None,
                                    volume=None,
                                ),
                            ),
                            species=species[(row["Genus"], row["Species"])],
                            county=counties[county],
                            state=ma,
                        )
                    )

other_columns = ["MA", "Bugguide", "Tom Murray", "JFO"]
for row in (
    df[df[ma_counties].isnull().all(axis=1)][["Genus", "Species"] + other_columns]
    .drop_duplicates()
    .to_dict("records")
):
    for column in other_columns:
        if str(row[column]) == row[column]:
            for code in str(row[column]).split(","):
                if code.strip():
                    session.add(
                        Record(
                            source=sources.get(
                                code.strip(),
                                Source(
                                    name=code,
                                    long_name=None,
                                    year=None,
                                    person=None,
                                    url=None,
                                    journal=None,
                                    volume=None,
                                ),
                            ),
                            species=species[(row["Genus"], row["Species"])],
                            county=null_county,
                            state=ma,
                        )
                    )

publications_species = {}
for row in (
    df[["Author", "AuthorSimple", "Year", "Species", "Genus"]]
    .dropna()
    .drop_duplicates()
    .to_dict("records")
):
    original = 0
    # if we dropped any () from the author this means the species was renamed
    if row["Author"] == row["AuthorSimple"]:
        original = 1

    publication = publications[(row["AuthorSimple"], row["Year"])]
    if publication is None:
        print(f'Error: {row["Author"]} {row["Year"]} {row["Genus"]} {row["Species"]}')
    else:
        publications_species[
            (row["AuthorSimple"], row["Year"], row["Genus"], row["Species"])
        ] = PublicationsSpecies(
            original=original,
            publication=publication,
            species=species[(row["Genus"], row["Species"])],
        )

# add_dict_to_session(publications_species)

synonyms = [
    Synonym(name=synonym.strip(), species=species[(row["Genus"], row["Species"])])
    for row in df[["Genus", "Species", "Synonyms"]]
    .dropna()
    .drop_duplicates()
    .to_dict("records")
    for synonym in row["Synonyms"].split(",")
]
[session.add(synonym) for synonym in synonyms]

common_names = [
    CommonName(
        name=row["Common Name"], species=[species[(row["Genus"], row["Species"])]]
    )
    for row in df[["Genus", "Species", "Common Name"]]
    .dropna()
    .drop_duplicates()
    .to_dict("records")
]
[session.add(common_name) for common_name in common_names]


session.commit()
session.close()
