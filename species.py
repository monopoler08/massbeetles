from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    genus_id = Column(ForeignKey("genera.id"))
    genus = relationship("Genus", backref=backref("species"))

    def __init__(self, name, genus):
        self.name = name
        self.genus = genus

    def scientific_name(self):
        return f"{self.genus.name} {self.name}"

    def __repr__(self):
        return f"<Species name={self.name}, genus={self.genus.name}>"

