
from api.oanda_api import OandaApi
from architecture.instrument_collection import instrument_collection
import time

if __name__ == '__main__':
    api = OandaApi()
    instrument_collection.LoadInstruments("./data")
    #trade_id = api.place_trade("EUR_USD", 100, 1, stop_loss= 1.0000, take_profit=1.300)
    #api.get_open_trade(trade_id)
    #time.sleep(10)
    #api.close_trade(trade_id)

    print(api.get_last_completed_candle_time("EUR_USD", granularity="M5"))