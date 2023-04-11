from api.oanda_api import OandaApi
from architecture.instrument_collection import instrument_collection
from simulation.ma_cross import run_ma_simulation
# rom simulation.ema_macd_start import run_ema_macd
from simulation.ema_macd_start_mp import run_ema_macd
from dateutil import parser
from architecture.collect_data import run_collection

if __name__ == '__main__':
    api = OandaApi()

    # instrument_collection.CreateNewInstrumentsFile(api.get_account_instruments(), "./data")
    
    instrument_collection.LoadInstruments("./data")
    # run_collection(instrument_collection, api)

    # run_ma_simulation()
    # run_ema_macd(instrument_collection)
    run_ema_macd(instrument_collection)