def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    base = -((gap - 20) * (gap - 20))
    if gap <= 3:
        return base + 1500
    elif gap <= 10:
        return base + 600 - gap * 10
    elif gap <= 25:
        return base + 200 - gap * 4
    elif gap <= 50:
        return base + 50 - gap
    else:
        return base - (gap - 50)
