def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    u = capacity - remaining
    return 1.0 / (r + 1) + u * item / (capacity * capacity)
