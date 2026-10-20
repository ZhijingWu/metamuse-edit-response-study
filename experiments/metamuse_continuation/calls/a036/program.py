def score(remaining, item, capacity, index, n_bins):
    diff = remaining - item - 20
    return -diff * diff - exp(max(0, diff))
