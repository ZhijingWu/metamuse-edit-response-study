def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    ratio = item / capacity
    if gap == 0:
        return 1000000.0
    if ratio > 0.7:
        return -(gap ** 2)
    if gap <= 5:
        return 1000.0 - gap
    return -(gap + gap ** 0.5)