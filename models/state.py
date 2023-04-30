from typing import List
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    abbreviation: Mapped[str] = mapped_column(String[2])
    records: Mapped[List["Record"]] = relationship(back_populates="state")
    counties: Mapped[List["County"]] = relationship(back_populates="state")

    def __init__(self, name, abbreviation):
        self.name = name
        self.abbreviation = abbreviation

    def __repr__(self):
        return f"<State name={self.name}, name={self.abbreviation}>"
