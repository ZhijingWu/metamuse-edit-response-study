def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    new_used = used + item
    space = remaining - item
    u = new_used / capacity
    fill = 1.0 / (space + 1)
    pop = 1.0 + used / (capacity + 1)
    return fill * (1.0 + u ** 2) * pop