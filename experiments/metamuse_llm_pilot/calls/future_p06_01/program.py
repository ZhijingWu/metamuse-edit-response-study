def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    used = capacity - remaining
    return gap ** 3 - used * gap * 5 - item * gap * 2 - used ** 2 - item
