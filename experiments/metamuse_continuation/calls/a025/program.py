def score(remaining, item, capacity, index, n_bins):
    leftover = remaining - item
    if leftover < 20:
        return item - remaining + leftover / (item + 1)
    else:
        return item ** 1.2 - remaining
