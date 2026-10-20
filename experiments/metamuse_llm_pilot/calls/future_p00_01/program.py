def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    n_items = used // item if used > 0 and item > 0 and used >= item else 0
    fit = remaining - item
    return (n_items + 1) ** 2 / (fit + 1.0)