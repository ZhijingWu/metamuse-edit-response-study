def score(remaining, item, capacity, index, n_bins):
    w = remaining - item
    c = capacity - remaining
    f = c / capacity
    return w * (1.0 + f * f) * (1.0 + 0.003 * c)