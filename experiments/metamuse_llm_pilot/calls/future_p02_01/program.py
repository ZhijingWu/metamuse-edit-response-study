def score(remaining, item, capacity, index, n_bins):
    after = remaining - item
    return -after * 10000 - remaining * 10 - index
