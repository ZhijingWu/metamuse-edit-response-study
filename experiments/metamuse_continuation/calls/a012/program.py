def score(remaining, item, capacity, index, n_bins):
    s = capacity - remaining
    return s * 1000.0 - index
