from sqlalchemy.orm import Session
from models.base import Base
from models.author import Author
from models.county import County
from models.family import Family
from models.genus import Genus
from models.publication import Publication
from models.publications_species import PublicationsSpecies
from models.record import Record
from models.source import Source
from models.species import Species
from models.state import State
from models.super_family import SuperFamily
from models.sub_order import SubOrder
from models.synonym import Synonym
from models.common_name import CommonName
import pytest
from utils import count_unique_species


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="module")
def basic_data():
    sub_order = SubOrder(name="stub")
    super_family = SuperFamily(name="stub", sub_order=sub_order)
    family = Family(name="Platypus", super_family=super_family)
    genus = Genus(name="Platypus", family=family)
    species1 = Species(name="Awesomus", genus=genus, notes="interesting stuff")
    species2 = Species(name="sp.", genus=genus, notes="not sure what I was looking at")
    return [species1, species2]


@pytest.fixture(scope="module")
def record_sample():
    data = [
        {
            "scientific_name": "Trigonorhinus alternatus",
            "species": "alternatus",
            "genus": "Trigonorhinus",
            "family": "Anthribidae",
            "common_names": [],
            "synonyms": [],
            "counties": ["MASS"],
            "county_records": [{"MASS": ["DNA"]}],
            "notes": "common; found on weeds",
        },
        {
            "scientific_name": "Trigonorhinus rotundatus",
            "species": "rotundatus",
            "genus": "Trigonorhinus",
            "family": "Anthribidae",
            "common_names": [],
            "synonyms": ["Anthribulus"],
            "counties": ["MASS", "Middlesex"],
            "county_records": [
                {"MASS": ["DNA", "Bugguide", "TM"], "Middlesex": ["CJ"]}
            ],
            "notes": "found on huckleberry flowers",
        },
        {
            "scientific_name": "Trigonorhinus sp.",
            "species": "sp.",
            "genus": "Trigonorhinus",
            "family": "Anthribidae",
            "common_names": [],
            "synonyms": [],
            "counties": ["MASS"],
            "county_records": [{"MASS": ["Bugguide"]}],
            "notes": "",
        },
    ]
    return data


def test_common_name(basic_data):
    # I should really mock most of these
    species = basic_data[0]
    assert species.scientific_name() == "Platypus Awesomus"

    # should be able to do italicized name without author
    assert species.italicized_sci_name_with_author() == "<i>Platypus Awesomus</i>"

    # should not italicize sp.
    species.name = "sp."
    assert species.italicized_sci_name_with_author() == "<i>Platypus</i> sp."


def test_species_count(record_sample, mocker):
    mocker.patch("utils.get_all_records", return_value=record_sample)
    assert 2 == count_unique_species(None)
