from typing import List
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    year: Mapped[int] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="publications")
    species: Mapped[List["Species"]] = relationship(
        back_populates="publications", secondary="publications_species", viewonly=True
    )
    publications_species: Mapped["PublicationsSpecies"] = relationship(
        back_populates="publication", viewonly=True
    )

    def __init__(self, year, author):
        self.year = year
        self.author = author

    def __repr__(self):
        return f"<Publication author={self.author.name} year={self.year}>"
