import pytest

from ats.pql.pql import parse_query


def test_relations_modifies_and_follows_star():
    result = parse_query(
        """
            while w3; stmt s2; variable v;
            Select w3 such that Modifies(s2, v) and Follows*(w3, s2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Follows*"


def test_relations_follows_and_modifies():
    result = parse_query(
        """
            while w3; stmt s2; procedure p; variable v;
            Select w3 such that Follows(20, w3) and Modifies(s2, v)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Follows"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_parent_star_and_modifies():
    result = parse_query(
        """
            while w3; stmt s2; variable v;
            Select w3 such that Parent*(20, _) and Modifies(s2, v)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent*"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_parent_and_follows():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Parent(20, _) and Follows(_, s2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Follows"


def test_relations_follows_star_and_next_and_modifies():
    result = parse_query(
        """
            while w3; stmt s2; variable v;
            Select w3 such that Follows*(20, _) and Next(_, _) and Modifies(s2, v)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Follows*"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Next"
    assert result[0]["conditions"]["relations"][2]["relation"] == "Modifies"


def test_relations_modifies_and_parent():
    result = parse_query(
        """
            while w3; stmt s4; procedure p; variable v;
            Select w3 such that Modifies(p, v) and Parent(w3, s4)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Parent"


def test_relations_modifies_and_uses():
    result = parse_query(
        """
            while w; stmt s4; variable v, v2; procedure p;
            Select w such that Modifies(p, v2) and Uses(p, v)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Uses"


def test_relations_uses_and_modifies():
    result = parse_query(
        """
            while w; stmt s4; variable v, v2; procedure p;
            Select w such that Uses(329, v) and Modifies(p, v2)
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Uses"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"


def test_relations_uses_and_modifies_not_valid_modifies():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w; stmt s4; procedure p; variable v;
            Select w such that Uses(p, v) and Modyfikuje(_, "hello")
            """
        )

    assert "Token 'Modyfikuje' is not a valid RELATIONSHIP_NAME" in str(e.value)


def test_relations_uses_and_modifies_not_valid_uses():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w; stmt s4;
            Select w such that Use(329, w) and Modifies(_, "hello")
            """
        )

    assert "Token 'Use' is not a valid RELATIONSHIP_NAME" in str(e.value)
