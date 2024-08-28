"""行情接口基类、交易接口基类"""

from typing import Literal, Union, Optional, List, Dict, Any, Tuple
from vxquant.__base import VXCalendar, VXInstruments, VXMarketPreset, VXSymbol
from vxquant.models import VXCashInfo, VXOrder, VXExecRpt, VXPosition


class VXMdAPI:
    """行情API"""

    def instruments(self, name: str) -> VXInstruments:
        """获取股票池"""
        raise NotImplementedError

    def calendar(self, exchange: Literal["CN"] = "CN") -> VXCalendar:
        """交易日历"""
        raise NotImplementedError

    def market_preset(self, symbol: Union[str, VXSymbol]) -> VXMarketPreset:
        """市场预设"""
        return VXMarketPreset(symbol)

    def current(self, *symbols: str) -> pl.DataFrame:
        """获取当前行情"""
        raise NotImplementedError

    def history(
        self,
        symbols: List[str],
        start_date: Optional[Datetime] = None,
        end_date: Optional[Datetime] = None,
        freq: Literal["d", "min"] = "d",
    ) -> pl.DataFrame:
        """获取历史行情"""
        raise NotImplementedError

    def factor(
        self,
        factor_name: str,
        instruments: Union[VXInstruments, List[str]],
        start_date: Optional[Datetime] = None,
        end_date: Optional[Datetime] = None,
    ) -> pl.DataFrame:
        """获取因子"""
        raise NotImplementedError


class VXTdAPI:
    """交易API"""

    def get_cash(self) -> VXCashInfo:
        """获取现金"""
        raise NotImplementedError

    def get_positions(self, symbol: Optional[str] = None) -> pl.DataFrame:
        """持仓"""
        raise NotImplementedError

    def get_orders(self, order_id: str = "", is_open: bool = True) -> pl.DataFrame:
        """订单"""
        raise NotImplementedError

    def get_trades(self, trade_id: str = "") -> pl.DataFrame:
        raise NotImplementedError

    def current(self, *symbols: str) -> pl.DataFrame:
        raise NotImplementedError

    def order_batch(self, *orders: VXOrder) -> List[VXOrder]:
        """批量下单"""
        raise NotImplementedError

    def order_volume(
        self, symbol: str, volume: int, price: Optional[float] = None
    ) -> VXOrder:
        """下单"""
        raise NotImplementedError

    def order_cancel(self, order: Union[str, VXOrder]) -> VXOrder:
        """撤单"""
        raise NotImplementedError

    def auto_repo(
        self,
        reversed_balance: float = 0.0,
        symbols: Optional[List[str]] = None,
        strategy_id: str = "",
        order_remark: str = "",
    ) -> Optional[VXOrder]:
        """自动回购"""
        raise NotImplementedError

    def auto_ipo_bond_purchase(
        self,
        symbols: Optional[List[str]] = None,
        strategy_id: str = "",
        order_remark: str = "",
    ) -> List[VXOrder]:
        """自动新债申购函数

        Arguments:
            symbols {List[str]} -- 申购证券代码列表，若为空则根据策略自动选择，否则按照列表顺序申购
            strategy_id {str} -- 策略ID
            order_remark {str} -- 交易备注

        Returns:
            List[VXOrder] -- _description_
        """
        raise NotImplementedError
