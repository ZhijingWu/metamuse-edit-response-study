def score(remaining, item, capacity, index, n_bins):
    x = remaining - item
    t = x * x
    c = (capacity - item) * (capacity - item)
    if x < 20:
        return -t - 80000.0 * (20 - x) / (x + 1)
    elif x < 50:
        return -t
    else:
        return -c - t
