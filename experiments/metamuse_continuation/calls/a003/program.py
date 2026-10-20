def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    c = capacity
    p = c - remaining
    i = item
    return (r / c) ** 2 * (1.0 + p / c) - (i / c) ** 4
