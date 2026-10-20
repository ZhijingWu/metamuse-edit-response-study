def score(remaining, item, capacity, index, n_bins):
    s = capacity - remaining
    return 1.0 / (remaining + 1) - 1.0 / (s + 1) - 1e-9 * index
