def score(remaining, item, capacity, index, n_bins):
    s = capacity - remaining
    x = remaining - item
    return x * x * (s + 1) * (item + 1)
