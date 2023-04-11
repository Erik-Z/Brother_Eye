class Instrument:
    def __init__(self, name, instrument_type, display_name, pip_location, trade_units_precision, margin_rate, display_precision):
        self.name: str = name
        self.ins_type = instrument_type
        self.display_name = display_name
        self.pip_location = pow(10, pip_location)
        self.trade_units_precision = trade_units_precision
        self.margin_rate = float(margin_rate)
        self.display_precision = display_precision

    def __repr__(self) -> str:
        return str(vars(self))

    @classmethod
    def FromApiObject(cls, obj):
        return Instrument(
            obj["name"],
            obj["type"],
            obj["displayName"],
            obj["pipLocation"],
            obj["tradeUnitsPrecision"],
            obj["marginRate"],
            obj["displayPrecision"]
        )