def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    util = used / capacity
    w = 1.0 + util * util
    gap = remaining - item
    if gap == 0:
        return 1e12 * w
    elif gap <= 3:
        return 1e6 * w / gap
    return w / (gap + 1)
