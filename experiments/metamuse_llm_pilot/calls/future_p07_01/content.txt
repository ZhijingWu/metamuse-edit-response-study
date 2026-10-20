def score(remaining, item, capacity, index, n_bins):
    slack = remaining - item
    used = capacity - remaining
    pop = used // max(item, 1)
    fit = -((slack - 12) ** 2)
    bonus = (pop - 1) * 7
    return fit + bonus