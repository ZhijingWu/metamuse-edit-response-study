def score(remaining, item, capacity, index, n_bins):
    space = remaining - item
    frac = space / capacity
    load = 1.0 - remaining / capacity
    return frac * (1.0 + frac * frac) * (1.0 + 0.5 * load * load)
