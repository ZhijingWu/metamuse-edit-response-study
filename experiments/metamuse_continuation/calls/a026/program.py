def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    return 1.0 / (gap + 1) - remaining / (capacity * 2.0) + 1.0 / (remaining + 1) - 0.01 * item / capacity
