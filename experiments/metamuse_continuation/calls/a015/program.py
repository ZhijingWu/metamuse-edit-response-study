def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    base = r / capacity
    return base * exp(-r) if r < 1 else base * sqrt(r)
