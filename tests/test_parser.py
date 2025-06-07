import sys
import os
import pytest

# Add the root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from eval_harness import parse_scores


def test_parse_scores_valid_response():
    response = """
    Clarity & Structure: 4/5 – Well-organized and clear.
    Clinical Accuracy & Appropriateness: 5/5 – Reflects session faithfully.
    Tone & Professionalism: 5/5 – Professional and empathetic tone.
    """
    scores = parse_scores(response)
    assert scores["clarity_score"] == 4
    assert scores["accuracy_score"] == 5
    assert scores["tone_score"] == 5


def test_parse_scores_missing_accuracy():
    response = """
    Clarity & Structure: 3/5 – Adequate clarity.
    Tone & Professionalism: 4/5 – Good tone.
    """
    scores = parse_scores(response)
    assert scores["clarity_score"] == 3
    assert scores["accuracy_score"] is None
    assert scores["tone_score"] == 4


def test_parse_scores_malformed_input():
    response = """
    Clarity & Structure – 4 of 5
    Accuracy – perfect
    Tone: 5
    """
    scores = parse_scores(response)
    assert scores["clarity_score"] is None
    assert scores["accuracy_score"] is None
    assert scores["tone_score"] is None


def test_parse_scores_out_of_range():
    response = """
    Clarity & Structure: 7/5 – Overly positive.
    Clinical Accuracy & Appropriateness: 0/5 – Incorrect.
    Tone & Professionalism: -1/5 – Negative tone.
    """
    scores = parse_scores(response)
    assert scores["clarity_score"] == 7
    assert scores["accuracy_score"] == 0
    assert scores["tone_score"] == -1


def test_parse_scores_empty_input():
    scores = parse_scores("")
    assert scores["clarity_score"] is None
    assert scores["accuracy_score"] is None
    assert scores["tone_score"] is None
