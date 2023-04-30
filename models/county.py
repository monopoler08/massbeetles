from typing import List
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


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

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    abbreviation: Mapped[str] = mapped_column(String)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"))
    state: Mapped["State"] = relationship(back_populates="counties")
    records: Mapped[List["Record"]] = relationship(back_populates="county")

    def __init__(self, name, abbreviation, state):
        self.name = name
        self.abbreviation = abbreviation
        self.state = state

    def __repr__(self):
        return f"<County name={self.name} abbrev={self.abbreviation} state={self.state.name}>"
