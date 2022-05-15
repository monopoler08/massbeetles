from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import relationship, backref
from base import Base


class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    genus_id = Column(ForeignKey("genera.id"))
    genus = relationship("Genus", backref=backref("species"))

    def __init__(self, name, genus):
        self.name = name
        self.genus = genus

    def scientific_name(self):
        return f"{self.genus.name} {self.name}"

    def sci_name_with_author(self):
        basename = self.scientific_name()
        author_strings = []
        for ps in self.publications_species:
            author_string = f"{ps.publication.author.name} {ps.publication.year}"
            if not ps.original:
                author_string = "(" + author_string + ")"
            author_strings.append(author_string)

        return basename + " " + ", ".join(author_strings)

    def __repr__(self):
        return f"<Species name={self.name}, genus={self.genus.name}>"

    def to_dict(self):
        return {
            "scientific_name": self.sci_name_with_author(),
            "species": self.name,
            "genus": self.genus.name,
            "family": self.genus.family.name,
            "super_family": self.genus.family.super_family.name,
            "sub_order": self.genus.family.super_family.sub_order.name,
            "counties": ", ".join(set([record.county.name for record in self.records])),
            "state": "Massachusetts",
            "sources": ",".join(set([record.source.name for record in self.records])),
            "common_names": ", ".join(
                set([common_name.name for common_name in self.common_names])
            ),
            "synonyms": ", ".join(set([synonym.name for synonym in self.synonyms])),
        }
