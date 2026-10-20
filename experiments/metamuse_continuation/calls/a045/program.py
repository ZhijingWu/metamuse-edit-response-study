def score(remaining, item, capacity, index, n_bins):
    slack = remaining - item
    fullness = capacity - remaining
    if slack <= 10:
        t = -(fullness * fullness)
    else:
        t = remaining + item
    return -item + t
