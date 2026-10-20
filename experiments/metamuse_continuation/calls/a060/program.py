def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    fit = remaining - item
    s = item / capacity
    rf = fit / capacity
    uf = used / capacity
    return uf ** 3 * (1.0 - rf) * (1.0 + 5.0 * s) / (index + 1)
