from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class County(Base):
    ma_counties = [
        "Barnstable",
        "Berkshire",
        "Bristol",
        "Dukes",
        "Essex",
        "Franklin",
        "Hampden",
        "Hampshire",
        "Middlesex",
        "Nantucket",
        "Norfolk",
        "Plymouth",
        "Suffolk",
        "Worcester",
    ]
    __tablename__ = "counties"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state_id = Column(ForeignKey("states.id"))
    state = relationship("State", backref=backref("county", uselist=False))

    def __init__(self, name, state):
        self.name = name
        self.state = state

    def __repr__(self):
        return f"<County name={self.name} state={self.state.name}>"
