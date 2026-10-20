def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    r = remaining - item
    f = r / capacity
    s = item / capacity
    return -(abs(f - 0.09) + 0.12 * (used / capacity) ** 2 + 0.05 * abs(s - 0.28))
