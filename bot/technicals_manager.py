from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
from collections.abc import Callable

ADD_ROWS = 20

def get_trade_decision(candle_time: str, pair: str, granularity: str, api: OandaApi, 
                        trade_settings: TradeSettings, log_message: Callable[[str, str], None]):
    
    max_rows = trade_settings.n_ma + 1 + ADD_ROWS
    log_message(f"tech_manager: max_rows: {max_rows} candle_time:{candle_time} ", pair)

    return None