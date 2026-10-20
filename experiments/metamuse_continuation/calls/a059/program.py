def score(remaining, item, capacity, index, n_bins):
    base = remaining - item - 20
    if base == 0:
        return 1.0 - index * 1e-8
    return -abs(base) * (1.0 + 0.005 * abs(base))
