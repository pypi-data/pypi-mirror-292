import datetime as dt
from dataclasses import dataclass
import pandas as pd
from enum import Enum, auto



type CandleArray = list[Candle]


class Dir(Enum):
    UP = auto()
    DOWN = auto()
    DOJI = auto()


@dataclass
class Candle:
    open: float
    high: float
    low: float 
    close: float
    time: dt.datetime
    bar_index: int
    
    @property
    def dir(self):
        x = ''
        if self.open>self.close:
            x = Dir.DOWN
        elif self.close>self.open:
            x = Dir.UP
        else:
            x = Dir.DOJI
        return x   

    @property
    def truedate(self)->dt.date:
        """
        function to generate truedate for a candle
        """
        
        
        truedate: dt.date = self.time
        if truedate.time() >= dt.time(18,0):
            truedate = self.time + dt.timedelta(1)
        
        truedate = truedate.date()
        return truedate

def to_candle_array(data: pd.DataFrame) -> CandleArray:
    candles: CandleArray = []
    
    for _, row in data.iterrows(): # type: ignore
        candle = Candle(row['open'],row['high'],row['low'],row['close'],row['datetime']) # type: ignore
        candles.append(candle) # type: ignore
    
    return candles
 

    