from ats.pql.pql import parse_query


def test_double_such_that():
    parse_query(
        """ stmt s1;
            Select s1 such that Next(s1, 3) such that Follows(s1, 3)
           """
    )


def test_double_such_that_assert():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Next(s1, 3) such that Follows(s1, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Next"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Follows"


def test_double_such_that_multiple_relation_using_ands_assert():
    result = parse_query(
        """ prog_line pr; stmt s1;
            Select s1 such that Next(pr, 3) and Calls(s1, "x") such that Follows(s1, 3) and Parent*(s1, 5)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Next"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Calls"
    assert result[0]["conditions"]["relations"][2]["relation"] == "Follows"
    assert result[0]["conditions"]["relations"][3]["relation"] == "Parent*"


def test_double_such_that_using_with_assert():
    result = parse_query(
        """
        procedure p1;
        stmt s1;
        Select s1
            such that Calls(p1, p1)
            with p1.procName = "hello there"

            such that Follows(s1, 3)
            with s1.stmt# = 5
        """
    )

    assert result[0]["conditions"]["attributes"][0]["left"] == "p1"
    assert result[0]["conditions"]["attributes"][0]["attr_left"] == "procName"
    assert result[0]["conditions"]["attributes"][0]["right"] == '"hello there"'
    assert result[0]["conditions"]["attributes"][0]["attr_right"] is None
    assert result[0]["conditions"]["attributes"][1]["left"] == "s1"
    assert result[0]["conditions"]["attributes"][1]["attr_left"] == "stmt#"
    assert result[0]["conditions"]["attributes"][1]["right"] == "5"
    assert result[0]["conditions"]["attributes"][1]["attr_right"] is None


def test_triple_such_that_multiple_relation_using_ands_assert():
    result = parse_query(
        """ prog_line pr; stmt s1;
            Select s1 such that Next(pr, 3) such that Follows(s1, 3)
            such that Parent*(s1, 5)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Next"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Follows"
    assert result[0]["conditions"]["relations"][2]["relation"] == "Parent*"


def test_triple_such_that_using_with_assert():
    result = parse_query(
        """ prog_line pr; stmt s1, s2;
            Select s1 such that Next(pr, 3) with pr.procName = "general Kenobi" such that Follows(s1, 3) with s1.value = 109
            such that Parent*(s1, 5) with "bestname" = s2.varName
           """
    )

    assert result[0]["conditions"]["attributes"][0]["left"] == "pr"
    assert result[0]["conditions"]["attributes"][0]["attr_left"] == "procName"
    assert result[0]["conditions"]["attributes"][0]["right"] == '"general Kenobi"'
    assert result[0]["conditions"]["attributes"][0]["attr_right"] is None
    assert result[0]["conditions"]["attributes"][1]["left"] == "s1"
    assert result[0]["conditions"]["attributes"][1]["attr_left"] == "value"
    assert result[0]["conditions"]["attributes"][1]["right"] == "109"
    assert result[0]["conditions"]["attributes"][1]["attr_right"] is None
    assert result[0]["conditions"]["attributes"][2]["left"] == '"bestname"'
    assert result[0]["conditions"]["attributes"][2]["attr_left"] is None
    assert result[0]["conditions"]["attributes"][2]["right"] == "s2"
    assert result[0]["conditions"]["attributes"][2]["attr_right"] == "varName"
