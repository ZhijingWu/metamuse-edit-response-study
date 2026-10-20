def score(remaining, item, capacity, index, n_bins):
    u = capacity - remaining
    f = remaining - item
    r = remaining / capacity
    i = item / capacity
    u2 = u * u
    f2 = f * f
    c2 = capacity * capacity
    t = (u2 - f2) / c2
    w = u / capacity
    p = w * (1.0 - w)
    s = t * (1.0 + 4.0 * p) + 2.0 * p * (1.0 - 2.0 * p)
    s = s - 3.5 * r * i
    b = 1.0 - r
    s = s + 2.0 * b * b * i
    s = s - 0.15 * p
    s = s - 0.002 * index
    return s
