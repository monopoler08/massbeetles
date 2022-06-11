from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import relationship, backref
from models.base import Base


class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    notes = Column(String)
    genus_id = Column(ForeignKey("genera.id"))
    genus = relationship("Genus", backref=backref("species"))

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
        for ps in self.publications_species:
            author_string = f"{ps.publication.author.name} {ps.publication.year}"
            if not ps.original:
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
