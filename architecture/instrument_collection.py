import json
from models.instrument import Instrument
class InstrumentCollection:
    FILE_NAME = "instruments.json"
    API_KEYS = ["name", "type", "displayName", "pipLocation", "displayPrecision", "tradeUnitsPrecision", "marginRate"]

    def __init__(self) -> None:
        self.instruments = {}


    def LoadInstruments(self, path: str) -> None:
        self.instruments = {}
        file_name = f"{path}/{self.FILE_NAME}"
        with open(file_name, "r") as f:
            data = json.loads(f.read())
            for k, v in data.items():
                self.instruments[k] = Instrument.FromApiObject(v)


    def CreateNewInstrumentsFile(self, data, path) -> None:
        if data is None:
            print("Instrument data not found.")
            return

        instruments = {}
        for i in data:
            key = i['name']
            instruments[key] = {k: i[k] for k in self.API_KEYS}
        file_name = f"{path}/{self.FILE_NAME}"
        with open(file_name, "w") as f:
            f.write(json.dumps(instruments, indent=2))


    def PrintInstruments(self) -> None:
        [print(k,v) for k,v in self.instruments.items()]
        print(len(self.instruments.keys()), "instruments")

instrument_collection = InstrumentCollection()