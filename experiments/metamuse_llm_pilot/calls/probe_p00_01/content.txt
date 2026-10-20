def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    gap = remaining - item
    fullness = used / capacity
    rel_item = item / capacity
    tightness = 1.0 - gap / capacity
    if gap == 0:
        return 100000.0 - index * 0.001
    if gap < 3:
        return 50000.0 / (gap + 0.1) + fullness * 100.0 - index * 0.001
    if rel_item > 0.5:
        return tightness * 200.0 + fullness * 50.0 - log(gap + 1.0) * 2.0 - index * 0.001
    if fullness > 0.75:
        return 30.0 / (gap + 1.0) + fullness * 80.0 + tightness * 20.0 - index * 0.001
    if gap > 50:
        return fullness * 60.0 - sqrt(gap) * 1.5 - index * 0.001
    return fullness * 70.0 - log(gap + 1.0) * 5.0 + tightness * 15.0 - index * 0.001