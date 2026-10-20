def score(remaining, item, capacity, index, n_bins):
    space = remaining - item
    if space == 0:
        return 1.0e9 - index
    return -space * 100.0 - index
