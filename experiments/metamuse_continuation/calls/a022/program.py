def score(remaining, item, capacity, index, n_bins):
    filled = capacity - remaining
    return (filled + 1) ** 3 + 1.0 / (remaining + 1)
