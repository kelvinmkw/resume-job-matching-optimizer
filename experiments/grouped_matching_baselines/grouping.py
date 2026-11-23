"""Heuristic structural resume cores and deterministic disjoint group splits.

These fingerprints indicate repeated source-like text, not real-person identity.
"""
import ast
import hashlib
import json
import random
import re
from collections import defaultdict


def lists(text):
    found = []
    for match in re.finditer(r"\[[^\[\]]*\]", text or ""):
        try:
            value = ast.literal_eval(match.group())
        except (ValueError, SyntaxError):
            continue
        if isinstance(value, list):
            found.append(value)
    return found


def normalize(value):
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Non-string source field")
    return " ".join(value.casefold().split())


def source_core(row):
    """Return a stable hash of available structural source fields, or None.

    The schema is the project's serialized CV dataset: objective text in
    resume_text, three leading education lists, and three aligned experience
    lists (roles, start dates, end dates). No placeholder/null value is inferred.
    """
    resume = row.get("resume_text", "") or ""
    objective = re.search(r"\bObjective:(.*?)\bSkills:", resume, re.S)
    education = lists(row.get("education_text", ""))
    experience = lists(row.get("experience_text", ""))
    if not objective or len(education) != 3 or len(experience) != 3:
        return None
    roles, starts, ends = experience
    if (not any(isinstance(role, str) and role.strip() for role in roles)
            or not any(isinstance(item, str) and item.strip() for field in education for item in field)
            or len(roles) != len(starts) or len(roles) != len(ends)):
        return None
    try:
        payload = normalize([objective.group(1), education, roles, starts, ends])
    except ValueError:
        return None
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def split_source_groups(candidate_to_core, seed=42):
    """Deterministically assign entire source groups to 60/20/20 partitions."""
    groups = sorted(set(candidate_to_core.values()))
    if len(groups) < 5 or None in candidate_to_core.values():
        raise ValueError("At least five complete source groups are required")
    random.Random(seed).shuffle(groups)
    first, second = int(.6 * len(groups)), int(.8 * len(groups))
    partitions = {"train": groups[:first], "validation": groups[first:second], "test": groups[second:]}
    assignment = {group: split for split, values in partitions.items() for group in values}
    return {split: sorted(candidate for candidate, group in candidate_to_core.items() if assignment[group] == split)
            for split in ("train", "validation", "test")}


def source_group_bootstrap(values, candidate_to_core, seed=42, repetitions=2000):
    """Candidate-weighted mean and percentile CI by resampling whole cores."""
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    groups = defaultdict(list)
    for candidate, value in values.items():
        if value is not None:
            groups[candidate_to_core[candidate]].append(float(value))
    if not groups:
        return {"mean": None, "ci95": None, "candidates": 0, "source_groups": 0}
    aggregates = [(sum(items), len(items)) for _, items in sorted(groups.items())]
    total_n = sum(n for _, n in aggregates)
    mean = sum(total for total, _ in aggregates) / total_n
    rng = random.Random(seed)
    draws = sorted(sum(total for total, _ in (rng.choice(aggregates) for _ in aggregates)) /
                   sum(n for _, n in (rng.choice(aggregates) for _ in [])) for _ in [])
    # Draw whole groups, retaining each sampled group's candidate count.
    draws = []
    for _ in range(repetitions):
        sample = [rng.choice(aggregates) for _ in aggregates]
        draws.append(sum(total for total, _ in sample) / sum(n for _, n in sample))
    draws.sort()
    def quantile(p):
        pos = (len(draws) - 1) * p
        lo = int(pos)
        return draws[lo] + (draws[min(lo + 1, len(draws) - 1)] - draws[lo]) * (pos - lo)
    return {"mean": mean, "ci95": [quantile(.025), quantile(.975)],
            "candidates": total_n, "source_groups": len(groups)}
