def score(remaining, item, capacity, index, n_bins):
    r = remaining / capacity
    s = item / capacity
    if r > 0.05:
        p = (1.0 - r) ** 2
    else:
        p = (1.0 - r) ** 0.5
    return p + 1.0 / (index + 1) - s * r
