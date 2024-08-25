import pandas as pd
import datetime as dt

type filename = str
type ticker = str
type timeframe = str



ROOT = 'price_data/'

def load_data(ticker: ticker, interval: timeframe) -> pd.DataFrame:
    
    file_to_pull: filename = ROOT+ticker+'_'+interval+'.pkl'
    df: pd.DataFrame = pd.read_pickle(file_to_pull)
    return df

def true_date_processor(date: dt.datetime) -> dt.date:
    ADJ = dt.timedelta(days = 1)
    _d = date
    
    if date.hour >= 18:
        _d = _d + ADJ
        
    return _d.date()
    

def add_truedate(data: pd.DataFrame) -> pd.DataFrame:
    
    data['truedate'] = data['datetime'].apply(lambda x: true_date_processor(x)) #type: ignore
    return data

if __name__ == '__main__':
    data = load_data('ES','5M')
    processed = add_truedate(data)
    print(processed)
    
    

