from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    species: Mapped["Species"] = relationship(back_populates="records")
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship(back_populates="records")
    county_id: Mapped[int] = mapped_column(ForeignKey("counties.id"))
    county: Mapped["County"] = relationship(back_populates="records")
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"))
    state: Mapped["State"] = relationship(back_populates="records")

    def __init__(self, species, source, county, state):
        self.species = species
        self.source = source
        self.county = county
        self.state = state

    def __repr__(self):
        return f"<Record species={self.species.scientific_name()}, source={self.source.name}, county={self.county.name if self.county else None}>"
