"""Generate the frozen Stage4A-R2 precision and paired-power design."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
from scipy.stats import binom


Z_95 = NormalDist().inv_cdf(0.975)


def wilson_halfwidth(n: int, prevalence: float, z: float = Z_95) -> float:
    denominator = 1.0 + z * z / n
    return (
        z
        * math.sqrt(
            prevalence * (1.0 - prevalence) / n
            + z * z / (4.0 * n * n)
        )
        / denominator
    )


def minimum_wilson_n(prevalence: float, target_halfwidth: float) -> int:
    low, high = 1, 200_000
    while low < high:
        middle = (low + high) // 2
        if wilson_halfwidth(middle, prevalence) <= target_halfwidth:
            high = middle
        else:
            low = middle + 1
    return low


def exact_conditional_mcnemar_power(
    n: int,
    total_discordance: float,
    net_gain: float,
    alpha: float,
) -> float:
    gain_probability = (total_discordance + net_gain) / 2.0
    conditional_gain = gain_probability / total_discordance
    lower_m = max(0, int(binom.ppf(1e-13, n, total_discordance)))
    upper_m = min(n, int(binom.ppf(1.0 - 1e-13, n, total_discordance)) + 1)
    discordant_counts = np.arange(lower_m, upper_m + 1)
    count_probabilities = binom.pmf(discordant_counts, n, total_discordance)
    lower_critical = binom.ppf(alpha / 2.0, discordant_counts, 0.5) - 1
    upper_critical = binom.isf(alpha / 2.0, discordant_counts, 0.5) + 1
    rejection_probabilities = binom.cdf(
        lower_critical,
        discordant_counts,
        conditional_gain,
    ) + binom.sf(
        upper_critical - 1,
        discordant_counts,
        conditional_gain,
    )
    return float(np.sum(count_probabilities * rejection_probabilities))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--planning-prevalence", type=float, default=0.03)
    parser.add_argument("--target-halfwidth", type=float, default=0.005)
    parser.add_argument("--development-n", type=int, default=4500)
    parser.add_argument("--reservation-n", type=int, default=4500)
    parser.add_argument("--excluded-prefix", type=int, default=800)
    parser.add_argument("--official-dev-rows", type=int, default=12576)
    parser.add_argument("--mcnemar-discordance", type=float, default=0.05)
    parser.add_argument("--mcnemar-net-gain", type=float, default=0.01)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--target-power", type=float, default=0.80)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frozen = {
        "planning_prevalence": 0.03,
        "target_halfwidth": 0.005,
        "development_n": 4500,
        "reservation_n": 4500,
        "excluded_prefix": 800,
        "official_dev_rows": 12576,
        "mcnemar_discordance": 0.05,
        "mcnemar_net_gain": 0.01,
        "alpha": 0.05,
        "target_power": 0.80,
    }
    for name, expected in frozen.items():
        actual = getattr(args, name)
        if isinstance(expected, float):
            if not math.isclose(actual, expected, abs_tol=1e-15):
                raise ValueError(f"Stage4A-R2 freezes {name}={expected}")
        elif actual != expected:
            raise ValueError(f"Stage4A-R2 freezes {name}={expected}")

    minimum_n = minimum_wilson_n(
        args.planning_prevalence,
        args.target_halfwidth,
    )
    if minimum_n != 4497 or args.development_n < minimum_n:
        raise ValueError(f"Unexpected Wilson minimum or undersized design: {minimum_n}")

    development_start = args.excluded_prefix
    development_end = development_start + args.development_n
    reservation_start = development_end
    reservation_end = reservation_start + args.reservation_n
    if reservation_end > args.official_dev_rows:
        raise ValueError("Stage4A-R2 partitions exceed official dev rows")

    paired_power = exact_conditional_mcnemar_power(
        args.development_n,
        args.mcnemar_discordance,
        args.mcnemar_net_gain,
        args.alpha,
    )
    if paired_power < args.target_power:
        raise ValueError(f"Secondary paired-power target not met: {paired_power}")

    sensitivity = []
    for prevalence in (0.005, 0.01, 0.02, 0.03, 0.04):
        sensitivity.append(
            {
                "prevalence": prevalence,
                "minimum_n_for_halfwidth": minimum_wilson_n(
                    prevalence,
                    args.target_halfwidth,
                ),
                "halfwidth_at_n4500": wilson_halfwidth(
                    args.development_n,
                    prevalence,
                ),
            }
        )

    plan = {
        "status": "FROZEN_APPROVED_BEFORE_OFFICIAL_ROW_EXTRACTION",
        "primary_design": {
            "estimands": ["q25_gain_prevalence", "q25_harm_prevalence"],
            "interval": "Wilson 95%",
            "planning_prevalence": args.planning_prevalence,
            "target_halfwidth": args.target_halfwidth,
            "exact_minimum_n": minimum_n,
            "development_n": args.development_n,
            "achieved_halfwidth_at_planning_prevalence": wilson_halfwidth(
                args.development_n,
                args.planning_prevalence,
            ),
        },
        "secondary_paired_design": {
            "test": "exact conditional two-sided McNemar",
            "alpha": args.alpha,
            "minimum_net_cr20_gain": args.mcnemar_net_gain,
            "planning_total_discordance": args.mcnemar_discordance,
            "power_at_development_n": paired_power,
            "target_power": args.target_power,
        },
        "official_dev_partition": {
            "excluded_prior_rows": f"[0:{args.excluded_prefix})",
            "development_rows": f"[{development_start}:{development_end})",
            "development_queries": args.development_n,
            "reservation_rows": f"[{reservation_start}:{reservation_end})",
            "reservation_queries": args.reservation_n,
            "unused_rows": f"[{reservation_end}:{args.official_dev_rows})",
            "unused_queries": args.official_dev_rows - reservation_end,
        },
        "sensitivity": sensitivity,
        "interpretation": {
            "primary_objective": "official gain/harm prevalence estimation",
            "controller_training_authorized": False,
            "threshold_tuning_authorized": False,
            "reservation_metrics_authorized": False,
            "cross_dataset_generalization_claim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
