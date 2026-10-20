def score(remaining, item, capacity, index, n_bins):
    r = remaining / capacity
    i = item / capacity
    if r <= 0.05:
        return 100.0 / (index + 1)
    if r - i <= 0.05:
        return 50.0 / (index + 1)
    return (1.0 - r) / (index + 1)
