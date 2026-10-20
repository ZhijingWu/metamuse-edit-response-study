def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    return (1.0 / (r + 1)) * (1.0 / (index + 1))
