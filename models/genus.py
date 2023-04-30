from typing import List
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Genus(Base):
    __tablename__ = "genera"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    family: Mapped["Family"] = relationship(back_populates="genera")
    species: Mapped[List["Species"]] = relationship(back_populates="genus")

    def __init__(self, name, family):
        self.name = name
        self.family = family

    def __repr__(self):
        return f"<Genus name={self.name}, family={self.family.name}>"
