import pandas as pd

HANGING_MAN_BODY_SIZE = 15.0
HANGING_MAN_HEIGHT = 75.0
SHOOTING_STAR_HEIGHT = 25.0
SHOOTING_STAR_BODY_SIZE = 15.0
SPINNING_TOP_MIN = 40.0
SPINNING_TOP_MAX = 60.0
SPINNING_TOP_BODY_SIZE = 15.0
MARUBOZU_BODY_SIZE = 98.0
ENGULFING_FACTOR = 1.1

TWEEZER_BODY = 15.0
TWEEZER_HIGH_LOW = 0.01
TWEEZER_TOP_BODY = 40.0
TWEEZER_BOTTOM_BODY = 60.0

MORNING_STAR_BODY_SIZE_PREV_2 = 90.0
MORNING_STAR_BODY_SIZE_PREV = 10.0


def is_hanging_man(row: pd.Series):
    return row.body_bottom_percentage > HANGING_MAN_HEIGHT and row.body_percentage < HANGING_MAN_BODY_SIZE


def is_shooting_star(row: pd.Series):
    return row.body_top_percentage < SHOOTING_STAR_HEIGHT and row.body_percentage < SHOOTING_STAR_BODY_SIZE


def is_spinning_top(row: pd.Series):
    return row.body_top_percentage < SPINNING_TOP_MAX and \
        row.body_bottom_percentage > SPINNING_TOP_MIN and \
        row.body_percentage < SPINNING_TOP_BODY_SIZE


is_marubozu = lambda row: row.body_percentage > MARUBOZU_BODY_SIZE


def is_engulfing(row: pd.Series):
    if row.direction == row.direction_prev: return False
    return row.body_size > row.body_size_prev * ENGULFING_FACTOR


def is_tweezer_top(row: pd.Series):
    if abs(row.body_size_change) > TWEEZER_BODY: return False
    if row.direction == 1 or row.direction == row.direction_prev: return False
    if abs(row.low_change) > TWEEZER_HIGH_LOW or abs(row.high_change) > TWEEZER_HIGH_LOW: return False
    if row.body_top_percentage > TWEEZER_TOP_BODY: return False
    return True


def is_tweezer_bottom(row: pd.Series):
    if abs(row.body_size_change) > TWEEZER_BODY: return False
    if row.direction == -1 or row.direction == row.direction_prev: return False
    if abs(row.low_change) > TWEEZER_HIGH_LOW or abs(row.high_change) > TWEEZER_HIGH_LOW: return False
    if row.body_top_percentage < TWEEZER_BOTTOM_BODY: return False
    return True


def is_morning_star(row: pd.Series, direction=1):
    if row.body_percentage_prev_2 < MORNING_STAR_BODY_SIZE_PREV_2: return False
    if row.body_percentage_prev > MORNING_STAR_BODY_SIZE_PREV: return False
    if row.direction != direction or row.direction_prev_2 == direction: return False
    if direction == 1:
        if row.mid_c < row.mid_point_prev_2: return False
        return True
    else:
        if row.mid_c > row.mid_point_prev_2: return False
        return True


def apply_candle_pattern(df_an: pd.DataFrame):
    df_an['HANGING_MAN'] = df_an.apply(is_hanging_man, axis=1)
    df_an['SHOOTING_STAR'] = df_an.apply(is_shooting_star, axis=1)
    df_an['SPINNING_TOP'] = df_an.apply(is_spinning_top, axis=1)
    df_an['MARUBOZU'] = df_an.apply(is_marubozu, axis=1)
    df_an['ENGULFING'] = df_an.apply(is_engulfing, axis=1)
    df_an['TWEEZER_TOP'] = df_an.apply(is_tweezer_top, axis=1)
    df_an['TWEEZER_BOTTOM'] = df_an.apply(is_tweezer_bottom, axis=1)
    df_an['MORNING_STAR'] = df_an.apply(is_morning_star, axis=1)
    df_an['EVENING_STAR'] = df_an.apply(is_morning_star, axis=1, direction=-1)


def init_candle_properties(df: pd.DataFrame) -> pd.DataFrame:
    df_an = df.copy()
    direction = df_an.mid_c - df_an.mid_o
    body_size = abs(direction)
    direction = [1 if x >= 0 else -1 for x in direction]
    full_range = df_an.mid_h - df_an.mid_l
    body_percentage = (body_size / full_range) * 100
    body_lower = df_an[["mid_c", "mid_o"]].min(axis=1)
    body_upper = df_an[["mid_c", "mid_o"]].max(axis=1)
    body_bottom_percentage = ((body_lower - df_an.mid_l) / full_range) * 100
    body_top_percentage = ((body_upper - df_an.mid_l) / full_range) * 100
    
    mid_point = full_range / 2 + df_an.mid_l

    low_change = df_an.mid_l.pct_change() * 100
    high_change = df_an.mid_h.pct_change() * 100
    body_size_change = body_size.pct_change() * 100

    df_an["body_lower"] = body_lower
    df_an["body_upper"] = body_upper
    df_an["body_bottom_percentage"] = body_bottom_percentage
    df_an["body_top_percentage"] = body_top_percentage
    df_an["body_percentage"] = body_percentage
    df_an['body_percentage_prev'] = df_an.body_percentage.shift(1)
    df_an['body_percentage_prev_2'] = df_an.body_percentage.shift(2)
    df_an["direction"] = direction
    df_an['direction_prev'] = df_an.direction.shift(1)
    df_an['direction_prev_2'] = df_an.direction.shift(2)
    df_an["body_size"] = body_size
    df_an['body_size_prev'] = df_an.body_size.shift(1)
    df_an["low_change"] = low_change
    df_an["high_change"] = high_change
    df_an["body_size_change"] = body_size_change
    df_an["mid_point"] = mid_point
    df_an["mid_point_prev_2"] = mid_point.shift(2)
    return df_an

def apply_candle_patterns(df: pd.DataFrame):
    df_an = init_candle_properties(df)
    apply_candle_pattern(df_an)
    return df_an