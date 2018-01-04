from doublecross import DoubleXover as dx
import sys
import numpy as np
import pandas as pd
import itertools

## Variables: (1) Period (300, 900, 1800, 7200, 14400, 86400), (2) Date Range (any possible) to input manually;
## Variables: (3) MA 1 - x ; (4) MA 2 - y; (5) Currency Pair (Code) BTC, BCH, ETH, NXT, XRP, LTC, REP, ETC, STR, ZEC, DASH, XMR (12 pairs).
## Due to restrictions in memory, I will test the following: (1) SMA or EMA - 2 (2) Date Range (past x months): 1, 3, 6, 12 - 4
## (3) pair: BTC (Bitcoin), XRP (Ripple), XLM (Stellar Lumens) - 3 (4) roll1, 10 periods to 10 periods starting from 10, 10 times
## (5) roll2, 10 periods to 10 periods starting from 20, 10 times. In total, since roll2 > roll1, there must be 55 combinations of rolls.
## We will have 2 * 3 * 4 * 3 * 55 = 3,960 results


period = [1800, 7200, 14400]  # , 7200, 14400, 86400]
date_range = [str('0112201601122017')]
pair = [str('USDT_BTC'), str('USDT_ETH'), str('USDT_XRP')]
roll1 = [10, 30, 50, 70, 90]
roll2 = [20, 40, 60, 80, 100]
roll_type = [str('exp'), str('simple')] # possible choices: 'exp' or 'simple'

combinations_12 = int(len(period) * len(date_range) * len(roll_type) * len(pair) * ((len(roll1) * (len(roll1) + 1)) / 2))
objects_feature_list = ['period', 'date_range', 'roll_type', 'roll1', 'roll2', 'pair']
pd.DataFrame(0, index=np.arange(combinations_12), columns=objects_feature_list)

p_12 = []

for element in itertools.product(period, date_range, roll_type, roll1, roll2, pair):
    if element[4] > element[3]:
        p_12.append(element)

results_feature_list_pre = ('period', 'date_range', 'roll_type', 'roll1', 'roll2', 'pair')
r12m = pd.DataFrame(p_12, index=np.arange(combinations_12), columns=results_feature_list_pre)



dic = {}
li = []

for i in range(0, combinations_12):
    d = dx(r12m.at[i, 'period'], r12m.at[i, 'date_range'], r12m.at[i, 'roll_type'], r12m.at[i, 'roll1'],
           r12m.at[i, 'roll2'], r12m.at[i, 'pair'])
    d.get_return()
    sys.stderr.write("{} {} {} \n".format(i, " in ", combinations_12))
    sys.stderr.flush()
    key = int(d.strategy_return * (10 ** 12))
    dic[key] = d
    li.append(key)

li.sort(reverse=True)
print("--")
for key in li:
    print("{} {} {} {} {} {} {}".format(dic[key].strategy_return, dic[key].period, dic[key].date_range,
                                        dic[key].roll_type, dic[key].first_roll, dic[key].second_roll,
                                        dic[key].currency_pair))



