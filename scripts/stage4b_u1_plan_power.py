"""Plan conditional power for the Stage4B-U1 frozen reservation.

The calculation uses only the fixed reservation size and already published
Stage4A-R2 development event counts. It never reads reservation records.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


RESERVATION_N = 4500
PLANNING_GAINS = 94
PLANNING_HARMS = 69
IUT_COMPONENT_ALPHA = 0.05
MIN_RETENTION_GAP = 0.15
MIN_CR20_DELTA = 0.005

SCENARIOS = (
    ("no_event_enrichment", 0.60, 0.60),
    ("weak_enrichment", 0.65, 0.50),
    ("target_enrichment", 0.70, 0.40),
    ("strong_enrichment", 0.75, 0.35),
)


def binomial_pmf(k: int, n: int, probability: float) -> float:
    return math.comb(n, k) * probability**k * (1.0 - probability) ** (n - k)


def fisher_greater_pvalue(selected_gains: int, gains: int, selected_harms: int, harms: int) -> float:
    selected_total = selected_gains + selected_harms
    population = gains + harms
    lower = max(0, selected_total - harms)
    upper = min(gains, selected_total)
    denominator = math.comb(population, selected_total)
    return sum(
        math.comb(gains, value) * math.comb(harms, selected_total - value) / denominator
        for value in range(max(selected_gains, lower), upper + 1)
    )


def exact_mcnemar_two_sided_pvalue(gains: int, harms: int) -> float:
    discordant = gains + harms
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, value) for value in range(0, min(gains, harms) + 1))
    return min(1.0, 2.0 * tail / (2.0**discordant))


def scenario_power(gain_retention: float, harm_retention: float) -> dict[str, float]:
    fisher_power = 0.0
    mcnemar_power = 0.0
    joint_power = 0.0
    for selected_gains in range(PLANNING_GAINS + 1):
        gain_mass = binomial_pmf(selected_gains, PLANNING_GAINS, gain_retention)
        for selected_harms in range(PLANNING_HARMS + 1):
            mass = gain_mass * binomial_pmf(selected_harms, PLANNING_HARMS, harm_retention)
            retention_gap = selected_gains / PLANNING_GAINS - selected_harms / PLANNING_HARMS
            cr20_delta = (selected_gains - selected_harms) / RESERVATION_N
            fisher_pass = (
                retention_gap >= MIN_RETENTION_GAP
                and fisher_greater_pvalue(
                    selected_gains, PLANNING_GAINS, selected_harms, PLANNING_HARMS
                )
                <= IUT_COMPONENT_ALPHA
            )
            mcnemar_pass = (
                cr20_delta >= MIN_CR20_DELTA
                and exact_mcnemar_two_sided_pvalue(selected_gains, selected_harms)
                <= IUT_COMPONENT_ALPHA
            )
            fisher_power += mass * fisher_pass
            mcnemar_power += mass * mcnemar_pass
            joint_power += mass * fisher_pass * mcnemar_pass
    return {
        "expected_selected_gains": PLANNING_GAINS * gain_retention,
        "expected_selected_harms": PLANNING_HARMS * harm_retention,
        "expected_cr20_delta_vs_dense": (
            PLANNING_GAINS * gain_retention - PLANNING_HARMS * harm_retention
        )
        / RESERVATION_N,
        "fisher_mechanism_power": fisher_power,
        "mcnemar_retrieval_power": mcnemar_power,
        "joint_primary_power": joint_power,
    }


def build_plan() -> dict[str, object]:
    return {
        "stage": "Stage4B-U1",
        "protocol": "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
        "protocol_status": "REVISION_2_DESIGN_ONLY_IMPLEMENTATION_PENDING",
        "status": "PLANNING_ONLY_NO_RESERVATION_ACCESS",
        "reservation_n": RESERVATION_N,
        "planning_anchor": {
            "source": "verified Stage4A-R2 development estimates",
            "gain_events": PLANNING_GAINS,
            "harm_events": PLANNING_HARMS,
            "restriction": "used for power planning only; never for controller fitting or threshold selection",
        },
        "primary_testing": {
            "framework": "intersection-union test for one joint claim",
            "joint_claim_alpha": 0.05,
            "alpha_per_component": IUT_COMPONENT_ALPHA,
            "mechanism_test": "one-sided Fisher exact test for gain retention > harm retention",
            "minimum_practical_retention_gap": MIN_RETENTION_GAP,
            "retrieval_test": "two-sided exact McNemar for controller vs dense CR@20",
            "minimum_practical_cr20_delta": MIN_CR20_DELTA,
            "success_rule": "both zero-null tests and both observed practical-effect gates must pass",
            "claim_boundary": "practical thresholds are observed effect gates, not tested margins",
        },
        "scenarios": [
            {
                "scenario": name,
                "gain_retention": gain_retention,
                "harm_retention": harm_retention,
                **scenario_power(gain_retention, harm_retention),
            }
            for name, gain_retention, harm_retention in SCENARIOS
        ],
        "interpretation": [
            "Power is conditional on 94 gain and 69 harm opportunities in a 4,500-query reservation.",
            "These counts are planning anchors, not assumed reservation outcomes.",
            "The 0.60 resource budget is defined on planned insert units, not query count.",
            "No scenario can authorize reservation access or alter the label-free controller.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/STAGE4B_U1_POWER_PLAN.json"),
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_plan(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
