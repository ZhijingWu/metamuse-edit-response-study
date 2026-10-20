def score(remaining, item, capacity, index, n_bins):
    f = (remaining - item) / capacity
    u = 1 - remaining / capacity
    return f * (1 + u * u) + (item / capacity) * (1 - u)