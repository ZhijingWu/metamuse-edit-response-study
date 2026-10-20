def score(remaining, item, capacity, index, n_bins):
    space = remaining - item
    fit_score = 1.0 + 1.0 / (1.0 + space)
    idx_score = 1.0 / (index + 1)
    return fit_score * idx_score
