import datetime as dt

class CandleTiming:
    def __init__(self, last_time):
        self.last_time = last_time
        self.is_ready = False

    
    def __repr__(self) -> str:
        return str(vars(self))