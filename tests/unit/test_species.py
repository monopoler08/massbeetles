from models.base import Session
from models.author import Author
from models.county import County
from models.family import Family
from models.genus import Genus
from models.publication import Publication, PublicationsSpecies
from models.record import Record
from models.source import Source
from models.species import Species
from models.state import State
from models.super_family import SuperFamily
from models.sub_order import SubOrder
from models.synonym import Synonym
from models.common_name import CommonName


def test_common_name():
    # I should really mock most of these
    sub_order = SubOrder(name="stub")
    super_family = SuperFamily(name="stub", sub_order=sub_order)
    family = Family(name="Platypus", super_family=super_family)
    genus = Genus(name="Platypus", family=family)
    species = Species(name="Awesomus", genus=genus, notes="interesting stuff")
    assert species.scientific_name() == "Platypus Awesomus"

    # should be able to do italicized name without author
    assert species.italicized_sci_name_with_author() == "<i>Platypus Awesomus</i>"

    # should not italicize sp.
    species.name = "sp."
    assert species.italicized_sci_name_with_author() == "<i>Platypus</i> sp."
