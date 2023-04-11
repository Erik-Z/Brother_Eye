import requests
import constants.defs as defs
import pandas as pd
import json
from dateutil import parser
from datetime import datetime
from architecture.instrument_collection import instrument_collection as ic
from models.open_trade import OpenTrade


class OandaApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {defs.API_KEY}",
            "Content-Type": "application/json"
        })

    def make_request(self, url, verb="get", code=200, params=None, data=None, headers=None):
        full_url = f"{defs.BASE_URL}/{url}"

        if data is not None:
            data = json.dumps(data)

        try:
            if verb == "get":
                response = self.session.get(full_url, params=params, data=data, headers=headers)
            elif verb == "post":
                response = self.session.post(full_url, params=params, data=data, headers=headers)
            elif verb == "put":
                response = self.session.put(full_url, params=params, data=data, headers=headers)
            
            if response == "None": return False, {"error": "Invalid Verb"} 
            
            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()

        except Exception as error:
            return False, {"Exception": error} 

    def __get_account_endpoint(self, endpoint, data_key):
        url = f"accounts/{defs.ACCOUNT_ID}/{endpoint}"
        ok, data = self.make_request(url)
        if ok and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_endpoint()", data)
            return None

    def get_account_summary(self):
        return self.__get_account_endpoint("summary", "account")

    def get_account_instruments(self):
        return self.__get_account_endpoint("instruments", "instruments")


    def fetch_candles(self, 
            currency_pair:      str, 
            count:          int=10, 
            granularity:    str="H1", 
            price:          str="MBA",
            date_from:      datetime=None,
            date_to:        datetime=None):
        url = f"instruments/{currency_pair}/candles"
        params = dict(
            granularity = granularity,
            price = price
        )

        if date_from is not None and date_to is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = datetime.strftime(date_from, date_format)
            params["to"] = datetime.strftime(date_to, date_format)
        else:
            params["count"] = count

        ok, data = self.make_request(url, params=params)
        if ok and "candles" in data:
            return data["candles"]
        else:
            print("ERROR fetch_candles()", params, data)
            return None


    def get_candles_df(self, currency_pair: str, **kwargs):
        data = self.fetch_candles(currency_pair, **kwargs)
        
        if data is None: return None
        if len(data) == 0: return pd.DataFrame()

        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']
        final_data = []
        for candle in data:
            if candle['complete'] == False: continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            final_data.append(new_dict)
            for p in prices:
                if p not in candle: break
                for o in ohlc:
                    new_dict[(f"{p}_{o}")] = float(candle[p][o])
        df = pd.DataFrame.from_dict(final_data)
        return df


    def create_candles_file(self, pair_name: str, count: int =10, granularity: str ="H1"):
        code, data = self.fetch_candles(pair_name, count=count, granularity="H4")
        if code != 200:
            print("API Error", pair_name, data)
            return
        if len(data) == 0:
            print("No data found")
            return
        candles_df = self.get_candles_df(data)
        candles_df.to_pickle(f"../data/{pair_name}_{granularity}.pkl")
        print(f"{pair_name} {granularity} {candles_df.shape[0]} candles, {candles_df.time.min()} {candles_df.time.max()}")


    def get_last_completed_candle_time(self, pair_name, granularity):
        df = self.get_candles_df(pair_name, granularity=granularity, count=10)
        if df.shape[0] == 0:
            return None
        return df.iloc[-1].time

    """
    Places a trade and returns trade ID if successful. Returns None if it isn't
    """
    def place_trade(self, pair_name: str, units: float, direction: int, stop_loss: float=None, take_profit: float=None) -> int:
        url = f"accounts/{defs.ACCOUNT_ID}/orders"

        instrument = ic.instruments[pair_name]
        
        if direction == defs.SELL:
            units *= -1

        units = round(units, instrument.trade_units_precision)

        data = dict(
            order=dict(
                units=str(units),
                instrument=pair_name,
                type="MARKET"
            )
        )

        if stop_loss is not None:
            sld = dict(price=str(round(stop_loss, instrument.display_precision)))
            data["order"]["stopLossOnFill"] = sld

        if take_profit is not None:
            tpd = dict(price=str(round(take_profit, instrument.display_precision)))
            data["order"]["takeProfitOnFill"] = tpd

        ok, response = self.make_request(url, verb="post", code=201, data=data)
        
        if ok and "orderFillTransaction" in response:
            return response["orderFillTransaction"]["id"]
        elif "orderCancelTransaction" in response:
            print(f"Trade Cannot be placed. Reason: {response['orderCancelTransaction']['reason']}")

        return None
    

    def close_trade(self, trade_id: int):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}/close"
        ok, _ = self.make_request(url, verb="put", code=200)

        if ok:
            print(f"Closed Trade {trade_id} successfully")
        else:
            print(f"Failed to close trade {trade_id}")

    
    def get_open_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}"
        ok, response = self.make_request(url)

        if ok and "trade" in response:
            return OpenTrade(response["trade"])


    def get_open_trades(self):
        url = f"accounts/{defs.ACCOUNT_ID}/openTrades"
        ok, response = self.make_request(url)

        if ok and "trades" in response:
            return [OpenTrade(x) for x in response["trades"]]