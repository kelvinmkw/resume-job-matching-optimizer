"""Linear-gain NDCG with tie averaging and bootstrap utilities."""
import math
import random
import statistics

def ndcg(labels, scores, k):
    if len(labels) != len(scores): raise ValueError("labels and scores must have equal length")
    if k < 1: raise ValueError("k must be positive")
    ideal = sum(float(v) / math.log2(i + 2) for i, v in enumerate(sorted(labels, reverse=True)[:k]))
    if ideal <= 0: return None
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    dcg, start = 0.0, 0
    while start < len(order) and start < k:
        end = start + 1
        while end < len(order) and scores[order[end]] == scores[order[start]]: end += 1
        mean_gain = statistics.mean(labels[i] for i in order[start:end])
        dcg += mean_gain * sum(1 / math.log2(rank + 2) for rank in range(start, min(end, k)))
        start = end
    return dcg / ideal

def expected_random(labels, k):
    return ndcg(labels, [0.0] * len(labels), k)

def bootstrap(values, seed=42, repetitions=2000):
    values = [float(v) for v in values if v is not None]
    if not values: return {"mean": None, "ci95": None, "candidates": 0}
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(repetitions))
    def quantile(p):
        pos = (len(draws) - 1) * p; lo = int(pos)
        return draws[lo] + (draws[min(lo + 1, len(draws)-1)] - draws[lo]) * (pos-lo)
    return {"mean": statistics.mean(values), "ci95": [quantile(.025), quantile(.975)], "candidates": len(values)}
