def score(remaining, item, capacity, index, n_bins):
    new_rem = remaining - item
    return -((new_rem ** 4 + 1) ** 0.125 - 1 + new_rem)
