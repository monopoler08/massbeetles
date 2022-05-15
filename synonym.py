from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Synonym(Base):
    __tablename__ = "synonyms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(ForeignKey("species.id"))
    species = relationship("Species", backref=backref("synonyms"))

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"<Synonym name={self.name} species={self.species.name}>"
