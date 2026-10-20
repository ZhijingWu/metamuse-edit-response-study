def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    x = gap - 20
    p = x * x
    if gap <= 5:
        return 1e6 - p
    if gap <= 30:
        return -p
    return -p * (1 + gap / 50)
