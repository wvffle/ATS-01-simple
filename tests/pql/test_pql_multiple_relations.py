import pytest

from ats.pql.pql import parse_query


def test_relations_modifies_and_follows_star():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Modifies(20, w3) and Follows*(w3, s2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Follows*"


def test_relations_follows_and_modifies():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Follows(20, w3) and Modifies(w3, s2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Follows"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_parent_star_and_modifies():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Parent*(20, _) and Modifies(_, s2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent*"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_modifies_and_parent():
    result = parse_query(
        """
            while w3; stmt s4;
            Select w3 such that Modifies(20, w3) and Parent(w3, s4)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Parent"


def test_relations_modifies_and_uses():
    result = parse_query(
        """
            while w; stmt s4;
            Select w such that Modifies(329, w) and Uses(_, "hello")
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Uses"


def test_relations_uses_and_modifies():
    result = parse_query(
        """
            while w; stmt s4;
            Select w such that Uses(329, w) and Modifies(_, "hello")
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Uses"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_uses_and_modifies_not_valid_modifies():
    with pytest.raises(
        ValueError, match="Token 'Modyfikuje' is not a valid NAME_TOKEN"
    ):
        parse_query(
            """
            while w; stmt s4;
            Select w such that Uses(329, w) and Modyfikuje(_, "hello")
            """
        )


def test_relations_uses_and_modifies_not_valid_uses():
    with pytest.raises(ValueError, match="Token 'Use' is not a valid NAME_TOKEN"):
        parse_query(
            """
            while w; stmt s4;
            Select w such that Use(329, w) and Modifies(_, "hello")
            """
        )
