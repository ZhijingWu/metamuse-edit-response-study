def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    if gap == 0:
        return 1e12
    fullness = capacity - gap
    if gap <= 3:
        p = (capacity - gap) ** 3 + 1.0 / (gap + 1)
    elif gap <= 10:
        p = fullness * (capacity - gap + 1)
    else:
        p = fullness + 1.0 / (gap + 1)
    return p - index * 1e-4
