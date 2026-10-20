def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    t = gap / capacity
    f = t * t
    return f - (1.0 - f) * index / capacity
