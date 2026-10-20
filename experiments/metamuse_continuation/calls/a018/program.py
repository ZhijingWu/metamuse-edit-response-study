def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    base = -abs(gap - 20)
    if gap >= 20:
        return base + (gap - 20) ** 2 / 200 - index / (n_bins + 1)
    else:
        tight = 20 - gap
        return base - tight ** 2 / 50 - index / (n_bins + 1)
