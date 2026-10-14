import json

from app.agents.subagents import build_report
from app.agents.verifier import extract_numbers, numbers_from_report, verify_answer
from langchain_core.messages import AIMessage, ToolMessage

STATS = '{"n": 66, "p25": 38000.0, "p50": 43500.0, "p75": 50000.0, "note": null}'


def stats_report():
    return build_report(
        [ToolMessage(STATS, tool_call_id="c1"), AIMessage("Median is 43,500.")]
    )


def test_extract_numbers_handles_commas_and_decimals():
    assert extract_numbers("between 38,000 and 50000.5 NIS") == {38000.0, 50000.5}


def test_extract_numbers_understands_thousands_suffixes():
    assert extract_numbers("about 43.5K or 43.5 אלף or 62 א׳") == {43500.0, 62000.0}


def test_extract_numbers_ignores_percentile_labels():
    assert extract_numbers("p50 is 43,500") == {43500.0}


def test_extract_numbers_does_not_treat_word_starting_with_k_as_thousands():
    assert extract_numbers("5 key points") == {5.0}


def test_numbers_from_report_reads_tool_data_only():
    assert numbers_from_report(stats_report()) == {
        66.0, 38000.0, 43500.0, 50000.0, 25.0, 50.0, 75.0
    }


def test_list_numbering_is_not_a_claim():
    assert extract_numbers("examples:\n1. 32,000 NIS\n2) 35,000 NIS") == {32000.0, 35000.0}


def test_percentile_labels_are_allowed_when_the_data_has_percentile_keys():
    result = verify_answer("q", "The 25% mark is 38,000 and the 75% mark is 50,000.", [stats_report()])

    assert result.ok


def test_percentile_label_is_not_allowed_without_percentile_data():
    result = verify_answer("q", "The 25% mark is 38,000.", [])

    assert result.unsupported == [25.0, 38000.0]


def test_numbers_from_report_without_marker_is_empty():
    assert numbers_from_report("just text with 99 in it") == set()


def test_numbers_from_report_survives_non_json_tool_output():
    report = f"x\n\n{DATA}\n" + json.dumps(["median 43,500 from 66 posts"])
    assert numbers_from_report(report) == {43500.0, 66.0}


def test_verified_answer_passes():
    result = verify_answer("devops salary", "Median 43,500 from 66 posts.", [stats_report()])

    assert result.ok
    assert result.unsupported == []


def test_invented_number_is_flagged():
    result = verify_answer("devops salary", "Median is 52,000 NIS.", [stats_report()])

    assert not result.ok
    assert result.unsupported == [52000.0]


def test_number_from_the_question_is_allowed():
    result = verify_answer("salary with 5 years", "With 5 years the median is 43,500.", [stats_report()])

    assert result.ok


def test_rounding_within_tolerance_is_allowed():
    result = verify_answer("q", "Median is 43,500.4", [stats_report()])

    assert result.ok


def test_answer_with_no_reports_and_a_number_is_flagged():
    result = verify_answer("q", "Typical pay is 40,000.", [])

    assert result.unsupported == [40000.0]


DATA = "TOOL_DATA:"
