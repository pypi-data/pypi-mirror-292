import pandas as pd
import datetime as dt

def time_indices(date: dt.date, time: dt.time, data: pd.DataFrame) -> list[int]:
    data['time'] = data['datetime'].dt.time
    
    filtered = data[(data['time']== time) & (data['truedate'] == date)]
    inds = filtered.index #type: ignore
    
    
    index_list = [i for i in inds] #type: ignore
    
    return index_list #type: ignore


def generate_datarange(ind: int, dev: int, data: pd.DataFrame) -> pd.DataFrame:
    
    spliced = data.iloc[ind-dev:ind+dev]
    return spliced