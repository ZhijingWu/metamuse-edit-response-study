def score(remaining, item, capacity, index, n_bins):
    leftover = remaining - item
    if leftover == 0:
        return 1000.0
    if leftover < 5:
        return -leftover * 10.0
    return -leftover - sqrt(leftover)
