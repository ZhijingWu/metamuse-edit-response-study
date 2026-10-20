def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    fill = (capacity - remaining) / capacity
    zone = min(max(fill, 0.0), 1.0)
    adj = 20.0 + 8.0 * (zone - 0.5)
    penalty = (gap - adj) ** 2
    if gap <= 5:
        penalty = penalty - 400.0
    elif gap <= 15:
        penalty = penalty - 200.0
    return -penalty
