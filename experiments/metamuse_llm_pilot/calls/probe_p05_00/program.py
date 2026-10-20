def score(remaining, item, capacity, index, n_bins):
    if remaining == item:
        return 100.0
    return (remaining - item) / remaining
