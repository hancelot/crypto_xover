# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import pandas as pd
import pprint

date_range = str('0112201601122017')


def get_epoch(timestr):
    pattern = '%d.%m.%Y %H:%M:%S'
    return int(time.mktime(time.strptime((timestr[0:2] + '.' + timestr[2:4] + '.' + timestr[4:9] + ' 00:00:00'), pattern)))

def transform_time_to_epoch(date_range):
    return get_epoch(date_range[:8]), get_epoch(date_range[8:])




# Here direct pairs to USDT, but if not listed, you can merge two dataframes including the rates to translate xxx to BTC or ETH, and then BTC or ETH to USDT_BTC

class DoubleXover:
    def __init__(self, period, date_range, roll_type, first_roll, second_roll, currency_pair):
        self.period = period
        self.date_range = date_range
        self.roll_type = roll_type
        self.first_roll = first_roll
        self.second_roll = second_roll
        self.currency_pair = currency_pair
        self.strategy_return = 0


    def get_return(self):
        fee_amount = 0.0025
        ep_from, ep_to = transform_time_to_epoch(self.date_range)

        # We call the Poloniex data and open it
        get_data_pair = urllib.request.urlopen(
            'https://poloniex.com/public?command=returnChartData&currencyPair=' + str(
                self.currency_pair) + '&start=' + str(ep_from) + '&end=' + str(ep_to) + '&period=' + str(
                self.period) + '')

        str_response = get_data_pair.read().decode('utf-8')

        # We load what we open in a JSON and assign it to the variable BTC
        pair_read = json.loads(str_response)

        # We create Pandas dataframes for both JSON; Remove unnecessary columns
        main_pair = pd.DataFrame(pair_read)
        columns_to_drop = ['high', 'low', 'open', 'quoteVolume', 'volume', 'weightedAverage']
        main = main_pair.drop(columns_to_drop, axis=1)

        # Switch & Rename columns appropriately
        main.columns = ['rate', 'date']
        main = main[['date', 'rate']]

        # converts date from epoch to datetime
        main['date'] = pd.to_datetime(main['date'], unit='s')

        # create new columns for moving averages
        if self.roll_type == str('exp'):
            main['MA-1'] = main['rate'].ewm(span=self.first_roll).mean()
            main['MA-2'] = main['rate'].ewm(span=self.second_roll).mean()
        if self.roll_type == str('simple'):
            main['MA-1'] = main['rate'].rolling(window=self.first_roll).mean()
            main['MA-2'] = main['rate'].rolling(window=self.second_roll).mean()

        # create new column Order, indexed, and fill it with random numbers in it

        main['Order'] = len(main['date'])

        for k in range(1, len(main['date'])):
            if main['MA-2'][k - 1] > main['MA-1'][k - 1] and main['MA-2'][k] < main['MA-1'][k]:
                main.loc[k, 'Order'] = 1
            elif main['MA-2'][k - 1] < main['MA-1'][k - 1] and main['MA-2'][k] > main['MA-1'][k]:
                main.loc[k, 'Order'] = -1
            else:
                main.loc[k, 'Order'] = 0

        starting_position_USDT = 1000000.0

        main.loc[:, 'Cumul_Coin'] = 0
        main.loc[:, 'Cumul_USDT'] = 0

        start = main[main['Order'] == 1].iloc[0]
        start_trading = main.loc[main['date'] == start[0]].index[0]
        main.loc[start_trading, 'Cumul_Coin'] = (starting_position_USDT / start['rate'])

        for i in range(start_trading + 1, len(main['date'])):
            if main['Order'][i] == 0:
                main.loc[i, 'Cumul_Coin'] = main.loc[i - 1, 'Cumul_Coin']
                main.loc[i, 'Cumul_USDT'] = main.loc[i - 1, 'Cumul_USDT']
            if main['Order'][i] == 1:
                main.loc[i, 'Cumul_Coin'] = (main.loc[i - 1, 'Cumul_USDT'] / main['rate'][i]) * (1 - fee_amount)
                main.loc[i, 'Cumul_USDT'] = 0
            if main['Order'][i] == -1:
                main.loc[i, 'Cumul_USDT'] = ((main.loc[i - 1, 'Cumul_Coin'] * main['rate'][i]) * (1 - fee_amount))
                main.loc[i, 'Cumul_Coin'] = 0

        main.loc[:, 'Reval_USDT'] = 0
        for i in range(1, len(main['date'])):
            main.loc[i, 'Reval_USDT'] = (main.loc[i, 'Cumul_Coin'] * main['rate'][i]) + (main['Cumul_USDT'][i])

        end_position_USDT = main.iloc[-1, -1]
        self.strategy_return = (
            (end_position_USDT - starting_position_USDT) / starting_position_USDT)
		
       
		
