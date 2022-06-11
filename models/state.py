from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base


class State(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbreviation = Column(String)

    def __init__(self, name, abbreviation):
        self.name = name
        self.abbreviation = abbreviation

    def __repr__(self):
        return f"<State name={self.name}, name={self.abbreviation}>"
