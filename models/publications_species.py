from typing import List
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class PublicationsSpecies(Base):
    __tablename__ = "publications_species"

    id: Mapped[int] = mapped_column(primary_key=True)
    original: Mapped[int] = mapped_column(Integer)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"))
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    publication: Mapped["Publication"] = relationship(
        back_populates="publications_species", viewonly=True
    )
    species: Mapped["Species"] = relationship(back_populates="publications_species")

    def __init__(self, original, publication, species):
        if not publication:
            raise (ValueError)
        self.original = original
        self.publication = publication
        self.species = species

    def __repr__(self):
        return f"<PublicationSpecies id={self.id} publication_id={self.publication_id} species_id={self.species_id}>"
