def score(remaining, item, capacity, index, n_bins):
    u = remaining - item
    if u < 20:
        return -abs(u - 20) * (1.0 + (20 - u) / 20.0)
    else:
        return -sqrt(u - 20 + 1.0) - 19.0
