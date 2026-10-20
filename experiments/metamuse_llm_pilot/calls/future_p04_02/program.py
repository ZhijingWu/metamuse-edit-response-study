def score(remaining, item, capacity, index, n_bins):
    u = capacity - remaining
    if remaining <= 50:
        return 10000 - remaining * remaining
    else:
        return (remaining - item) + 200 * item / remaining
