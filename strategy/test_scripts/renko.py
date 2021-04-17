import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
#import talib
import pandas as pd
from get_db_data import get_db_data

class renko(object):      
    def __init__(self):
        self.source_prices = []
        self.renko_prices = []
        self.renko_directions = []
    
    # Setting brick size. Auto mode is preferred, it uses history
    def set_brick_size(self, HLC_history = None, auto = True, brick_size = 10.0):
        if auto == True:
            self.brick_size = self.__get_optimal_brick_size(HLC_history.iloc[:, [0, 1, 2]])
        else:
            self.brick_size = brick_size
        return self.brick_size
    
    def __renko_rule(self, last_price):
        # Get the gap between two prices
        gap_div = int(float(last_price - self.renko_prices[-1]) / self.brick_size)
        is_new_brick = False
        start_brick = 0
        num_new_bars = 0

        # When we have some gap in prices
        if gap_div != 0:
            # Forward any direction (up or down)
            if (gap_div > 0 and 
                (self.renko_directions[-1] > 0 or self.renko_directions[-1] == 0)) \
            or (gap_div < 0 and 
                (self.renko_directions[-1] < 0 or self.renko_directions[-1] == 0)):
                num_new_bars = gap_div
                is_new_brick = True
                start_brick = 0
            # Backward direction (up -> down or down -> up)
            elif np.abs(gap_div) >= 1: # Should be double gap at least
                num_new_bars = gap_div
                num_new_bars -= np.sign(gap_div)
                start_brick = 2
                is_new_brick = True
                self.renko_prices.append(self.renko_prices[-1] + 2 * self.brick_size * np.sign(gap_div))
                self.renko_directions.append(np.sign(gap_div))
            else:
                num_new_bars = 0

            if is_new_brick:
                # Add each brick
                for d in range(start_brick, np.abs(gap_div)):
                    self.renko_prices.append(self.renko_prices[-1] + self.brick_size * np.sign(gap_div))
                    self.renko_directions.append(np.sign(gap_div))
        
        return num_new_bars
                
    # Getting renko on history
    def build_history(self, prices):
        if len(prices) > 0:
            # Init by start values
            self.source_prices = prices
            self.renko_prices.append(prices.iloc[0])
            self.renko_directions.append(0)
        
            # For each price in history
            for p in self.source_prices[1:]:
                self.__renko_rule(p)
        
        return len(self.renko_prices)
    
    # Getting next renko value for last price
    def do_next(self, last_price):
        if len(self.renko_prices) == 0:
            self.source_prices.append(last_price)
            self.renko_prices.append(last_price)
            self.renko_directions.append(0)
            return 1
        else:
            self.source_prices.append(last_price)
            return self.__renko_rule(last_price)
    
    # Simple method to get optimal brick size based on ATR
    def __get_optimal_brick_size(self, HLC_history, atr_timeperiod = 14):
        brick_size = 0.0
        
        # If we have enough of data
        if HLC_history.shape[0] > atr_timeperiod:
            #brick_size = np.median(talib.ATR(high = np.double(HLC_history.iloc[:, 0]), 
                                             #low = np.double(HLC_history.iloc[:, 1]), 
                                             #close = np.double(HLC_history.iloc[:, 2]), 
                                             #timeperiod = atr_timeperiod)[atr_timeperiod:])
        
        # return brick_size
           pass
    
    def evaluate(self, method = 'simple'):
        balance = 0
        sign_changes = 0
        price_ratio = len(self.source_prices) / len(self.renko_prices)

        if method == 'simple':
            for i in range(2, len(self.renko_directions)):
                if self.renko_directions[i] == self.renko_directions[i - 1]:
                    balance = balance + 1
                else:
                    balance = balance - 2
                    sign_changes = sign_changes + 1

            if sign_changes == 0:
                sign_changes = 1

            score = balance / sign_changes
            if score >= 0 and price_ratio >= 1:
                score = np.log(score + 1) * np.log(price_ratio)
            else:
                score = -1.0

            return {'balance': balance, 'sign_changes:': sign_changes, 
                    'price_ratio': price_ratio, 'score': score}
    
    def get_renko_prices(self):
        return self.renko_prices
    
    def get_renko_directions(self):
        return self.renko_directions
    
    def plot_renko(self, col_up = 'g', col_down = 'r'):
        fig, ax = plt.subplots(1, figsize=(20, 10))
        ax.set_title('Renko chart')
        ax.set_xlabel('Renko bars')
        ax.set_ylabel('Price')

        # Calculate the limits of axes
        ax.set_xlim(0.0, 
                    len(self.renko_prices) + 1.0)
        ax.set_ylim(np.min(self.renko_prices) - 3.0 * self.brick_size, 
                    np.max(self.renko_prices) + 3.0 * self.brick_size)
        
        # Plot each renko bar
        for i in range(1, len(self.renko_prices)):
            # Set basic params for patch rectangle
            col = col_up if self.renko_directions[i] == 1 else col_down
            x = i
            y = self.renko_prices[i] - self.brick_size if self.renko_directions[i] == 1 else self.renko_prices[i]
            height = self.brick_size
                
            # Draw bar with params
            ax.add_patch(
                patches.Rectangle(
                    (x, y),   # (x,y)
                    1.0,     # width
                    self.brick_size, # height
                    facecolor = col
                )
            )
        
        plt.show()
        
# \Python\First_Choice_Git\xts\strategy\test_scripts\sample.csv
# header_list = ["date", "time", "open","high","low","close","volume"]
header_list = ["date", "open","high","low","close","volume"]
raw_df = pd.read_csv(r'D:\sample.csv',
                      names=header_list,
                      header=None,
                      index_col=False,
                      #parse_dates=[['date','time']]
                      )
raw_df = raw_df.astype(dtype={
    'open': float, 'high': float, 'low': float, 'close': float, 'volume': int})


# raw_df['date_time'] = pd.to_datetime(raw_df['date'],unit='s')
# #raw_df['date_time'] = raw_df['date_time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
# data=raw_df.sort_values(by="date",ascending=False)

# data = data_df.copy()    
# # # optimal_brick = renko().set_brick_size(auto = True, HLC_history = data[["high", "low", "close"]])

data = get_db_data('ITC','2021-04-13')
data = data.shift(1,axis=0)
data = data.fillna(data.open.iloc[1])

# # # Build Renko chart
# for i in range(len(data)):
renko_obj_atr = renko()
print('Set brick size to optimal: ', renko_obj_atr.set_brick_size(auto = False, brick_size = 1))
renko_obj_atr.build_history(prices = data.close)
print('Renko bar prices: ', renko_obj_atr.get_renko_prices())
print('Renko bar directions: ', renko_obj_atr.get_renko_directions())
# print('Renko bar evaluation: ', renko_obj_atr.evaluate())

if len(renko_obj_atr.get_renko_prices()) > 1:
    renko_obj_atr.plot_renko()    
    