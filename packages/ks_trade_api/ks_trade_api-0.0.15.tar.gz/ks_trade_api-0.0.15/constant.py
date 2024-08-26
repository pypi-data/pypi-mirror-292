"""
General constant enums used in the trading platform.
"""

from enum import Enum
import pytz
from datetime import time
from ks_utility.constants import Environment


class Direction(Enum):
    """
    Direction of order/trade/position.
    """
    LONG = "多"
    SHORT = "空"
    NET = "净"


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = ""
    OPEN = "开"
    CLOSE = "平"
    CLOSETODAY = "平今"
    CLOSEYESTERDAY = "平昨"


class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = "提交中"
    NOTTRADED = "未成交"
    PARTTRADED = "部分成交"
    ALLTRADED = "全部成交"
    CANCELLED = "已撤销"
    REJECTED = "拒单"


class Product(Enum):
    """
    Product class.
    """
    EQUITY = "股票"
    FUTURES = "期货"
    OPTION = "期权"
    INDEX = "指数"
    FOREX = "外汇"
    SPOT = "现货"
    ETF = "ETF"
    BOND = "债券"
    WARRANT = "权证"
    SPREAD = "价差"
    FUND = "基金"


class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = "限价"
    MARKET = "市价"
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = "询价"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = "看涨期权"
    PUT = "看跌期权"

class Currency(Enum):
    """
    Currency.
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"


class Interval(Enum):
    """
    Interval of bar data.
    """
    MINUTE = "1m"
    HOUR = "1h"
    DAILY = "d"
    WEEKLY = "w"
    TICK = "tick"

#=======================================

# 这里是把常量映射为字符串 'FUTURE' = > Enum('FUTURE)
def enum_map(enum):
    kv = {}
    for item in enum:
        kv[item.name] = item
        kv[item.value] = item
        kv[item] = item
        
    return kv


DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = DATE_FMT + ' %H:%M:%S.%f' + '%z'

class SwitchStatus(Enum):
    """
    移仓换月的状态
    """
    UNRUN = "UNRUN"
    RUNNING = "RUNNING"
    DONE = "DONE"

tz = pytz.timezone('PRC')
SETTLE_START_TIME = time(15,5,0,0, tzinfo=tz)
SETTLE_END_TIME = time(17,30,0,0, tzinfo=tz) #todo


DAY_OPEN_TIME = time(9,0,0, tzinfo=tz)
DAY_CLOSE_TIME = time(15,0,0, tzinfo=tz)

NIGHT_OPEN_TIME = time(21,0,0,0, tzinfo=tz)
NIGHT_CLOSE_TIME = time(2,3,0,0, tzinfo=tz)

class AccountType(Enum):
    """
    Option type.
    """
    NONE = 'N/A'     # 未知类型
    CASH = '现金'           # 现金账户
    MARGIN = '信用'       # 保证金账户

class Product(Enum):
    """
    Product class.
    """
    EQUITY = "股票"
    FUTURES = "期货"
    OPTION = "期权"
    INDEX = "指数"
    FOREX = "外汇"
    SPOT = "现货"
    ETF = "ETF"
    BOND = "债券"
    WARRANT = "权证"
    SPREAD = "价差"
    FUND = "基金"
    COIN = "数字货币"

class Exchange(Enum):
    """
    Exchange.
    """
    # Chinese
    CFFEX = "CFFEX"         # China Financial Futures Exchange
    SHFE = "SHFE"           # Shanghai Futures Exchange
    CZCE = "CZCE"           # Zhengzhou Commodity Exchange
    DCE = "DCE"             # Dalian Commodity Exchange
    INE = "INE"             # Shanghai International Energy Exchange
    GFEX = "GFEX"           # Guangzhou Futures Exchange
    SSE = "SSE"             # Shanghai Stock Exchange
    SZSE = "SZSE"           # Shenzhen Stock Exchange
    BSE = "BSE"             # Beijing Stock Exchange
    SGE = "SGE"             # Shanghai Gold Exchange
    WXE = "WXE"             # Wuxi Steel Exchange
    CFETS = "CFETS"         # CFETS Bond Market Maker Trading System
    XBOND = "XBOND"         # CFETS X-Bond Anonymous Trading System

    # Global
    SMART = "SMART"         # Smart Router for US stocks
    NYSE = "NYSE"           # New York Stock Exchnage
    NASDAQ = "NASDAQ"       # Nasdaq Exchange
    ARCA = "ARCA"           # ARCA Exchange
    EDGEA = "EDGEA"         # Direct Edge Exchange
    ISLAND = "ISLAND"       # Nasdaq Island ECN
    BATS = "BATS"           # Bats Global Markets
    IEX = "IEX"             # The Investors Exchange
    AMEX = "AMEX"           # American Stock Exchange
    TSE = "TSE"             # Toronto Stock Exchange
    NYMEX = "NYMEX"         # New York Mercantile Exchange
    COMEX = "COMEX"         # COMEX of CME
    GLOBEX = "GLOBEX"       # Globex of CME
    IDEALPRO = "IDEALPRO"   # Forex ECN of Interactive Brokers
    CME = "CME"             # Chicago Mercantile Exchange
    ICE = "ICE"             # Intercontinental Exchange
    SEHK = "SEHK"           # Stock Exchange of Hong Kong
    HKFE = "HKFE"           # Hong Kong Futures Exchange
    SGX = "SGX"             # Singapore Global Exchange
    CBOT = "CBT"            # Chicago Board of Trade
    CBOE = "CBOE"           # Chicago Board Options Exchange
    CFE = "CFE"             # CBOE Futures Exchange
    DME = "DME"             # Dubai Mercantile Exchange
    EUREX = "EUX"           # Eurex Exchange
    APEX = "APEX"           # Asia Pacific Exchange
    LME = "LME"             # London Metal Exchange
    BMD = "BMD"             # Bursa Malaysia Derivatives
    TOCOM = "TOCOM"         # Tokyo Commodity Exchange
    EUNX = "EUNX"           # Euronext Exchange
    KRX = "KRX"             # Korean Exchange
    OTC = "OTC"             # OTC Product (Forex/CFD/Pink Sheet Equity)
    IBKRATS = "IBKRATS"     # Paper Trading Exchange of IB

    # Special Function
    LOCAL = "LOCAL"         # For local generated data

    # Coins Exchanges
    BINANCE = 'BINANCE'
    DERIBIT = 'DERIBIT'

EXCHANGE_MAP = enum_map(Exchange)


# U本位 币本位
class ContractType(Enum):
    U = 'U本位'
    B = '币本位'

class TimeInForce(Enum):
    GTC = 'good_til_cancelled' # GTC = '立即成交剩余挂单至手工撤单(GTC)'
    GTD = 'good_til_day' # GTD = '立即成交剩余挂单至收盘(GTD)'
    FOK = 'fill_or_kill' # GTC = '全部成交或者撤单(FOK)'
    IOC = 'immediate_or_cancel' # IOC = '立即成交剩余撤销(IOC)'

class RetCode(Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    ASYNC = 'ASYNC'

RET_OK = RetCode.OK
RET_ERROR = RetCode.ERROR
RET_ASYNC = RetCode.ASYNC

class TradeSide(Enum):
    BUY = '买'
    SELL = '卖'

class SubscribeType(Enum):
    BOOK = 'BOOK'
    TICK = 'TICK'
    TRADE = 'TRADE'
    USER_TRADE = 'USER_TRADE'
    USER_ORDER = 'USER_ORDER'
    USER_POSITION = 'USER_POSITION'

class Currency(Enum):
    HKD = 'HKD'
    USD = 'USD'
    CNY = 'CNY'

class ErrorCode(Enum):
    RATE_LIMITS_EXCEEDED = 1
    SUBSCRIPTION_ERROR = 2
    BUY_POWER_EXCEEDED = 3 # 超过购买力
    LIQUIDITY_LACKED = 4 # 股票流动性不足

    # 100开始是交易框架的错误代码
    GATEWAY_NOT_FOUND = 100
    NOT_TRADING = 101 # trader被关停


OPTIONTYPE_MAP = enum_map(OptionType)
ACCOUNTTYPE_MAP = enum_map(AccountType)
ENVIRONMENT_MAP = enum_map(Environment)
CONTRACTTYPE_MAP = enum_map(ContractType)
DIRECTION_MAP = enum_map(Direction)
OFFSET_MAP = enum_map(Offset)
STATUS_MAP = enum_map(Status)
ORDER_TYPE_MAP = enum_map(OrderType)
PRODUCT_MAP = enum_map(Product)
TIMEINFORCE_MAP = enum_map(TimeInForce)
TRADE_SIDE_MAP = enum_map(TradeSide)

CHINA_TZ = pytz.timezone('PRC')       # 中国时区
US_EASTERN_TZ = pytz.timezone('US/Eastern')   # 美东时间

class TradingHours(Enum):
    PRE_MARKET = 'PRE_MARKET' # 盘前
    RTH = 'RTH' # 盘中
    AFTER_HOURS = 'AFTER_HOURS' # 盘后
    OVER_NIGHT = 'OVER_NIGHT' # 夜盘

class RthTime(Enum):
    # 美股时间
    US_EQUITY_PRE_MARKET_START = time(4, 0, 0, 0)
    US_EQUITY_PRE_MARKET_END = time(9, 30, 0, 0)
    US_EQUITY_RTH_START = time(9, 30, 0, 0)
    US_EQUITY_RTH_END = time(16, 0, 0, 0)
    US_EQUITY_AFTER_HOURS_START = time(16, 0, 0, 0)
    US_EQUITY_AFTER_HOURS_END = time(20, 0, 0, 0)
    US_EQUITY_OVER_NIGHT_START = time(20, 0, 0, 0)
    US_EQUITY_OVER_NIGHT_END = time(4, 0, 0, 0)

class Right(Enum):
    CALL = 'CALL'
    PUT = 'PUT'
