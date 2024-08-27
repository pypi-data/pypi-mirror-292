from ta.trend import SMAIndicator
import logging as log
from scipy.optimize import minimize
import numpy as np
import os
from pyttrading.utils.pre_processing import remove_noise_trading
from ta.trend import MACD
from pyttrading.backtesting_custom.generic_backtesting import GenericBacktesting


params_default = [(6, 100), (4, 100), (4, 100)]
params_default = [(30, 100), (30, 100), (30, 100)]
params_default = [(100, 200), (100, 200), (100, 200)]



params_init = []
for param in params_default:
    param_low = param[0]
    params_init.append(param_low)


class Strategy: 

    def __init__(self, df=None, strategy_name :str = "StrategyName", bk_initial_money :float = 2000.0, bk_commission :float = 0.02):
        self.name = 'MACD'
        self.open_long = 1
        self.close_long = 2
        self.keep = 0
        self.strategy_name = strategy_name,

        self.bk_initial_money=bk_initial_money
        self.bk_commission=bk_commission
    
        
    def eval(self, df=None, params=[10, 30]):
        
        window_slow, window_fast, window_sign = params
        window_slow = window_slow
        window_fast = window_fast
        window_sign = window_sign
        
        
        macd = MACD(df['close'], 
                    window_slow=window_slow, 
                    window_fast=window_fast, 
                    window_sign=window_sign,
                    fillna=True
                )
        
        df['macd_line'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        df.loc[(df['macd_line'] > df['macd_signal']) & (df['macd_line'].shift() <= df['macd_signal'].shift()), 'actions'] = 1  # Señal de compra
        df.loc[(df['macd_line'] < df['macd_signal']) & (df['macd_line'].shift() >= df['macd_signal'].shift()), 'actions'] = 2  # Señal de venta
        
        df['actions'] = df['actions'].mask(df['actions'].eq(df['actions'].shift()))
        df['actions'] = df['actions'].fillna(0)
        df['actions'] = remove_noise_trading(actions=df['actions'])
        
        
        return df
    
    def objective_function(self, params=[10,30], df=None):
        
        # Apply the strategy with the current parameters
        
        result_df = self.eval(df=df.copy(), params=params)
        
        back_testing = GenericBacktesting(
            df=result_df,
            skip=True,
            initial_money=2000.0,
            commission=0.02,
            plot_result=False,
            path_save_result=".",
            print_stacks=False
        )
        return_data, _ = back_testing.calculate_bk()
        
        log.info(f'Strategy: {self.name} RETURN: {return_data} PARAMS: {params}')
        # Minimize the negative return to maximize the return
        return -return_data
    
    def optimize(self, parms: list = params_default, initial_guess: list = params_init, df=None, method: str = "Nelder-Mead"):
        
        threshold_bounds = parms
        
        result = minimize(self.objective_function, initial_guess, bounds=threshold_bounds, args=(df), method=method)
        
        best_breakout_threshold = result
        
        best_return = -result.fun

        return best_return, best_breakout_threshold
    


    def experiment(self, df=None, parms=params_default,initial_guess=params_init):
        
        methods_list = [
            # 'Nelder-Mead',
            'Powell',
            # 'CG',
            # 'L-BFGS-B',
            # 'COBYLA',
            # 'trust-constr'
        ]
        
        results_methods = {}
        results_method_list = []
        result_method_name = []
        
        for method in methods_list:
            print(f"Method: {method}")
    
            best_return, best_sma_threshold = self.optimize(
                parms=parms, 
                initial_guess=initial_guess,
                df=df, 
                method=method
            )
    
            results_method_list.append(best_return)
            result_method_name.append(method)
    
            results_methods[method] = best_return, best_sma_threshold.x
            

        # get the max value of results_method_list
        optimize = results_method_list.index(max(results_method_list))
        method = result_method_name[optimize]
        best_return, best_sma_threshold = results_methods[method]
        
        return method, best_return, best_sma_threshold

# strategy_data = Strategy(df=data)
# method, best_return, best_parameters = strategy_data.experiment(df=data)
# print(f"Best Return: {best_return}", )
# print(f"Best parms: {best_parameters}")
# print(f"Method: {method}")

# data2 = strategy_data.eval(df=data, params=best_parameters)
# data2.head()
# strategy_data.plot(df=data2, save_figure=True)
