import pytest
from importlib import import_module
import os 
import requests
import logging as log 
import pandas as pd 


def get_market_data(interval :str = "4h", symbol :str = "TNA", start_date :int = 1716696000000, end_date :int = 1724530861868):

    market_data_url = os.getenv('MARKET_DATA_URL', f'http://market-data.stage.tredops.com/symbol/{symbol}/intreval/{interval}/start_date/{str(start_date)}/end_date/{end_date}')

    data = requests.get(market_data_url, verify=False)

    if data.status_code != 200:
        log.error("Not was possible collect the market data")
        return 

    data_market = data.json()

    df = pd.DataFrame(data_market)

    return df 

@pytest.mark.parametrize("strategy", [
    "ema", 
    "rsi", 
    "macd"
])
def test_eval_strategies(strategy):

    libray_trading = f"pyttrading.strategies.{strategy}"
    model_module = import_module(libray_trading)
    strategy = getattr(model_module, "Strategy")
    strategy_model = strategy(strategy_name=strategy)


    df = get_market_data(interval="1h", start_date=1698793200000, end_date=1711922400000)

    assert len(df) > 200, "Not found data from remote provider"

    method, best_return, best_parameters =  strategy_model.experiment(df=df.dropna())
    
    best_return = float(best_return)
    log.info(f"End optimization method {method} best_return: {best_return}")

    assert best_return > 0.3
    
    df_test =  get_market_data(interval="1h", start_date=1711922400000, end_date=1722463200000)

    result = strategy_model.eval(df=df_test.dropna(), params=best_parameters)

    assert len(result[result['actions'] == 1]) > 1, "Not was get the actions igual to 1"
    assert len(result[result['actions'] == 2]) > 1, "Not was get the actions igual to 2"

