def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    leftover = remaining - item
    return 1.0 / (leftover + 1) + item * used
