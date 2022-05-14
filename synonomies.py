from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Synonymy(Base):
    __tablename__ = "synonomies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(ForeignKey("species.id"))
    species = relationship("Species", backref=backref("synonomies"))

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"<Synonomy name={self.name} species={self.species.name}>"
