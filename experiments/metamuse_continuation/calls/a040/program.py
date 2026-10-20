def score(remaining, item, capacity, index, n_bins):
    u = capacity - remaining
    f = remaining - item
    return (u + 1) ** 3 / (f + 1)
