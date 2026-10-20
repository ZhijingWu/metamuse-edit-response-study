def score(remaining, item, capacity, index, n_bins):
    waste = remaining - item
    return -waste / item - waste / capacity
