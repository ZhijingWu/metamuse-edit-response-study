def score(remaining, item, capacity, index, n_bins):
    u = remaining / capacity
    i = item / capacity
    if i < 0.2:
        return remaining - item
    elif i < 0.4:
        return remaining - item + 100 * u * u
    elif i < 0.6:
        return remaining - item + 400 * u * u
    else:
        return remaining - item + 900 * u * u
