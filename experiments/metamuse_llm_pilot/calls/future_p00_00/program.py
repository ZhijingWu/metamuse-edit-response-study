def score(remaining, item, capacity, index, n_bins):
    g = remaining - item
    return item * 1.05 - remaining + g / remaining
