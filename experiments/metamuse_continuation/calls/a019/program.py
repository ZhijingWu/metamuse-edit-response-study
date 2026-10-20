def score(remaining, item, capacity, index, n_bins):
    used = capacity - remaining
    # Heavily prefer bins that can perfectly fit the item.
    if remaining == item:
        return 1e8 - index
    # For non-perfect fits, score based on a combination of:
    # - High remaining space (keeps tight packing, avoids fragmentation)
    # - High used space (avoids spreading items across many bins)
    # - Small item size (small items are more flexible, place them in less optimal bins)
    # The weighted sum ensures tight fits and high usage bins are prioritized.
    return remaining * 1e4 + used * 1e2 - item * 1e2 - index
