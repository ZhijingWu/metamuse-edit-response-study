def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    c = capacity - item
    near_full = 1 if gap < 20 else 0
    near_cap = 1 if c < 20 else 0
    w = 4 + 3 * near_cap
    return -(gap - 20) * (gap - 20) - w * near_full
