def score(remaining, item, capacity, index, n_bins):
    w = remaining - item
    return (w * w - w + 1) / (remaining + 1)
