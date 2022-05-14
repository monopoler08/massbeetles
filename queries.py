from sqlalchemy import select, func
from base import Session
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

session = Session()
statement = (
    select(Genus.name, Species.name, Source.name, County.name)
    .select_from(Record)
    .join(Record.species)
    .join(Species.genus)
    .join(Record.source)
    .join(Record.county)
    .order_by(Genus.name, Species.name, Source.name, County.name)
)


for row in session.execute(statement):
    print(row)
