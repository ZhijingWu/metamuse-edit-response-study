def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    space = remaining - item
    return (used ** 2) / (space + 1)
