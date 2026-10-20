def score(remaining, item, capacity, index, n_bins):
    x = remaining - item
    t = remaining / capacity
    s = item / capacity
    if x < 1:
        p = 4.0
    elif x < 3:
        p = 2.5
    elif x < 8:
        p = 1.5
    else:
        p = 0.8
    fit = x ** p
    c1 = (1.0 - s) * (1.0 - t)
    c2 = t * t
    c3 = 1.0 - abs(t - s)
    bonus = 5.0 * c1 + 3.0 * c2 + 2.0 * c3
    return -fit + bonus - index * 0.001
