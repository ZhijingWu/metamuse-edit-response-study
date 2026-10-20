def score(remaining, item, capacity, index, n_bins):
    gap = remaining - item
    used = capacity - remaining
    norm_item = item / capacity
    norm_gap = gap / capacity
    norm_used = used / capacity
    tightness = (norm_item * norm_gap) ** 2
    pop_affinity = (1.0 + norm_used ** 2)
    idx_cost = (1.0 - index / (index + 1.0)) * 0.01
    return tightness * pop_affinity - idx_cost
