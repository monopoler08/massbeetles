from typing import List
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    genus_id: Mapped[int] = mapped_column(ForeignKey("genera.id"))
    genus: Mapped["Genus"] = relationship(back_populates="species")
    publications: Mapped[List["Publication"]] = relationship(
        back_populates="species", secondary="publications_species", viewonly=True
    )
    records: Mapped[List["Record"]] = relationship(back_populates="species")
    synonyms: Mapped[List["Synonym"]] = relationship(back_populates="species")
    publications_species: Mapped["PublicationsSpecies"] = relationship(
        back_populates="species", viewonly=True
    )
    common_names: Mapped[List["CommonName"]] = relationship(
        secondary="common_names_species", back_populates="species", viewonly=True
    )

    def __init__(self, name, genus, notes):
        self.name = name
        self.genus = genus
        self.notes = notes

    def scientific_name(self):
        return f"{self.genus.name} {self.name}"

    def italicized_sci_name_with_author(self):
        basename = "<i>" + self.genus.name
        if self.name == "sp.":
            basename = basename + "</i> " + self.name
        else:
            basename = basename + " " + self.name + "</i>"
        author_strings = []
        for pub in self.publications:
            author_string = f"{pub.author.name} {pub.year}"
            if not pub.original:
                author_string = "(" + author_string + ")"
            author_strings.append(author_string)

        if author_strings:
            basename = basename + " " + ", ".join(author_strings)

        return basename

    def __repr__(self):
        return f"<Species name={self.name}, genus={self.genus.name}>"

    def to_dict(self):
        source_list = list(set([record.source.name for record in self.records]))
        source_list.sort()
        synonym_list = list(set([synonym.name for synonym in self.synonyms]))
        synonym_list.sort()
        county_list = list(
            set(
                [
                    record.county.abbreviation
                    for record in self.records
                    if record.county.abbreviation != "null"
                ]
            )
        )
        county_list.sort()
        common_names_list = list(
            set([common_name.name for common_name in self.common_names])
        )
        common_names_list.sort()
        return {
            "family": self.genus.family.name,
            "scientific_name": self.italicized_sci_name_with_author(),
            "common_names": ", ".join(common_names_list),
            "species": self.name,
            "genus": "<i>" + self.genus.name + "</i>",
            "super_family": self.genus.family.super_family.name,
            "sub_order": self.genus.family.super_family.sub_order.name,
            "counties": ", ".join(county_list),
            "state": "Massachusetts",
            "sources": ",".join(source_list),
            "synonyms": ", ".join(synonym_list),
            "notes": self.notes,
        }
