def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    if remaining < item:
        return -1e9
    post = remaining - item
    u_ratio = used / capacity
    p_ratio = post / capacity
    if used > 0:
        affinity = (item / used) ** 2
    else:
        affinity = 0.0
    fill_bonus = (u_ratio ** 3) * 4.0
    post_penalty = (p_ratio ** 4) * 2.5
    return affinity + fill_bonus - post_penalty
