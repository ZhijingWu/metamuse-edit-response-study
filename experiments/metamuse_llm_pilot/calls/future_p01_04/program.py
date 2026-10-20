def score(remaining, item, capacity, index, n_bins):
    slack = remaining - item
    tight = 1.0 / (slack + 1.0)
    near_full = slack**0.5 / (remaining + 1.0)
    small_penalty = 500.0 / (slack + 1.0)**3
    bonus = item * tight
    return bonus + near_full - small_penalty - index * 1e-6
