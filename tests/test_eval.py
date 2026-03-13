from __future__ import annotations

from eval.eval_runner import (
    answer_length_words,
    evaluate_answer,
    grounding_check,
    keyword_coverage,
)


def test_answer_length_words_counts_tokens() -> None:
    answer = "Quarterly net revenue is gross sales minus returns."
    assert answer_length_words(answer) == 8


def test_grounding_check_returns_fraction_of_matches() -> None:
    answer = "According to the finance policy handbook, see the internal glossary."
    score = grounding_check(answer, ["finance policy handbook", "internal glossary", "control matrix"])
    assert score == 0.667


def test_keyword_coverage_returns_fraction_of_matches() -> None:
    answer = "Critical vendors require an annual review and a security questionnaire."
    score = keyword_coverage(
        answer,
        ["critical vendor", "annual review", "security questionnaire", "tiering"],
    )
    assert score == 0.75


def test_evaluate_answer_contains_expected_keys() -> None:
    metrics = evaluate_answer(
        answer="Reference to third-party risk policy and annual review process.",
        expected_keywords=["annual review"],
        grounding_terms=["third-party risk policy"],
    )
    assert "answer_length_words" in metrics
    assert "grounding_score" in metrics
    assert "keyword_coverage_score" in metrics
    assert "composite_score" in metrics
