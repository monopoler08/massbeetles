from base import Session, engine, Base
from author import Author
from county import County
from family import Family
from genus import Genus
from record import Record
from source import Source
from species import Species
from state import State
from super_family import SuperFamily
from sub_order import SubOrder
import pandas as pd

Base.metadata.create_all(engine)

session = Session()


def add_dict_to_session(data):
    [session.add(item) for item in data.values()]


df = pd.read_csv("beetles.csv")[:-5]


ma = State(name="Massachusetts", abbreviation="MA")
session.add(ma)

counties = {county: County(name=county, state=ma) for county in County.ma_counties}
[session.add(county) for county in counties.values()]

# melt county info
non_county_columns = list(set(df.columns) - set(County.ma_counties))
df = df.melt(non_county_columns, var_name="County", value_name="Record Code").dropna(
    subset=["Record Code"]
)

# massage the author field and combine author+year for a source
df["Author"] = df["Author"].str.replace("[()]", "", regex=True)
df["Publication"] = df["Author"] + "(" + df["Year"].astype(str) + ")"
authors = {
    name: Author(name=name)
    for name in list(df["Author"].dropna().drop_duplicates().values)
}
add_dict_to_session(authors)

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
    row["Species"]: Species(name=row["Species"], genus=genera[row["Genus"]],)
    for row in df[["Species", "Genus"]].drop_duplicates().to_dict("records")
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
        "BG. iN",
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
        "iNat",
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
    )
}
add_dict_to_session(sources)

records = [
    Record(
        source=sources.get(
            code.strip(), Source(name=code, year=None, person=None, url=None)
        ),
        species=species[row["Species"]],
        county=counties[row["County"]],
        state=ma,
    )
    for row in df[["Species", "County", "Record Code"]]
    .drop_duplicates()
    .to_dict("records")
    for code in row["Record Code"].split(",")
    if code.strip()
]
[session.add(record) for record in records]

session.commit()
session.close()

