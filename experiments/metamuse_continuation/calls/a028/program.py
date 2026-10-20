def score(remaining, item, capacity, index, n_bins):
    fit = (item / remaining) ** 2
    idx_pref = 1.0 / (index + 1)
    return idx_pref + fit
