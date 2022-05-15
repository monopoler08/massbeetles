from sqlalchemy import select, func
from base import Session
from author import Author
from county import County
from family import Family
from genus import Genus
from record import Record
from source import Source
from species import Species
from publication import Publication, PublicationsSpecies
from state import State
from super_family import SuperFamily
from sub_order import SubOrder

from sqlalchemy.orm import configure_mappers

session = Session()
configure_mappers()

statement = (
    select(
        Genus.name,
        Species.name,
        Source.name,
        County.name,
        PublicationsSpecies.original,
        Author.name,
        Publication.year,
    )
    .select_from(Record)
    .join(Record.species)
    .join(Species.genus)
    .join(Record.source)
    .join(Record.county)
    .join(Species.publications_species)
    .join(PublicationsSpecies.publication)
    .join(Publication.author)
    .order_by(Genus.name, Species.name, Source.name, County.name)
)

# for row in session.execute(statement):
#    print(row)

for record in session.query(Record).all():
    print(record.species.sci_name_with_author())
