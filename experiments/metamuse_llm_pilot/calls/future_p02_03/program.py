def score(remaining, item, capacity, index, n_bins):
    return capacity - remaining + item - index
