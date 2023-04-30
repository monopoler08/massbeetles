from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Synonym(Base):
    __tablename__ = "synonyms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    species: Mapped["Species"] = relationship(back_populates="synonyms")

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"<Synonym name={self.name} species={self.species.name}>"
