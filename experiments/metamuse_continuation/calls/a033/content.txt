def score(remaining, item, capacity, index, n_bins):
    u = remaining - item
    fullness = capacity - remaining
    return (fullness ** 2) + (100 * u) - (u * u // 30) - (u * item // 40)