#！/usr/bin/python
# Author:   Karay
# Date:     20180523
# Desc:     given the start date and symbols, display the quotes from start_date to today

import baostock as bs
import pandas as pd
import numpy as np
import datetime
import sys
import re
#get the market data , and set the warning price based on the K-Data
def return_constraintdict(stock_code_list, startdate):
    login_result = bs.login()
    print ('login respond error_msg:' + login_result.error_msg)

    today = datetime.datetime.now()
    delta = datetime.timedelta(days = 1)

#get the history market data till last exchange date
    predate = today - delta
    strpredate = datetime.datetime.strftime(predate, '%Y-%m-%d')
    for stock_code in stock_code_list:
        rs = bs.query_history_k_data("%s" % stock_code, "date, code, open, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg, peTTM, pbMRQ, psTTM, pcfNcfTTM",
                start_date = startdate, end_date=strpredate, frequency="d", adjustflag="2")
        print ('query_history_k_data respond error_code:' + rs.error_code)
        print ('query_history_k_data respond error_msg:' + rs.error_msg)

        result_list = []
        while(rs.error_code == '0') & rs.next():
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)
        print (result)

        closelist = list(result['close'])
        closelist = [float(price) for price in closelist]


if __name__ == '__main__':
    stock_code_list = []
    if len(sys.argv) == 1:
        print ("no symbols are provided! Do nothing")
        sys.exit()
    if len(sys.argv) < 3:
        print ("there must be start_date and symbols provided")
        sys.exit()
    start_date = sys.argv[1]
    mat = re.search(r"(\d{4}-\d{2}-\d{2})", start_date)
    if mat is None:
        print("there must be start_date provided!")
        sys.exit()

    for index in range(2, len(sys.argv)):
        stock_code_list.append(sys.argv[index])
    print (stock_code_list)
    return_constraintdict(stock_code_list, start_date)

