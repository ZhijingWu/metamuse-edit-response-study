def score(remaining, item, capacity, index, n_bins):
    tightness = (capacity - remaining) / capacity
    weight = item / capacity
    return tightness * weight + tightness * tightness * (1.0 - weight) + 1.0 / (index + 2)
