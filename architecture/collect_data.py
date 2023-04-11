import pandas as pd
import datetime
from dateutil import parser
from architecture.instrument_collection import InstrumentCollection
from api.oanda_api import OandaApi


CANDLE_COUNT = 3000
INCREMENTS = {
    "M5" : 5 * CANDLE_COUNT,
    "H1" : 60 * CANDLE_COUNT,
    "H4" : 240 * CANDLE_COUNT,
}


def save_file(df: pd.DataFrame, file_prefix: str, granularity: str, currency_pair: str):
    filename = f"{file_prefix}{currency_pair}_{granularity}.pkl"
    df.drop_duplicates(subset=['time'], inplace=True)
    df.sort_values(by="time", inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.to_pickle(filename)
    print(f"*** {currency_pair} {granularity} {df.time.min()} {df.time.max()} -> {df.shape[0]} ***")

    
def fetch_candles(
        currency_pair:  str, 
        granularity:    str, 
        date_from:      datetime.datetime, 
        date_to:        datetime.datetime,
        api:            OandaApi) -> pd.DataFrame:
    attempts = 0
    while attempts < 3:
        candles = api.get_candles_df(
            currency_pair, 
            granularity=granularity,
            date_from=date_from,
            date_to=date_to,
        )

        if candles is not None:
            break

        attempts += 1

    if candles is not None and not candles.empty:
        return candles
    return None


def collect_data(
        currency_pair:  str, 
        granularity:    str, 
        date_from:      str, 
        date_to:        str, 
        file_prefix:    str, 
        api:            OandaApi):
    time_step = INCREMENTS[granularity]
    from_date = parser.parse(date_from)
    end_date = parser.parse(date_to)

    candle_dataframes = []

    to_date = from_date
    while to_date < end_date:
        to_date = from_date + datetime.timedelta(minutes=time_step)
        if to_date > end_date: to_date = end_date

        candles = fetch_candles(currency_pair, granularity, from_date, to_date, api)
        if candles is not None:
            candle_dataframes.append(candles)
            print(f"{currency_pair} {granularity} {from_date} {to_date} -> {candles.shape[0]} Candles")
        else:
            print(f"{currency_pair} {granularity} {from_date} {to_date} -> No Candles")

        from_date = to_date

    if len(candle_dataframes) > 0:
        results_dataframe = pd.concat(candle_dataframes)
        save_file(results_dataframe, file_prefix, granularity, currency_pair)
    else:
        print(f"{currency_pair} {granularity} -> No Data")


def run_collection(instrument_collection: InstrumentCollection, api: OandaApi):
    currencies = ["AUD", "CAD", "JPY", "USD", "EUR", "GBP", "NZD"]
    for currency1 in currencies:
        for currency2 in currencies:
            currency_pair = f"{currency1}_{currency2}"
            if currency_pair not in instrument_collection.instruments.keys(): continue
            for granularity in ["M5","H1", "H4"]:
                print(currency_pair, granularity)
                collect_data(
                    currency_pair, 
                    granularity, 
                    "2010-01-01T00:00:00Z",
                    "2021-12-31T00:00:00Z",
                    "./data/forex/",
                    api
                )