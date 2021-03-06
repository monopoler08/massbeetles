from sqlalchemy import select, func
from models.base import Session
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
from sqlalchemy.orm import configure_mappers

session = Session()
configure_mappers()

df = pd.read_csv("beetles.csv")

csv_species_list = set(df["Scientific Name"].values.tolist())

db_species = (
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

db_species_list = set([species.scientific_name() for species in db_species])

difflist = list(csv_species_list - db_species_list)

difflist.sort()
print(difflist)
print(df[["Family", "Scientific Name"]][df["Scientific Name"].isin(difflist)])

gcount = { count_tuple[0]:count_tuple[1] for count_tuple in session.query(Genus.name,func.count(Species.genus)).join(Species.genus).group_by(Genus.name).all() }

gcount_sp_only = { count_tuple[0]:count_tuple[1] for count_tuple in session.query(Genus.name,func.count(Species.genus)).join(Species.genus).filter(Species.name.in_(['sp.'])).group_by(Genus.name).all() }

total = 0
for genus in gcount.keys():
    if gcount[genus] == gcount_sp_only.get(genus,0):
        gcount[genus] = 1
    else:
        gcount[genus] = gcount[genus] - gcount_sp_only.get(genus,0)
    total = total + gcount[genus]
    print(f'{genus},{gcount[genus]}')

print(total)
