def score(remaining, item, capacity, index, n_bins):
    space = remaining - item
    return -space * 10000 - remaining * 10 - index
