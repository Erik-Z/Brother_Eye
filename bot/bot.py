import json
import time
from architecture.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.oanda_api import OandaApi
from bot.candle_manager import CandleManager

class Bot:

    ERROR_LOG = "error"
    MAIN_LOG = "main"
    GRANULARITY = "M1"
    SLEEP = 10

    def __init__(self):
        self.load_settings()
        self.setup_logs()

        self.api = OandaApi()
        self.candle_manager = CandleManager(self.trade_settings, self.log_message, Bot.GRANULARITY)

        self.log_to_main("Bot Started")
        self.log_to_error("Bot Started")


    def load_settings(self):
        with open("./bot/settings.json", "r") as f:
            data = json.loads(f.read())
            self.trade_settings = { k: TradeSettings(v, k) for k, v in data.items()}


    def setup_logs(self):
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(f"Bot Started with \n {self.trade_settings}")


    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)


    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)


    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)


    def process_candles(self, triggered: list[str]):
        if len(triggered) > 0:
            self.log_message(f"process_candle triggered: {triggered}", Bot.MAIN_LOG)
            for p in triggered:
                last_time = self.candle_manager.timings[p].last_time


    def run(self):
        while True:
            time.sleep(Bot.SLEEP)
            self.process_candles(self.candle_manager.update_timings())
