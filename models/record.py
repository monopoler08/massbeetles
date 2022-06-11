from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)
    species_id = Column(ForeignKey("species.id"))
    species = relationship("Species", backref=backref("records"))
    source_id = Column(ForeignKey("sources.id"))
    source = relationship("Source", backref=backref("records"))
    county_id = Column(ForeignKey("counties.id"))
    county = relationship("County", backref=backref("records"))
    state_id = Column(ForeignKey("states.id"))
    state = relationship("State", backref=backref("record", uselist=False))

    def __init__(self, species, source, county, state):
        self.species = species
        self.source = source
        self.county = county
        self.state = state

    def __repr__(self):
        return f"<Record species={self.species.scientific_name()}, source={self.source.name}, county={self.county.name if self.county else None}>"

