#!/usr/bin/env python

# @Author:  Karay
# @Date:    2018/06/06
# @Desc:    based on the valuation and trading detail
#			Sum{today_position * MktPrice} - Sum{against_position * MktPrice} + (Dividend + Interest) * MktFX - Sum{buyQty * price} + Sum{sellQty * price}
#			buy and sell info is from the trading detail, including the master valuation report and the W1-n valuation report

import pandas as pd
import sys

"""
pd.set_option('display.height',1000)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)
"""

print ('------------------there must be at least 2 file names provided!')
print ('------------------      T0 valuation report')
print ('------------------      T-1 valuation report')
print ('------------------      additional: Outside securities valuation report, e.g. W1_Valuation_Report')
print ('------------------example: python analyze_pnl.py Chenjie_ValuationReport_20180606.xls Chenjie_ValuationReport_20180605.xls ChenjieW1B_ValuationReport_20180606.xls')
if len(sys.argv) < 3:
    print ("!!!parameters wrongly provided!")
    print ("!!!there should be at lest file_to_handle and file_as_against both provided")
    print ("         for example: python analyze_pnl.py 'Chenjie_ValuationReport_20180606.xls' 'Chenjie_ValuationReport_20180605.xls'")
    sys.exit(0)

filename = sys.argv[1]
file_against = sys.argv[2]

names_valuation=['symbol','qty','price','FX','Interest','Dividend','TotalSWAP']
names_detail = ['symbol', 'side', 'qty', 'price','FX']
result_col = ['RMB_PNL', 'USD_PNL', 'remarks']
testSymbol = '600487.SSC'

df = pd.ExcelFile(filename)
date = filename[-12:-4]
def init_valuation(filename):
    df = pd.ExcelFile(filename)
    valuation = df.parse('Valuation')
    valuation = valuation[9:len(valuation)]
    valuation = valuation.ix[:,[3,8,10,12,21,22,23]]
    valuation.columns = names_valuation
    valuation = valuation.dropna(how='any')
#valuation.index = valuation['symbol'].tolist()
    valuation.index = list(range(len(valuation)))
    return valuation
  
def init_detail(df):
    trading_detail = df.parse('Trading Detail')
    trading_detail = trading_detail[8:len(trading_detail)]
    trading_detail = trading_detail.ix[:, [4,2,3,9,10]]
    trading_detail.columns = names_detail
    trading_detail = trading_detail.dropna(how='any')
    trading_detail.index = list(range(len(trading_detail)))
    return trading_detail

valuation_today = init_valuation(filename)

#result: symbol, RMB_PNL, USD_PNL
resultDict = {}

"""
Valuation part: Sum(price * qty) + (Dividend+Interest)*MktFX
    algo2: +TotalSWAP
"""
for i in range(0,len(valuation_today)):
    record = valuation_today.loc[i]
    key = record['symbol']
    temp1 = 0
    temp2 = 0
    # position * MktFX
    temp1 += int(record['qty']) * float(record['price'])
    temp2 += temp1 / float(record['FX'])
    temp1 += float(record['FX']) * (float(record['Dividend']) + float(record['Interest']))
    temp2 += float(record['Dividend']) + float(record['Interest'])

    if key not in resultDict:
        resultDict[key] = [0, 0, '']
    resultDict[key][0] += temp1
    resultDict[key][1] += temp2
"""
Valuation part-yesterday: - Sum(price * qty)
    algo2: -TotalSWAP
"""
valuation_against = init_valuation(file_against)
for i in range(0, len(valuation_against)):
    record = valuation_against.loc[i]
    key = record['symbol']
    temp1 = 0
    temp2 = 0
    # position * MktFX
    temp1 += int(record['qty']) * float(record['price'])
    temp2 += temp1 / float(record['FX'])
    if key not in resultDict:
        remarks = 'the symbol gets closeout today: existed yesterday, not today'
        resultDict[key] = [0, 0,remarks]
    resultDict[key][0] -= temp1
    resultDict[key][1] -= temp2

"""
Trading detail: -sum{Buy} + sum{Sell}
"""

trading_detail = init_detail(df)
for i in range(0, len(trading_detail)):
    record = trading_detail.loc[i]
    key = record['symbol']
    if key not in resultDict:
        remarks = 'Alert: the symbol does not exist in the valuation sheet, but owns trading detail!'
        resultDict[key] = [0, 0, remarks]
    # for 'sell', the qty itself if "-", no need to separately handle it
    temp = int(record['qty']) * float(record['price'])
    resultDict[key][0] -= temp
    resultDict[key][1] -= temp / float(record['FX'])

"""
Outside Securities pool: 
trading detail: -sum{Buy} + sum{Sell}
"""
for i in range(3, len(sys.argv)):
    print ('process file', sys.argv[i])
    file_Wn = sys.argv[i]
    df_Wn = pd.ExcelFile(file_Wn)
    trading_detail_Wn = init_detail(df_Wn)
    for i in range(0, len(trading_detail_Wn)):
        record = trading_detail_Wn.loc[i]
        key = record['symbol']
        if key not in resultDict:
            remarks = 'Alert: the symbol does not exist in the valuation sheet, but owns trading detail with outside!'
            resultDict[key] = [0, 0, remarks]
        # for 'sell', the qty itself if "-", no need to separately handle it
        temp = int(record['qty']) * float(record['price'])
        resultDict[key][0] -= temp
        resultDict[key][1] -= temp / float(record['FX'])

result = pd.DataFrame.from_dict(resultDict, orient='index')
result.columns = result_col
print (result.head(5))
result.to_csv('out.csv', sep=',', header=True, index=True)

