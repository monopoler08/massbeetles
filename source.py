from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    person = Column(String)
    name = Column(String)
    url = Column(String)
    year = Column(Integer)

    def __init__(self, name, year, person, url):
        self.name = name
        self.year = year
        self.person = person
        self.url = url

    def __repr__(self):
        return f"<Source name={self.name} person={self.person} year={self.year} url={self.url}"
