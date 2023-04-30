from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base

common_names_species_association = Table(
    "common_names_species",
    Base.metadata,
    Column("common_name_id", Integer, ForeignKey("common_names.id"), primary_key=True),
    Column("species_id", Integer, ForeignKey("species.id"), primary_key=True),
)


class CommonName(Base):
    __tablename__ = "common_names"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    species: Mapped[List["Species"]] = relationship(
        secondary="common_names_species",
        back_populates="common_names",
    )

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"<CommonName name={self.name}>"
