from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from base import Base

authors_publications_association = Table(
    "authors_publications",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors.id")),
    Column("publication_id", Integer, ForeignKey("publications.id")),
)

publications_species_association = Table(
    "publications_species",
    Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id")),
    Column("species_id", Integer, ForeignKey("species.id")),
)


class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    authors = relationship(
        "Author", secondary=authors_publications_association, backref="publications"
    )
    species = relationship(
        "Species", secondary=publications_species_association, backref="publications"
    )

    def __init__(self, name, year):
        self.name = name
        self.year = year

    def __repr__(self):
        return f"<Author name={self.name} year={self.year}>"
