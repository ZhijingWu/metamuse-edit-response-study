def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    pop = capacity - remaining
    s = item / capacity
    g = gap / capacity
    t = remaining / capacity
    x = gap - 20
    p = pop - 20
    return -(x * x) - 15 * (g * g) - 3 * (p * p) - 10 * g * s - 5 * t * s
