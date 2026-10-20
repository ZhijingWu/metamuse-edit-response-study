def score(remaining, item, capacity, index, n_bins):
    fit = remaining - item
    norm = fit / capacity
    return -norm - 0.001 * (index + 1) * (1 - norm)
