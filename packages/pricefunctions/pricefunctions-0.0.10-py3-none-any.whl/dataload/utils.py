import dataload.loadassets as loadassets
import pandas as pd


def processing(ticker: str, interval: str) -> pd.DataFrame:
    
    data = loadassets.load_data(ticker, interval)
    processed = loadassets.add_truedate(data)
    return processed


def load_daily(ticker: str) -> pd.DataFrame:
    return processing(ticker, 'D')

def load_15M(ticker: str) -> pd.DataFrame:
    return processing(ticker, '15M')

def load_5M(ticker: str) -> pd.DataFrame:
    return processing(ticker, '5M')