def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    if r == 0:
        return 10000 - index
    if r < 5:
        return 8000 - r * 10 - index
    f = r / capacity
    return -f * f - 1.0 - index * 0.001
