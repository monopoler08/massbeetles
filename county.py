from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class County(Base):
    ma_counties = [
        {"name": "Barnstable", "abbreviation": "BA"},
        {"name": "Berkshire", "abbreviation": "BE"},
        {"name": "Bristol", "abbreviation": "BR"},
        {"name": "Dukes", "abbreviation": "DU"},
        {"name": "Essex", "abbreviation": "ES"},
        {"name": "Franklin", "abbreviation": "FR"},
        {"name": "Hampden", "abbreviation": "HD"},
        {"name": "Hampshire", "abbreviation": "HS"},
        {"name": "Middlesex", "abbreviation": "MI"},
        {"name": "Nantucket", "abbreviation": "NA"},
        {"name": "Norfolk", "abbreviation": "NO"},
        {"name": "Plymouth", "abbreviation": "PL"},
        {"name": "Suffolk", "abbreviation": "SU"},
        {"name": "Worcester", "abbreviation": "WO"},
    ]
    __tablename__ = "counties"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbreviation = Column(String)
    state_id = Column(ForeignKey("states.id"))
    state = relationship("State", backref=backref("county", uselist=False))

    def __init__(self, name, abbreviation, state):
        self.name = name
        self.abbreviation = abbreviation
        self.state = state

    def __repr__(self):
        return f"<County name={self.name} abbrev={self.abbreviation} state={self.state.name}>"

