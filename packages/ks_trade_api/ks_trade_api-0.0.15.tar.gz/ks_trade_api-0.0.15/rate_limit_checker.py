from abc import ABC, abstractmethod
import os
import pandas as pd
from typing import Union, Tuple, Optional
#SysConfig.set_all_thread_daemon(True)
from ks_utility.logs import LoggerBase
from datetime import datetime
from .constant import *
from ks_trade_api.object import ContractData, MyAccountData, ErrorData, MyPositionData, MyTradeData, MyOrderData
from .constant import (
    Currency as KsCurrency,
    Exchange as KsExchange,
    Direction as KsDirection, 
    OrderType as ksOrderType, 
    Direction as KsDirection,
    Offset as KsOffset, 
    TimeInForce as KsTimeInForce,
    ErrorCode as KsErrorCode,
    Status as KsStatus,
    RET_OK, 
    RET_ERROR, 
    CHINA_TZ,
    
)
from ks_trade_api.utility import extract_vt_symbol
import sys
from decimal import Decimal
import uuid

RATES_INTERVAL = 30 # 30秒内30次请求，所以一旦超频，就睡眠30秒

class RateLimitChecker(LoggerBase):
    def __init__(self, rate_interval = RATES_INTERVAL):
        LoggerBase.__init__(self)
        
        self.rate_interval: int = rate_interval
        self.last_error_time: Optional[datetime] = None
        self.last_error_data: Optional[ErrorData] = None
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            diff_seconds = -1
            if self.last_error_time:
                now = datetime.now()
                interval_seconds = (now - self.last_error_time).seconds
                diff_seconds = self.rate_interval - interval_seconds
            if diff_seconds >= 0:
                self.log({'function_name': func.__name__, 'now': now, 'self.last_error_time': self.last_error_time}, tag=f'触发API超频，请求截断。{diff_seconds}秒后恢复访问')
                return RET_ERROR, self.last_error_data
            
            ret, data = func(*args, **kwargs)
            self.last_error_time = None

            if ret == RET_ERROR:
                if data.code == KsErrorCode.RATE_LIMITS_EXCEEDED:
                    self.last_error_time = datetime.now()
                    self.last_error_data = data
                    args[0].send_dd(f'{data.msg}', title=f'超频请求提示')

            return ret, data
        return wrapper