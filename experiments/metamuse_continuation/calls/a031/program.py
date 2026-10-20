def score(remaining, item, capacity, index, n_bins):
    s = remaining - item
    if capacity % s == 0:
        p = s / capacity
        return s - s * p * p - 1.0
    if s % item == 0:
        return s - item / s - 0.5
    if item % s == 0:
        return s - s / item - 0.5
    if (item * s) % (item + s) == 0:
        return s - 0.25
    return s + s / (capacity + s)
