def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    gap = remaining - item
    fit = item / capacity
    u = used / capacity
    g = gap / capacity
    if u < 0.5:
        return fit * 2.0 - g * g * 0.5
    elif u < 0.75:
        return fit * 1.5 + u - g * g
    else:
        return fit + u * 2.0 - g * g * 3.0
