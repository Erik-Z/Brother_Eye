from dateutil import parser

class OpenTrade:

    def __init__(self, api_obj):
        self.id = api_obj["id"]
        self.instrument = api_obj["instrument"]
        self.currentUnits = float(api_obj["currentUnits"])
        self.price = float(api_obj["price"])
        self.realizedPL = api_obj["realizedPL"]
        self.unrealizedPL = api_obj["unrealizedPL"]
        self.marginUsed = api_obj["marginUsed"]

    def __repr__(self) -> str:
        return str(vars(self))