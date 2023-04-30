from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    publications: Mapped[List["Publication"]] = relationship(back_populates="author")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Author {self.id=} {self.name=}>"
