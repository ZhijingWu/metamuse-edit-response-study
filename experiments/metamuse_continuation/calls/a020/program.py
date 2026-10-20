def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    new_used = used + item
    waste = remaining - item
    fill_ratio = new_used / capacity
    waste_ratio = waste / capacity
    item_ratio = item / capacity
    pop = used / 10
    pop_cost = pop * item_ratio
    fill_score = fill_ratio * fill_ratio * 100
    waste_score = waste_ratio * waste_ratio * 50
    return fill_score - waste_score - pop_cost
