import pandas as pd


def bollinger_bands(df: pd.DataFrame, n: int = 20, std_dev_step: int = 2):
    typical_price = (df.mid_h + df.mid_l + df.mid_c) / 3
    std_dev = typical_price.rolling(window=n).std()
    df["BB_MovingAverage"] = typical_price.rolling(window=n).mean()
    df["BB_Upperbound"] = df["BB_MovingAverage"] + std_dev * std_dev_step
    df["BB_Lowerbound"] = df["BB_MovingAverage"] - std_dev * std_dev_step
    return df


def average_true_range(df: pd.DataFrame, n: int = 14):
    prev_c = df.mid_c.shift(1)
    true_range1 = df.mid_h - df.mid_l
    true_range2 = abs(df.mid_h - prev_c)
    true_range3 = abs(prev_c - df.mid_l)
    true_range = pd.DataFrame({"true_range1": true_range1, "true_range2": true_range2, "true_range3": true_range3}).max(axis=1)
    df[f"average_true_range_{n}"] = true_range.rolling(window=n).mean()
    return df


def keltner_channels(df: pd.DataFrame, exponential_moving_averages=20, average_true_ranges=10):
    df["exponential_moving_average"] = df.mid_c.ewm(
                                            span = exponential_moving_averages, 
                                            min_periods = exponential_moving_averages
                                            ).mean()
    df = average_true_range(df, n=average_true_ranges)
    average_true_range_n = f"average_true_range_{average_true_ranges}"
    df["KC_Upperbound"] = df[average_true_range_n] * 2 + df.exponential_moving_average
    df["KC_Lowerbound"] = df.exponential_moving_average - df[average_true_range_n] * 2
    df.drop(average_true_range_n, axis=1, inplace=True)
    return df


def relative_strength_index(df: pd.DataFrame, n=14):
    alpha = 1.0 / n
    gains = df.mid_c.diff()

    wins = pd.Series([x if x >= 0 else 0.0 for x in gains], name="wins")
    losses = pd.Series([abs(x) if x < 0 else 0.0 for x in gains], name="losses")

    wins_rma = wins.ewm(min_periods=n, alpha=alpha).mean()
    losses_rma = losses.ewm(min_periods=n, alpha=alpha).mean()

    rs = wins_rma / losses_rma
    df[f"relative_strength_index_{n}"] = 100 - (100.0 / (1.0 + rs))
    return df


def moving_average_convergence_divergence(df: pd.DataFrame, n_fast=26, n_slow=12, n_signal=9):
    exponential_moving_average_long = df.mid_c.ewm(span=n_slow, min_periods=n_slow).mean()
    exponential_moving_average_short = df.mid_c.ewm(span=n_fast, min_periods=n_fast).mean()

    df["moving_average_convergence_divergence"] = exponential_moving_average_long - exponential_moving_average_short
    df["signal"] = df.moving_average_convergence_divergence.ewm(span=n_signal, min_periods=n_signal).mean()
    df["histogram"] = df.moving_average_convergence_divergence - df.signal

    return df