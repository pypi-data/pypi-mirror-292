from ...backtesting_custom.generic_backtesting import GenericBacktesting
from ...utils.pre_processing import remove_noise_trading
from scipy.optimize import minimize
from ta.trend import EMAIndicator
import logging as log
from pyttrading.utils.inflection_points import inflection_points
from pyttrading.utils.pre_processing import remove_noise_trading

params_default = [(10, 150), (10, 150), (0.1, 5)]

params_init = []
for param in params_default:
    param_low = param[0]
    params_init.append(param_low)

class Strategy: 

    def __init__(self, df=None, strategy_name :str = "StrategyName"):
        self.name = 'EMA'
        self.open_long = 1
        self.close_long = 2
        self.keep = 0
        self.strategy_name = strategy_name
    
    def eval(self, df=None, params=params_default):

        window_length, ema_smoothed, constant_inflection = params

        ema_indicator = EMAIndicator(close=df['close'], window=window_length)

        df['ema'] = ema_indicator.ema_indicator()
        # df['ema_s'] = talib.SMA(df['ema'], timeperiod=int(ema_smoothed)) #TODO deprecied
        df['ema_s'] = df['ema'].ewm(span=int(ema_smoothed), adjust=False).mean()

        df = inflection_points(df=df, threshold=constant_inflection, column_name='ema_s')
        df['actions'] = remove_noise_trading(actions=df['actions'])
        
        return df
    
    def objective_function(self, params=params_default, df=None):
        
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
    
    def optimize(self, params: list = params_default, initial_guess: list = params_init, df=None, method: str = "Nelder-Mead"):
        threshold_bounds = params
        result = minimize(self.objective_function, initial_guess, bounds=threshold_bounds, args=(df,), method=method)
        best_parameters = result.x
        best_return = -result.fun
        return best_return, best_parameters
    
    def experiment(self, df=None, params=params_default, initial_guess=params_init):

        methods_list = [
            'Nelder-Mead',
            # 'Powell',
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
            best_return, best_parameters = self.optimize(params=params, initial_guess=initial_guess, df=df, method=method)
            results_method_list.append(best_return)
            result_method_name.append(method)
            results_methods[method] = best_return, best_parameters
        
        optimize = results_method_list.index(max(results_method_list))
        method = result_method_name[optimize]
        best_return, best_parameters = results_methods[method]
        
        return method, best_return, best_parameters