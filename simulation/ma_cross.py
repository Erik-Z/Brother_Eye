import os.path
from datetime import date
from typing import Any, Dict, List, Callable
import pandas as pd
from models.instrument import Instrument
from architecture.instrument_collection import instrument_collection as ic
from simulation.ma_excel import create_moving_average_result

class MovingAverageResult:
    def __init__(
                self, 
                df_trades           : pd.DataFrame, 
                currency_pair       : str,
                granularity         : str, 
                moving_average_long : str, 
                moving_average_short: str) -> None:
        self.df_trades = df_trades
        self.currency_pair = currency_pair
        self.granularity = granularity
        self.moving_average_long = moving_average_long
        self.moving_average_short = moving_average_short
        self.result = self.get_results()

    def __repr__(self):
        return str(self.result)


    def get_results(self) -> Dict[str, Any]:
        return dict(
            currency_pair = self.currency_pair,
            number_of_trades = self.df_trades.shape[0],
            total_gain = int(self.df_trades.GAIN.sum()),
            average_gain = int(self.df_trades.GAIN.mean()),
            minimum_gain = int(self.df_trades.GAIN.min()),
            maximum_gain = int(self.df_trades.GAIN.max()),
            moving_average_long = self.moving_average_long,
            moving_average_short = self.moving_average_short,
            cross = f"{self.moving_average_short}_{self.moving_average_long}",
            granularity = self.granularity
        )


BUY = 1
SELL = -1
NONE = 0


get_ma_col: Callable[[str], str]= lambda x: f"MA_{x}"
add_cross_col: Callable[[pd.DataFrame], str] = lambda x: f"{x.moving_average_short}_{x.moving_average_long}"



def is_trade(row) -> int:
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    else:
        return NONE


def save_df_to_file(df, filename):
    if os.path.isfile(filename):
        dataframe_from_file = pd.read_pickle(filename)
        df = pd.concat([dataframe_from_file, df])
    df.reset_index(inplace=True, drop=True)
    df.to_pickle(filename)
    print(filename, df.shape)
    print(df.tail(2))

def get_full_path(filepath, filename):
    today = date.today()
    return f"{filepath}/{filename}_{today.strftime('%Y%m%d')}.pkl"


def process_trades(results_list : List[MovingAverageResult], filename: str):
    df = pd.concat([x.df_trades for x in results_list])
    save_df_to_file(df, filename)


def process_cumulative_results(results_list: List[MovingAverageResult], filename: str):
    results = [x.result for x in results_list]
    df = pd.DataFrame.from_dict(results)
    save_df_to_file(df, filename)


def process_results(results_list: List[MovingAverageResult], filepath):
    process_cumulative_results(results_list, get_full_path(filepath, "ma_results"))
    process_trades(results_list, get_full_path(filepath, "ma_trades"))
    # results = [x.result for x in results_list]
    # df = pd.DataFrame.from_dict(results)
    # print(df)
    # print(results_list[0].df_trades.head(2))


def load_price_data(
        currency_pair:      str, 
        granularity:        str, 
        moving_averages:    set[int]) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_pickle(f"./data/forex/{currency_pair}_{granularity}.pkl")
    for moving_average in moving_averages:
        df[get_ma_col(moving_average)] = df.mid_c.rolling(window=moving_average).mean()
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_trades(df_assess: pd.DataFrame, instrument: Instrument, granularity: str) -> pd.DataFrame:
    df_trades = df_assess[df_assess.TRADE != NONE].copy()
    df_trades["DIFF"] = df_trades.mid_c.diff().shift(-1)
    df_trades.fillna(0, inplace=True)
    df_trades["GAIN"] = df_trades.DIFF / instrument.pip_location * df_trades.TRADE
    df_trades["granularity"] = granularity
    df_trades["currency_pair"] = instrument.name
    df_trades["cumulative_gain"] = df_trades.GAIN.cumsum()
    return df_trades


def assess_pair(
        price_data:             pd.DataFrame, 
        moving_average_long:    str, 
        moving_average_short:   str,
        granularity:            str, 
        instrument:             Instrument) -> MovingAverageResult:
    df_assess: pd.DataFrame = price_data.copy()
    df_assess['DELTA'] = df_assess[moving_average_short] - df_assess[moving_average_long]
    df_assess['DELTA_PREV'] = df_assess["DELTA"].shift(1)
    df_assess["TRADE"] = df_assess.apply(is_trade, axis=1)
    df_trades = get_trades(df_assess, instrument, granularity)
    df_trades["moving_average_long"] = moving_average_long
    df_trades["moving_average_short"] = moving_average_short
    df_trades["cross"] = df_trades.apply(add_cross_col, axis=1)
    return MovingAverageResult(df_trades, instrument.name, granularity, moving_average_long, moving_average_short)


def analyse_pair(
            instrument:     Instrument, 
            granularity:    str, 
            ma_long:        List[int], 
            ma_short:       List[int],
            filepath:       str):
    moving_averages: set[int] = set(ma_long + ma_short)
    currency_pair: str = instrument.name

    price_data: pd.DataFrame = load_price_data(currency_pair, granularity, moving_averages)
    results_list =[]
    for moving_average_long in ma_long:
        for moving_average_short in ma_short:
            if moving_average_long <= moving_average_short: continue
            moving_average_result = assess_pair(
                price_data, 
                get_ma_col(moving_average_long),
                get_ma_col(moving_average_short),
                granularity,
                instrument
            )

            #print(moving_average_result)
            results_list.append(moving_average_result)
    process_results(results_list, filepath)
            

def run_ma_simulation(
        currencies:     List[str]=["CAD","JPY", "GBP", "NZD"],
        granularities:  List[str]=["H1"],
        ma_long:        List[int]=[20,40],
        ma_short:       List[int]=[10],
        filepath:       str="./data") -> None:
    ic.LoadInstruments(filepath)
    for granularity in granularities:
        for currency1 in currencies:
            for currency2 in currencies:
                currency_pair = f"{currency1}_{currency2}"
                if currency_pair in ic.instruments.keys():
                    analyse_pair(ic.instruments[currency_pair], granularity, ma_long, ma_short, filepath)
        create_moving_average_result(granularity)

