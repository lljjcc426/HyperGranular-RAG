"""Produce the deterministic event-count sample-size plan for restarted Stage4A."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def probability_at_least(n: int, event_target: int, prevalence: float) -> float:
    return 1.0 - sum(
        math.comb(n, events)
        * prevalence**events
        * (1.0 - prevalence) ** (n - events)
        for events in range(event_target)
    )


def minimum_n(event_target: int, prevalence: float, target_probability: float) -> int:
    n = event_target
    while probability_at_least(n, event_target, prevalence) < target_probability:
        n += 1
    return n


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-target", type=int, default=20)
    parser.add_argument("--minimum-prevalence", type=float, default=0.01)
    parser.add_argument("--target-probability", type=float, default=0.95)
    parser.add_argument("--round-to", type=int, default=100)
    parser.add_argument("--excluded-prefix", type=int, default=800)
    parser.add_argument("--official-dev-rows", type=int, default=12576)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.event_target != 20:
        raise ValueError("Restarted Stage4A aligns with the Stage3C 20-gain feasibility threshold")
    if not math.isclose(args.minimum_prevalence, 0.01, abs_tol=1e-15):
        raise ValueError("Restarted Stage4A uses a conservative minimum gain prevalence of 0.01")
    if not math.isclose(args.target_probability, 0.95, abs_tol=1e-15):
        raise ValueError("Restarted Stage4A uses a 0.95 target probability")
    if args.round_to != 100 or args.excluded_prefix != 800 or args.official_dev_rows != 12576:
        raise ValueError("Restarted Stage4A constants differ from the design audit")

    exact_n = minimum_n(args.event_target, args.minimum_prevalence, args.target_probability)
    planned_n = math.ceil(exact_n / args.round_to) * args.round_to
    development_start = args.excluded_prefix
    development_end = development_start + planned_n
    reservation_start = development_end
    reservation_end = reservation_start + planned_n
    if reservation_end > args.official_dev_rows:
        raise ValueError("Restarted Stage4A development and reservation slices exceed official dev rows")

    sensitivity = []
    for prevalence in (0.005, 0.01, 0.0102, 0.02):
        for target_probability in (0.80, 0.90, 0.95):
            n = minimum_n(args.event_target, prevalence, target_probability)
            sensitivity.append(
                {
                    "gain_prevalence": prevalence,
                    "target_probability": target_probability,
                    "minimum_n": n,
                }
            )

    plan = {
        "status": "PLANNING_LOWER_BOUND_ONLY_RETURNED_FOR_DESIGN_REVISION",
        "method": "exact binomial probability of observing at least the target number of gain events",
        "design_inputs": {
            "gain_event_target": args.event_target,
            "minimum_gain_prevalence": args.minimum_prevalence,
            "target_probability": args.target_probability,
            "round_to": args.round_to,
            "rationale": "20 gains aligns with a frozen Stage3C planning heuristic; 0.01 is a sensitivity assumption informed by the invalidated Stage4A mirror pilot, not an official-data lower bound",
        },
        "calculation": {
            "exact_minimum_n": exact_n,
            "planned_development_n": planned_n,
            "achieved_probability_at_planned_n": probability_at_least(
                planned_n,
                args.event_target,
                args.minimum_prevalence,
            ),
            "expected_gains_at_minimum_prevalence": planned_n * args.minimum_prevalence,
            "probability_at_stage4a_n400": probability_at_least(
                400,
                args.event_target,
                args.minimum_prevalence,
            ),
        },
        "official_dev_partition": {
            "excluded_prior_rows": "[0:800)",
            "development_rows": f"[{development_start}:{development_end})",
            "development_queries": planned_n,
            "reservation_rows": f"[{reservation_start}:{reservation_end})",
            "reservation_queries": planned_n,
            "unused_rows": f"[{reservation_end}:{args.official_dev_rows})",
            "unused_queries": args.official_dev_rows - reservation_end,
        },
        "sensitivity_table": sensitivity,
        "interpretation": {
            "planning_only": True,
            "confirmatory_power_claim": False,
            "retrieval_effect_power_analysis": False,
            "controller_training_adequacy_established": False,
            "approved_sample_size": False,
            "design_revision_required": True,
            "event_rate_below_0.01": "The design no longer guarantees 95% probability of 20 gains",
            "approval_required_before_extraction": True,
            "permitted_use": "Event-count lower bound only; do not execute the restarted Stage4A from this calculation",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
