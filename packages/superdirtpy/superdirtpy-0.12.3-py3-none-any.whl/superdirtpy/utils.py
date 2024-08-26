def zmap(
    v: float, low_in: float, high_in: float, low_out: float, high_out: float
) -> float:
    v = min(max(v, low_in), high_in)
    percent = (v - low_in) / (high_in - low_in)
    return percent * (high_out - low_out) + low_out
