from base import Session, engine, Base
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
import pandas as pd
import numpy as np

Base.metadata.create_all(engine)

session = Session()


def add_dict_to_session(data):
    [session.add(item) for item in data.values()]


df = pd.read_csv("beetles.csv")

ma = State(name="Massachusetts", abbreviation="MA")
session.add(ma)

counties = {county: County(name=county, state=ma) for county in County.ma_counties}
counties["null"] = County(name="null", state=ma)
null_county = counties["null"]
[session.add(county) for county in counties.values()]

# massage the author field and combine author+year for a source
df["AuthorSimple"] = df["Author"].str.replace(r"[()]", "", regex=True)
authors = {
    name: Author(name=name)
    for name in list(df["AuthorSimple"].dropna().drop_duplicates().values)
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
super_families = {
    row["Superfamily"]: SuperFamily(
        name=row["Superfamily"],
        sub_order=sub_orders.get(row["Suborder"], null_suborder),
    )
    for row in df[["Superfamily", "Suborder"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(super_families)

null_super_family = SuperFamily(name="NA", sub_order=null_suborder)
families = {
    row["Family"]: Family(
        name=row["Family"],
        super_family=super_families.get(row["Superfamily"], null_super_family),
    )
    for row in df[["Family", "Superfamily"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(families)

genera = {
    row["Genus"]: Genus(name=row["Genus"], family=families[row["Family"]],)
    for row in df[["Genus", "Family"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(genera)

species = {
    (row["Genus"], row["Species"]): Species(
        name=row["Species"], notes=row["Notes"], genus=genera[row["Genus"]],
    )
    for row in df[["Species", "Genus", "Notes"]].drop_duplicates().to_dict("records")
}
add_dict_to_session(species)

sources = {
    code: Source(name=code, year=None, person=None, url=None)
    for code in (
        "BG",
        "MCZ",
        "TKH",
        "iN",
        "KM",
        "JFO",
        "PB",
        "VV",
        "RN",
        "GAB",
        "SB",
        "JWG",
        "CJ",
        "DCR",
        "JMC",
        "xx",
        "TS",
        "PM",
        "NAPPO",
        "FFP",
        "BZ",
        "GS",
        "TM",
        "MBF",
        "KC",
        "MP",
        "G/S",
        "WTB",
        "IN",
        "CE",
        "RG",
        "AK",
        "JSR",
        "FB",
        "SG",
        "IDT",
        "CAF",
        "JAY",
        "BD",
        "TC",
        "HD",
        "LS",
        "JW",
        "CM",
        "AR",
        "TM",
    )
}
add_dict_to_session(sources)

# county data
for row in (
    df[["Genus", "Species"] + County.ma_counties].drop_duplicates().to_dict("records")
):
    for county in County.ma_counties:
        if str(row[county]) == row[county]:
            for code in str(row[county]).split(","):
                if code.strip():
                    session.add(
                        Record(
                            source=sources.get(
                                code.strip(),
                                Source(name=code, year=None, person=None, url=None),
                            ),
                            species=species[(row["Genus"], row["Species"])],
                            county=counties[county],
                            state=ma,
                        )
                    )

other_columns = ["MA", "Bugguide", "Tom Murray", "JFO"]
for row in (
    df[["Genus", "Species"] + other_columns].drop_duplicates().to_dict("records")
):
    for column in other_columns:
        if str(row[column]) == row[column]:
            for code in str(row[column]).split(","):
                if code.strip():
                    session.add(
                        Record(
                            source=sources.get(
                                code.strip(),
                                Source(name=code, year=None, person=None, url=None),
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

    publications_species[
        (row["AuthorSimple"], row["Year"], row["Genus"], row["Species"])
    ] = PublicationsSpecies(
        original=original,
        publication=publications[(row["AuthorSimple"], row["Year"])],
        species=species[(row["Genus"], row["Species"])],
    )

add_dict_to_session(publications_species)

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

