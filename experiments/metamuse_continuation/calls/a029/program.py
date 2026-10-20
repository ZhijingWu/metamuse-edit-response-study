def score(remaining, item, capacity, index, n_bins):
    free = remaining - item
    norm_free = free / capacity
    norm_item = item / capacity
    # Best fit prefers smallest remaining space (largest item relative to remaining)
    fit_score = (item / remaining) ** 2
    # Exponential penalty for near-full bins to avoid micro-fragmentsation
    space_penalty = 1.0 - exp(-8.0 * norm_free)
    # Balance index weight with n_bins to prevent premature index domination
    index_weight = min(1.0, n_bins / 16.0) * 0.2
    index_penalty = index_weight * index / max(n_bins, 1)
    # Reward bins that are already somewhat full but still have good fit
    fullness_bonus = (1.0 - norm_free) * norm_item
    return fit_score + space_penalty + fullness_bonus - index_penalty
