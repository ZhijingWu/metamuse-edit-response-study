def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    g = gap - 20
    return -(g * g) + 5.0 * (1.0 - 1.0 / (1.0 + gap * gap * 0.005)) - index * 0.005
