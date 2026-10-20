def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    fit = remaining - item
    p = used / capacity
    t = item / capacity
    d = fit / capacity
    return p ** 3 - d ** 3 + t * (p + 0.5 * t)
