# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 19:30:00 2021

@author: lmahendran
"""
from utils.utils import xts_init, configure_logging
import os 
import sys

startTime='11:22:00'
logname=os.path.basename(__file__).split('.')[0]
logger = configure_logging(logname)

xt = xts_init(interactive=True)
if not xt:
    sys.exit()

if __name__ == '__main__':
    xt.get_expiry()
    order_id = xt.place_order_id(22,'buy',40,'cm')
    tp, date = xt.get_traded_price(order_id)
    
    
    # response = xt.get_equity_symbol(
    #     exchangeSegment=1,
    #     series='EQ',
    #     symbol='Acc')
    # print('Equity Symbol:', str(response))
    
    # xt.masterEqDump()
    # a,b = xt.get_expiry()
    xt.master_eq_dump()
    xt.strike_price('NIFTYBANK')
    
    # xt.ltp_eq('DLF')
    xt.ltp_eq(22)
    
    logger.info('END')
    # xt.ltp_fo(60140)
    # xt.ltp_fo('NIFTY2142214100CE')
