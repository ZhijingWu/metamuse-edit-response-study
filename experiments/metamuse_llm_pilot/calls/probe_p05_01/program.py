def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    gap = remaining - item
    pop = used // item
    w1 = (gap / capacity) ** 2
    w2 = (item / capacity) * (item / remaining)
    w3 = 1.0 / (1.0 + pop)
    return w1 + w2 + w3
