def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    fit = remaining - item
    if used == 0:
        return 1.0 / (fit + 1)
    return used * used / (fit + 1)