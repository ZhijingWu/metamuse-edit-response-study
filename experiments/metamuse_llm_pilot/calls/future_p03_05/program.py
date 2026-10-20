def score(remaining, item, capacity, index, n_bins):
    r = remaining - item
    c = capacity - remaining
    t = r / capacity
    i = item / capacity
    p = 1.0 - t
    w = 1.0 - i
    return p * p * p * p + (t * w * w) * 0.001 + (i * i) * (1.0 / (c + 1.0)) * 0.0005
