from typing import List
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    super_family_id: Mapped[int] = mapped_column(ForeignKey("super_families.id"))
    super_family: Mapped["SuperFamily"] = relationship(back_populates="families")
    genera: Mapped[List["Genus"]] = relationship(back_populates="family")

    def __init__(self, name, super_family):
        self.name = name
        self.super_family = super_family

    def __repr__(self):
        return f"<Family name={self.name} super_family={self.super_family.name}>"
