from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def answer_length_words(answer: str) -> int:
    return len(re.findall(r"\b\w+\b", answer))


def grounding_check(answer: str, grounding_terms: list[str]) -> float:
    """
    Simple grounding heuristic: ratio of expected grounding terms present in answer.
    """
    if not grounding_terms:
        return 1.0

    normalized_answer = normalize_text(answer)
    matches = sum(
        1 for term in grounding_terms if normalize_text(term) and normalize_text(term) in normalized_answer
    )
    return round(matches / len(grounding_terms), 3)


def keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0

    normalized_answer = normalize_text(answer)
    matches = sum(
        1
        for keyword in expected_keywords
        if normalize_text(keyword) and normalize_text(keyword) in normalized_answer
    )
    return round(matches / len(expected_keywords), 3)


def evaluate_answer(
    answer: str,
    expected_keywords: list[str],
    grounding_terms: list[str],
) -> dict[str, Any]:
    length_score = answer_length_words(answer)
    grounding_score = grounding_check(answer, grounding_terms)
    keyword_score = keyword_coverage(answer, expected_keywords)
    composite = round((grounding_score + keyword_score) / 2, 3)

    return {
        "answer_length_words": length_score,
        "grounding_score": grounding_score,
        "keyword_coverage_score": keyword_score,
        "composite_score": composite,
    }


def load_dataset(dataset_path: Path) -> list[dict[str, Any]]:
    with dataset_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON array of records.")
    return data


def _live_agent_answer(question: str, session_id: str, trace: bool) -> str:
    from src.invoke_agent import invoke_agent

    result = invoke_agent(question=question, session_id=session_id, enable_trace=trace)
    return result.answer


def run_evaluation(
    dataset: list[dict[str, Any]],
    use_live_agent: bool = False,
    session_id: str | None = None,
    trace: bool = False,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    if use_live_agent:
        from src.config import resolve_session_id

        session_id = resolve_session_id(session_id)

    for item in dataset:
        question = item.get("question", "")
        expected_keywords = item.get("expected_keywords", [])
        grounding_terms = item.get("grounding_terms", [])

        if use_live_agent:
            answer = _live_agent_answer(question=question, session_id=session_id or "", trace=trace)
        else:
            answer = item.get("sample_answer", "")

        metrics = evaluate_answer(
            answer=answer,
            expected_keywords=expected_keywords,
            grounding_terms=grounding_terms,
        )
        results.append(
            {
                "id": item.get("id"),
                "question": question,
                "answer": answer,
                **metrics,
            }
        )

    summary = summarize_results(results)
    return {"summary": summary, "results": results}


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "num_samples": 0,
            "avg_answer_length_words": 0.0,
            "avg_grounding_score": 0.0,
            "avg_keyword_coverage_score": 0.0,
            "avg_composite_score": 0.0,
        }

    num_samples = len(results)
    avg_answer_length = round(
        sum(result["answer_length_words"] for result in results) / num_samples, 3
    )
    avg_grounding = round(sum(result["grounding_score"] for result in results) / num_samples, 3)
    avg_keyword_coverage = round(
        sum(result["keyword_coverage_score"] for result in results) / num_samples, 3
    )
    avg_composite = round(sum(result["composite_score"] for result in results) / num_samples, 3)

    return {
        "num_samples": num_samples,
        "avg_answer_length_words": avg_answer_length,
        "avg_grounding_score": avg_grounding,
        "avg_keyword_coverage_score": avg_keyword_coverage,
        "avg_composite_score": avg_composite,
    }


def _build_parser() -> argparse.ArgumentParser:
    default_dataset = Path(__file__).with_name("eval_dataset.json")
    default_output = Path(__file__).with_name("latest_eval_report.json")

    parser = argparse.ArgumentParser(description="Run lightweight RAG evaluation for Bedrock Agent answers.")
    parser.add_argument("--dataset", type=Path, default=default_dataset, help="Path to evaluation dataset.")
    parser.add_argument(
        "--use-live-agent",
        action="store_true",
        help="Invoke the configured Bedrock Agent for each question instead of sample answers.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Session ID to reuse across live evaluation calls.",
    )
    parser.add_argument("--trace", action="store_true", help="Enable trace capture for live invocations.")
    parser.add_argument("--output", type=Path, default=default_output, help="Path to JSON output report.")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    report = run_evaluation(
        dataset=dataset,
        use_live_agent=args.use_live_agent,
        session_id=args.session_id,
        trace=args.trace,
    )

    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    print("Evaluation complete.")
    print(f"Samples: {summary['num_samples']}")
    print(f"Avg answer length (words): {summary['avg_answer_length_words']}")
    print(f"Avg grounding score: {summary['avg_grounding_score']}")
    print(f"Avg keyword coverage: {summary['avg_keyword_coverage_score']}")
    print(f"Avg composite score: {summary['avg_composite_score']}")
    print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()
