def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    u = capacity - remaining
    return -abs(r - 10) - 0.002 * (r * r) - 0.001 * u * u
