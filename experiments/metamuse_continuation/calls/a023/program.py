def score(remaining, item, capacity, index, n_bins):
    f = remaining / capacity
    i = item / capacity
    r = f - i
    p = r ** 3 * 16.0
    if f < 0.25:
        p = p - 0.08
    elif f > 0.75:
        p = p - 0.04
    b = 1.0 - exp(-f * 6.0)
    c = 1.0 - exp(-i * 6.0)
    bc = b * c
    d = r * 8.0 * bc
    s = p + d
    if i > 0.7:
        s = s + 0.12 * r
    return s
