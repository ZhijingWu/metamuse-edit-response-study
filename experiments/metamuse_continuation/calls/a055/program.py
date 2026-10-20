def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    fill = capacity - remaining
    return item - fill * gap * gap / (capacity * capacity)
