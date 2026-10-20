def score(remaining, item, capacity, index, n_bins):
    return 1.0 / (remaining + 1) + 0.01 * (1.0 - exp(-0.5 * (index + 1)))
