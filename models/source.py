from typing import List
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    person: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    journal: Mapped[str] = mapped_column(String, nullable=True)
    volume: Mapped[str] = mapped_column(String, nullable=True)
    records: Mapped["Record"] = relationship(back_populates="source")

    def __init__(self, name, year, person, url, journal, volume):
        self.name = name
        self.year = year
        self.person = person
        self.url = url
        self.journal = journal
        self.volume = volume

    def __repr__(self):
        return f"<Source name={self.name} person={self.person} year={self.year} url={self.url}"
