class TradeSettings:
    def __init__(self, settings_obj, pair):
        self.n_ma = settings_obj["n_ma"]
        self.n_std = settings_obj["n_std"]
        self.max_spread = settings_obj["max_spread"]
        self.min_gain = settings_obj["min_gain"]
        self.risk_reward = settings_obj["risk_reward"]


    def __repr__(self) -> str:
        return str(vars(self))