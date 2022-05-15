from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from base import Base


class PublicationsSpecies(Base):
    __tablename__ = "publications_species"
    id = Column(Integer, primary_key=True)
    original = Column(Integer)
    publication_id = Column(ForeignKey("publications.id"))
    species_id = Column(ForeignKey("species.id"))
    publication = relationship("Publication", backref=backref("publications_species"))
    species = relationship("Species", backref=backref("publications_species"))

    def __init__(self, original, publication, species):
        if not publication:
            raise (ValueError)
        self.original = original
        self.publication = publication
        self.species = species

    def __repr__(self):
        return f"<PublicationSpecies id={self.id} publication_id={self.publication_id} species_id={self.species_id}>"


class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    author_id = Column(ForeignKey("authors.id"))
    author = relationship("Author", backref=backref("publications"))

    def __init__(self, year, author):
        self.year = year
        self.author = author

    def __repr__(self):
        return f"<Publication author_id={self.author_id} year={self.year}>"
