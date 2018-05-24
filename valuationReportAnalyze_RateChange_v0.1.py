#!/usr/bin/env python

# @Author:  Karay
# @Date:    2018/05/21
# @Desc:    calculate the diff introduced by the exchange rate
#           part1: valuation sheet: MarketValue with diff between T0 and T-1
#           part2: UnwoundEQ sheet: UnwoundEquity with diff between T0 and T-1
#           20180524, for python3.5

import pandas as pd
import sys

if len(sys.argv) != 3:
    print ("!!!parameters wrongly provided!")
    print ("!!!there should be file_to_handle and file_as_against both provided")
    print ("         for example: python valuationReportAnalyze_RateChange.py 'Chenjie_ValuationReport_20180518.xls' 'Chenjie_ValuationReport_20180517.xls'")
    sys.exit(0)

filename = sys.argv[1]
file_against = sys.argv[2]

df = pd.ExcelFile(filename)
date = filename[-12:-4]
"""
pd.set_option('display.height',1000)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)
"""
names=['date','qty','price','FX']

print ("---------------------------------------------------------Valuation sheet")

valuation = df.parse('Valuation')
valuation = valuation[9:len(valuation)]
valuation = valuation.ix[:,[2,8,10,12]]

valuation.columns = names
valuation = valuation.dropna(how='all')

print ("example data for valuation sheet after handling:")
print (valuation.tail(5))

cum_val = 0
fx = -1;
for i in range(0, len(valuation)):
    temp = valuation[i:i+1]
    cum_val = cum_val + float(temp['qty'] * temp['price'])
    fx = float(temp['FX'])

print ("cum_val value for valuation part is " + str(cum_val) + "RMB")
print ("FX for " + date + " is " + str(fx))

print ("---------------------------------------------------------EQ Unwound sheet")
dateAttr = date[0:4] + "/" + date[4:6] + "/" + date[6:]
unWoundEQ = df.parse('EQ Unwound')
unWoundEQ = unWoundEQ.ix[:,[0,6,7,11]]

unWoundEQ.columns = names
unWoundEQ = unWoundEQ[unWoundEQ['date']==dateAttr]

print ("example data for EQ_Unwound sheet after handling:")
print (unWoundEQ.head(5))

cum_eq = 0
unwoundFX = -1;
for i in range(0, len(unWoundEQ)):
    temp = unWoundEQ[i:i+1]
    cum_eq = cum_eq + float(temp['qty'] * temp['price'])
    unwoundFX = float(temp['FX'])

cum_eq = abs(cum_eq)
print ("cum_eq value for valuation part is " + str(cum_eq) + "RMB")
print ("FX for " + date + " is " + str(unwoundFX))

print ("---------------------------------------------------------calculate the final diff from the Foreign exchange")
df_against = pd.ExcelFile(file_against)
valuation_against = df_against.parse("Valuation")
unwoundEQ_against = df_against.parse("EQ Unwound")

valuation_against = valuation_against[9:len(valuation_against)]
valuation_against = valuation_against.ix[:,[2,8,10,12]]

valuation_against.columns = names
valuation_against = valuation_against.dropna(how='all')

fx_against = float((valuation_against[len(valuation_against)-1:len(valuation_against)])['FX'])
print ("as contrast, valuation FX = " + str(fx_against))
val1 = cum_val / fx - cum_val / fx_against
print (val1)

unwoundEQ_against = unwoundEQ_against.ix[:,[0,6,7,11]]
unwoundEQ_against.columns = names
unwoundFX_against =  float(unwoundEQ_against[len(unwoundEQ_against)-1:len(unwoundEQ_against)]['FX'])

print ("as contrast, unwoundEQ FX = " + str(unwoundFX_against))
val2 = cum_eq / unwoundFX - cum_eq / unwoundFX_against
print (val2)


print ("total diff caused by the exchange rate is " + str(val1 + val2) + "$")


