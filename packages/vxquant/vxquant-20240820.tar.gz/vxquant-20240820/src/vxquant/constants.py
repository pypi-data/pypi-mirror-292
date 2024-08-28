"""常用常量定义"""

from enum import Enum


class BarFreqType(Enum):
    """K线周期类型定义"""

    Tick = "tick"
    Min1 = "1m"
    Min5 = "5m"
    Min15 = "15m"
    Min30 = "30m"
    Hour1 = "1h"
    Day1 = "1d"
    Week1 = "1w"


class OrderStatus(Enum):
    """订单状态定义"""

    New = "New"  # 已报
    PartiallyFilled = "PartiallyFilled"  # 部成
    Filled = "Filled"  # 已成
    Canceled = "Canceled"  # 已撤
    Rejected = "Rejected"  # 已拒绝
    PendingNew = "PendingNew"  # 待报
    Expired = "Expired"  # 已过期
    Suspend = "Suspend"  # 暂停


class OrderSide(Enum):
    """订单方向定义"""

    Buy = "Buy"
    Sell = "Sell"


class OrderType(Enum):
    """订单类型定义"""

    Limit = "Limit"
    Market = "Market"
    Stop = "Stop"
    StopLimit = "StopLimit"
    TrailingStop = "TrailingStop"
    TrailingStopLimit = "TrailingStopLimit"


class ExecType(Enum):
    """成交类型定义"""

    Trade = "Trade"  # 成交
    CancelRejected = "CancelRejected"  # 撤单被拒绝


class PositionEffect(Enum):
    """持仓效果定义"""

    Open = "Open"  # 开仓
    Close = "Close"  # 平仓, 具体语义取决于对应的交易所（实盘上期所和上海能源所不适用，上期所和上海能源所严格区分平今平昨，需要用3和4）
    CloseToday = "CloseToday"  # 平今仓
    CloseYesterday = "CloseYesterday"  # 平昨仓(只适用于期货，不适用股票，股票用2平仓)


class PositionSide(Enum):
    """持仓方向定义"""

    Long = "Long"  # 多头
    Short = "Short"  # 空头


class OrderRejectCode(Enum):
    """委托拒绝代码定义"""

    Unknown = "Unknown"  # 未知原因
    RiskRuleCheckFailed = "RiskRuleCheckFailed"  # 不符合风控规则
    NoEnoughCash = "NoEnoughCash"  # 资金不足
    NoEnoughPosition = "NoEnoughPosition"  # 仓位不足
    IllegalAccountId = "IllegalAccountId"  # 非法账户ID
    IllegalStrategyId = "IllegalStrategyId"  # 非法策略ID
    IllegalSymbol = "IllegalSymbol"  # 非法交易标的
    IllegalVolume = "IllegalVolume"  # 非法委托量
    IllegalPrice = "IllegalPrice"  # 非法委托价
    AccountDisabled = "AccountDisabled"  # 交易账号被禁止交易
    AccountDisconnected = "AccountDisconnected"  # 交易账号未连接
    AccountLoggedout = "AccountLoggedout"  # 交易账号未登录
    NotInTradingSession = "NotInTradingSession"  # 非交易时段
    OrderTypeNotSupported = "OrderTypeNotSupported"  # 委托类型不支持
    Throttle = "Throttle"  # 流控限制


class CancelOrderRejectCode(Enum):
    """取消订单拒绝原因"""

    OrderFinalized = "OrderFinalized"  # 委托已完成
    UnknownOrder = "UnknownOrder"  # 未知委托
    BrokerOption = "BrokerOption"  # 柜台设置
    AlreadyInPendingCancel = "AlreadyInPendingCancel"  # 委托撤销中


class CashPositionChangeReason(Enum):
    """现金持仓变动原因"""

    Deposit = "Deposit"  # 存入
    Withdraw = "Withdraw"  # 取出
    Trade = "Trade"  # 交易
    Fee = "Fee"  # 手续费
    Interest = "Interest"  # 利息
    Dividend = "Dividend"  # 分红
    Transfer = "Transfer"  # 转账
    Other = "Other"  # 其他


class SecType(Enum):
    """标的类别"""

    REPO = "REPO"  # 回购
    STOCK = "STOCK"  # 股票
    FUND = "FUND"  # 基金
    ETFLOF = "ETFLOF"  # ETF/LOF
    INDEX = "INDEX"  # 指数
    FUTURE = "FUTURE"  # 期货
    OPTION = "OPTION"  # 期权
    CREDIT = "CREDIT"  # 信用交易
    BOND = "BOND"  # 债券
    BOND_CONVERTIBLE = "BOND_CONVERTIBLE"  # 可转债
    CONFUTURE = "CONFUTURE"  # 期货连续合约


class AccountStatus(Enum):
    """账户状态"""

    CONNECTING = "CONNECTING"  # 连接中
    CONNECTED = "CONNECTED"  # 已连接
    LOGGEDIN = "LOGGEDIN"  # 已登录
    DISCONNECTING = "DISCONNECTING"  # 断开中
    DISCONNECTED = "DISCONNECTED"  # 已断开
    ERROR = "ERROR"  # 错误


DEFULAT_SYMBOL_MAP = {
    ("SHSE", "204"): {
        "security_type": "REPO",
        "commission_coeff_peramount": 0.00,
        "commission_coeff_today_peramount": 0.0,
        "tax_coeff_peramount": 0.00,
        "price_tick": 0.0001,
        "volume_unit": 100,
        "upper_limit_ratio": 10000,
        "down_limit_ratio": 0.0,
        "allow_t0": False,
    },
    ("SZSE", "131"): {
        "security_type": "REPO",
        "commission_coeff_peramount": 0.00,
        "commission_coeff_today_peramount": 0.0,
        "tax_coeff_peramount": 0.00,
        "price_tick": 0.0001,
        "volume_unit": 10,
        "upper_limit_ratio": 10000,
        "down_limit_ratio": 0.0,
        "allow_t0": False,
    },
    ("SHSE", "60"): {
        "security_type": "STOCK",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SHSE", "68"): {
        "security_type": "STOCK",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 100,
        "upper_limit_ratio": 1.2,
        "down_limit_ratio": 0.8,
        "allow_t0": False,
    },
    ("SHSE", "00"): {
        "security_type": "INDEX",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 1,
        "upper_limit_ratio": 100,
        "down_limit_ratio": 0,
        "allow_t0": True,
    },
    ("SZSE", "39"): {
        "security_type": "INDEX",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 1,
        "upper_limit_ratio": 100,
        "down_limit_ratio": 0,
        "allow_t0": True,
    },
    ("SHSE", "50"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SHSE", "51"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SHSE", "58"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SHSE", "56"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SHSE", "10"): {
        "security_type": "BOND",
        "commission_coeff_peramount": 0.0008,
        "commission_coeff_today_peramount": 0.0008,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.0001,
        "volume_unit": 10,
        "upper_limit_ratio": 1.3,
        "down_limit_ratio": 0.7,
        "allow_t0": True,
    },
    ("SHSE", "11"): {
        "security_type": "BOND_CONVERTIBLE",
        "commission_coeff_peramount": 0.0008,
        "commission_coeff_today_peramount": 0.0008,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.01,
        "volume_unit": 10,
        "upper_limit_ratio": 1.3,
        "down_limit_ratio": 0.7,
        "allow_t0": True,
    },
    ("SZSE", "00"): {
        "security_type": "STOCK",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SZSE", "30"): {
        "security_type": "STOCK",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.001,
        "price_tick": 0.01,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SZSE", "12"): {
        "security_type": "BOND_CONVERTIBLE",
        "commission_coeff_peramount": 0.0008,
        "commission_coeff_today_peramount": 0.0008,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.01,
        "volume_unit": 10,
        "upper_limit_ratio": 1.3,
        "down_limit_ratio": 0.7,
        "allow_t0": True,
    },
    ("SZSE", "15"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SZSE", "16"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
    ("SZSE", "18"): {
        "security_type": "ETFLOF",
        "commission_coeff_peramount": 0.001,
        "commission_coeff_today_peramount": 0.001,
        "tax_coeff_peramount": 0.0,
        "price_tick": 0.001,
        "volume_unit": 100,
        "upper_limit_ratio": 1.1,
        "down_limit_ratio": 0.9,
        "allow_t0": False,
    },
}

# T0的ETF产品
T0_ETFLOF = [
    "161129.SZ",
    "160723.SZ",
    "160216.SZ",
    "501018.SH",
    "165513.SZ",
    "161116.SZ",
    "161815.SZ",
    "162719.SZ",
    "163208.SZ",
    "164701.SZ",
    "160416.SZ",
    "162411.SZ",
    "160719.SZ",
    "513500.SH",
    "513030.SH",
    "513080.SH",
    "513100.SH",
    "159941.SZ",
    "513300.SH",
    "161128.SZ",
    "161125.SZ",
    "161130.SZ",
    "161126.SZ",
    "162415.SZ",
    "161127.SZ",
    "513050.SH",
    "159822.SZ",
    "159607.SZ",
    "159605.SZ",
    "164906.SZ",
    "164824.SZ",
    "159740.SZ",
    "159741.SZ",
    "159742.SZ",
    "159823.SZ",
    "159850.SZ",
    "159892.SZ",
    "159920.SZ",
    "159954.SZ",
    "159960.SZ",
    "160322.SZ",
    "160717.SZ",
    "160922.SZ",
    "160924.SZ",
    "161124.SZ",
    "161831.SZ",
    "162416.SZ",
    "164705.SZ",
    "501021.SH",
    "501025.SH",
    "501301.SH",
    "501302.SH",
    "501303.SH",
    "501305.SH",
    "501306.SH",
    "501307.SH",
    "501309.SH",
    "501310.SH",
    "501311.SH",
    "510900.SH",
    "513000.SH",
    "513010.SH",
    "513060.SH",
    "513090.SH",
    "513130.SH",
    "513180.SH",
    "513330.SH",
    "513520.SH",
    "513550.SH",
    "513580.SH",
    "513600.SH",
    "513660.SH",
    "513680.SH",
    "513880.SH",
    "513900.SH",
    "513990.SH",
    "518880.SH",
    "159934.SZ",
    "518800.SH",
    "159937.SZ",
    "518680.SH",
    "518850.SH",
    "518600.SH",
    "518660.SH",
    "518890.SH",
    "159812.SZ",
    "518860.SH",
]
# 现金管理产品
CASH_SECURITIES = [
    "511990.SH",
    "511880.SH",
    "511660.SH",
    "511850.SH",
    "511810.SH",
    "159001.SZ",
    "511690.SH",
    "159003.SZ",
    "511800.SH",
    "511700.SH",
    "511820.SH",
    "511650.SH",
    "511900.SH",
    "511860.SH",
    "511620.SH",
    "159005.SZ",
    "511980.SH",
    "511600.SH",
    "511830.SH",
    "511950.SH",
    "511670.SH",
    "511920.SH",
    "511960.SH",
    "511970.SH",
    "511910.SH",
    "511770.SH",
    "511930.SH",
]

DEFAULT_PRESET = {
    "security_type": "OTHER",
    "commission_coeff_peramount": 0.001,
    "commission_coeff_today_peramount": 0.001,
    "tax_coeff_peramount": 0.001,
    "price_tick": 0.01,
    "volume_unit": 100,
    "upper_limit_ratio": 100,
    "down_limit_ratio": 0.0,
    "allow_t0": False,
}
