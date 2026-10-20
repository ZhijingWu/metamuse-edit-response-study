def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    u = used / capacity
    v = item / capacity
    r = remaining / capacity
    t = u + v / capacity
    fit = (1.0 - r) * (1.0 + t)
    item_p = 1.0 - abs(r - v)
    pop_b = 1.0 / (1.0 + u * u)
    w1 = 1.0 + v * v
    w2 = 0.5 * v
    w3 = 0.25
    return w1 * fit + w2 * item_p + w3 * pop_b
