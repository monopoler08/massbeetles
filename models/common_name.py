from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base

common_names_species_association = Table(
    "common_names_species",
    Base.metadata,
    Column("common_name_id", Integer, ForeignKey("common_names.id")),
    Column("species_id", Integer, ForeignKey("species.id")),
)


class CommonName(Base):
    __tablename__ = "common_names"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species = relationship(
        "Species", secondary=common_names_species_association, backref="common_names"
    )

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"<CommonName name={self.name}>"
