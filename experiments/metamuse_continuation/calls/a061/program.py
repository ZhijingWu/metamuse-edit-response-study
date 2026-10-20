def score(remaining, item, capacity, index, n_bins):
    slack = remaining - item
    return slack - 1.0 / (slack + 1.0)
