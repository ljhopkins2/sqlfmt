import pytest

from sqlfmt.merger import CannotMergeException, LineMerger
from sqlfmt.mode import Mode
from sqlfmt.parser import Query


@pytest.fixture
def merger(default_mode: Mode) -> LineMerger:
    return LineMerger(default_mode)


def test_create_merged_line(merger: LineMerger) -> None:

    source_string = """
    select
        able,
        baker,
        /*  a
            multiline
            comment
        */
        charlie,



    """
    raw_query = Query.from_source(source_string, merger.mode)

    expected = "select able, baker,\n"
    actual = merger.create_merged_line(raw_query.lines[0:4])
    assert str(actual) == expected

    with pytest.raises(CannotMergeException):
        # can't merge whitespace
        _ = merger.create_merged_line(raw_query.lines[-3:-1])

    with pytest.raises(CannotMergeException):
        # can't merge a multiline comment
        _ = merger.create_merged_line(raw_query.lines[4:8])


def test_basic_merge(merger: LineMerger) -> None:
    source_string = """
        nullif(
            full_name,
            ''
        ) as c,
    """
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    expected_string = "nullif(full_name, '') as c,"

    result = "".join(map(str, merged_lines)).strip()
    assert result == expected_string


def test_nested_merge(merger: LineMerger) -> None:
    source_string = """
    select
        a,
        nullif(
            split_part(
                full_name,
                ' ',
                2
            ),
            ''
        ) as last_name,
    """
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    expected_string = (
        "select a, nullif(split_part(full_name, ' ', 2), '') as last_name,"
    )

    result = "".join(map(str, merged_lines)).strip()
    assert result == expected_string


def test_incomplete_merge(merger: LineMerger) -> None:
    source_string = """
    select
        first_field,
        nullif(
            split_part(
                full_name,
                ' ',
                2
            ),
            ''
        ) as last_name,
        another_field,
        case
            when short
            then 1
        end,
        yet_another_field,
        and_still_another_field
    from
        my_table
    where
        some_condition is true
    """
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    result = list(map(str, merged_lines))

    expected = [
        "\n",
        "select\n",
        "    first_field,\n",
        "    nullif(split_part(full_name, ' ', 2), '') as last_name,\n",
        "    another_field,\n",
        "    case when short then 1 end,\n",
        "    yet_another_field,\n",
        "    and_still_another_field\n",
        "from my_table\n",
        "where some_condition is true\n",
    ]

    assert result == expected


def test_cte_merge(merger: LineMerger) -> None:
    source_string = """
    with
        my_cte as (
            select * from my_table
        )
    select * from my_cte
    """
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    result = list(map(str, merged_lines))

    expected = [
        "with my_cte as (select * from my_table) select * from my_cte\n",
    ]

    assert result == expected


def test_case_then_merge(merger: LineMerger) -> None:
    source_string = """
    case
        when
            some_initial_condition_is_true
        then
            some_other_condition
        else
            something_else_entirely
    end
    """
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    result = list(map(str, merged_lines))

    expected = [
        "\n",
        "case\n",
        "    when some_initial_condition_is_true\n",
        "    then some_other_condition\n",
        "    else something_else_entirely\n",
        "end\n",
    ]

    assert result == expected


def test_merge_count_window_function(merger: LineMerger) -> None:
    source_string = (
        "count(\n"
        "    case\n"
        "        when\n"
        "            a is null\n"
        "        then\n"
        "            1\n"
        "    end\n"
        ") over (\n"
        "    partition by\n"
        "        user_id,\n"
        "        date_trunc('year', performed_at)\n"
        ") as d,\n"
    )
    raw_query = Query.from_source(source_string, merger.mode)
    merged_lines = merger.maybe_merge_lines(raw_query.lines)

    result = list(map(str, merged_lines))

    expected = [
        "count(case when a is null then 1 end) over (\n",
        "    partition by user_id, date_trunc('year', performed_at)\n",
        ") as d,\n",
    ]

    assert result == expected
