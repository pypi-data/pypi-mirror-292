import polars as pl
import logging
import json
import re
from functools import lru_cache
from pathlib import Path
from collections import defaultdict, namedtuple
from datetime import datetime, date, timedelta
from typing import (
    List,
    Union,
    Dict,
    Optional,
    Any,
    Literal,
    Iterator,
    Callable,
)
from pydantic import Field
from vxutils import Datetime, to_datetime, to_json
from vxutils.datamodel.core import VXDataModel
from vxquant.constants import (
    DEFAULT_PRESET,
    T0_ETFLOF,
    CASH_SECURITIES,
    DEFULAT_SYMBOL_MAP,
)


__all__ = [
    "default_formatter",
    "symbol_parser",
    "to_symbol",
    "VXSymbol",
    "VXCalendar",
    "VXInstruments",
    "VXMarketPreset",
    "VXSubPortfolio",
    "VXPortfolio",
]


VXSymbol = namedtuple("Symbol", ["exchange", "code"])

_CODE_TO_EXCHANGE = {
    "0": "SZSE",
    "1": "SZSE",
    "2": "SZSE",
    "3": "SZSE",
    "4": "BJSE",
    "5": "SHSE",
    "6": "SHSE",
    "7": "SHSE",
    "8": "BJSE",
    "9": "SHSE",
}


def default_formatter(symbol: VXSymbol) -> str:
    return f"{symbol.code}.{symbol.exchange.upper()[:2]}"


def symbol_parser(symbol: str) -> VXSymbol:
    # todo 用正则表达式进行进一步优化
    symbol = symbol.strip().upper()

    match_obj = re.match(r"^(\d{6,10})$", symbol)
    if match_obj:
        code = match_obj[1]
        exchange = _CODE_TO_EXCHANGE.get(code[0], "UNKNOWN")
        return VXSymbol(exchange, code)

    match_obj = re.match(r"^[A-Za-z]{2,4}.?([0-9]{6,10})$", symbol)

    if not match_obj:
        match_obj = re.match(r"^([0-9]{6,10}).?[A-Za-z]{2,4}$", symbol)

    if match_obj is None:
        raise ValueError(f"{symbol} format is not support.")

    code = match_obj[1]
    exchange = symbol.replace("SE", "").replace(".", "").replace(code, "")
    if exchange in {"OF", "ETF", "LOF", ""}:
        exchange = _CODE_TO_EXCHANGE.get(code[0], "UNKNOWN")
    elif exchange in {"XSHG", "XSZG", "XBJG", "XSHE", "XSZE", "XBJE"}:
        exchange = exchange[1:3]
    exchange = exchange if len(exchange) > 2 else f"{exchange}SE"
    return VXSymbol(exchange.upper(), code)


@lru_cache(200)
def to_symbol(
    instrument: str, *, formatter: Callable[[VXSymbol], Any] = default_formatter
) -> Any:
    """格式化symbol

    Arguments:
        instrument {str} -- 需要格式化的symbol

    Keyword Arguments:
        formatter {Callable[[str, str], str]} -- 格式化函数 (default: {default_formatter})

    Returns:
        str -- 格式化后的symbol
    """
    if instrument.upper() in {"CNY", "CACH"}:
        return "CNY"

    symbol = symbol_parser(instrument)
    return formatter(symbol)


class VXCalendar:
    def __init__(
        self,
        trade_dates: Optional[Union[pl.Series, List[date], List[datetime]]] = None,
    ):
        self._data = pl.DataFrame(
            {
                "trade_date": pl.date_range(
                    date(1990, 1, 1), date.today().replace(month=12, day=31), eager=True
                )
            }
        ).with_columns(
            [
                pl.lit(False).cast(pl.Boolean).alias("is_trade_day"),
            ]
        )
        if trade_dates:
            self.update_data(trade_dates)

    @property
    def data(self) -> pl.DataFrame:
        return self._data

    def update_data(
        self, trade_dates: Union[pl.Series, List[Union[datetime, date, str, float]]]
    ) -> None:
        """更新交易日数据"""
        if not isinstance(trade_dates, pl.Series):
            trade_dates = pl.Series(trade_dates)

        trade_dates = trade_dates.map_elements(
            lambda x: to_datetime(x).date(), return_dtype=pl.Date
        )

        if max(trade_dates) > self._data["trade_date"].max():
            self._data = pl.concat(
                [
                    self._data,
                    pl.DataFrame(
                        {
                            "trade_date": pl.date_range(
                                self._data["trade_date"].max() + timedelta(days=1),
                                max(trade_dates).replace(month=12, day=31),
                                eager=True,
                            ),
                        }
                    ),
                ]
            )

        self._data = self._data.with_columns(
            pl.when(pl.col("trade_date").is_in(trade_dates))
            .then(True)
            .otherwise(pl.col("is_trade_day"))
            .alias("is_trade_day")
        )

    @property
    def max(self) -> date:
        return self._data["trade_date"].max()

    def add_holidays(
        self,
        start_date: Union[str, date, datetime, float],
        end_date: Union[str, date, datetime, float],
        holidays: List[Union[str, date, datetime, float]],
    ) -> None:
        """添加节假日"""
        holidays: pl.Series = pl.Series(holidays).map_elements(
            lambda x: to_datetime(x).date(), return_dtype=pl.Date
        )
        if holidays:
            start_date = max(to_datetime(start_date).date(), holidays.min())
            end_date = min(to_datetime(end_date).date(), holidays.max())
        else:
            start_date = to_datetime(start_date).date()
            end_date = to_datetime(end_date).date()
        trade_dates = pl.DataFrame(
            {"trade_date": pl.date_range(start_date, end_date, eager=True)}
        ).with_columns(
            pl.col("trade_date").not_().is_in(holidays).alias("is_trade_day")
        )[
            "trade_date"
        ]
        self.update_data(trade_dates)

    def is_trade_day(
        self,
        input_date: Optional[Union[datetime, date, float, str]] = None,
    ) -> bool:
        """判断是否交易日"""
        input_date = (
            to_datetime(input_date).date() if input_date is not None else date.today()
        )
        return (
            input_date in self._data.filter(pl.col("is_trade_day") == 1)["trade_date"]
        )

    def next_n_trade_day(
        self,
        n: int = 1,
        input_date: Optional[Union[datetime, date, float, str]] = None,
    ) -> date:
        """获取下n个交易日"""
        if n < 1:
            raise ValueError("n should be greater than 0")

        input_date = (
            to_datetime(input_date).date() if input_date is not None else date.today()
        )
        return self._data.filter(pl.col("trade_date") > input_date)["trade_date"][n - 1]

    def prev_n_trade_day(
        self,
        n: int = 1,
        input_date: Optional[Union[datetime, date, float, str]] = None,
    ) -> date:
        """获取前n个交易日"""
        if n < 1:
            raise ValueError("n should be greater than 0")

        input_date = (
            to_datetime(input_date).date() if input_date is not None else date.today()
        )
        return self._data.filter(pl.col("trade_date") < input_date)["trade_date"][-n]

    def date_range(
        self,
        start_date: Union[str, date, datetime, float],
        end_date: Union[str, date, datetime, float],
        perion: Literal["D", "W", "M"] = "D",
    ) -> pl.Series:
        """获取日期范围"""
        start_date = to_datetime(start_date).date()
        end_date = to_datetime(end_date).date()
        return self._data.filter(
            [pl.col("trade_date") >= start_date, pl.col("trade_date") <= end_date]
        )["trade_date"]


class VXInstruments:
    """股票池类"""

    def __init__(self, name: str, registrations: Optional[pl.DataFrame] = None) -> None:
        self._name = name
        self._registrations = (
            registrations.with_columns(
                [
                    pl.col("start_date").map_elements(
                        to_datetime, return_dtype=pl.Datetime
                    ),
                    pl.col("end_date").map_elements(
                        to_datetime, return_dtype=pl.Datetime
                    ),
                ]
            )
            if registrations is not None
            else pl.DataFrame(
                {"symbol": [], "start_date": [], "end_date": []},
                schema={
                    "symbol": pl.Utf8,
                    "start_date": pl.Datetime,
                    "end_date": pl.Datetime,
                },
            )
        )
        self._last_updated_dt = (
            datetime.today()
            if self._registrations.height == 0
            else to_datetime(self._registrations["end_date"].max())
        )

    @property
    def name(self) -> str:
        """股票池名称"""
        return self._name

    def __str__(self) -> str:
        return f"< 证券池({self._name})  最新证券:\n {self.list_instruments()} >"

    @property
    def registrations(self) -> pl.DataFrame:
        """股票池出入注册表

        Returns:
            pl.DataFrame -- 注册表
        """
        return self._registrations

    def list_instruments(self, trade_date: Optional[Datetime] = None) -> List[str]:
        """列出股票池中的证券

        Keyword Arguments:
            trade_date {Datetime} -- 交易日，若为空，则为当前日期 (default: {None})

        Returns:
            List[InstrumentType] -- 股票列表
        """
        trade_date = (
            to_datetime(trade_date) if trade_date is not None else datetime.today()
        )

        inst = self._registrations.filter(
            [(pl.col("start_date") <= trade_date), (pl.col("end_date") >= trade_date)]
        )

        return inst["symbol"].to_list()

    def add_instrument(
        self,
        symbol: str,
        start_date: Datetime,
        end_date: Optional[Datetime] = None,
        #
    ) -> "VXInstruments":
        try:
            symbol = to_symbol(symbol)
            start_date = to_datetime(start_date)
            end_date = to_datetime(end_date) if end_date else start_date
        except Exception as e:
            raise ValueError(f"参数错误: {e}")

        self._registrations.vstack(
            pl.DataFrame(
                [
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                ],
                schema={
                    "symbol": str,
                    "start_date": pl.Datetime,
                    "end_date": pl.Datetime,
                },
            ),
            in_place=True,
        )
        return self

    def update_components(
        self,
        instruments: List[str],
        start_date: Datetime,
        end_date: Datetime,
    ) -> "VXInstruments":
        """按增量更新股票池"""

        end_date = to_datetime(end_date)
        start_date = to_datetime(start_date)

        new_instruments = pl.DataFrame(
            [
                {
                    "symbol": to_symbol(symbol),
                    "start_date": start_date,
                    "end_date": end_date,
                }
                for symbol in instruments
            ],
            schema={
                "symbol": pl.Utf8,
                "start_date": pl.Datetime,
                "end_date": pl.Datetime,
            },
        )

        self._registrations = pl.concat([self._registrations, new_instruments])
        self.rebuild()
        return self

    @classmethod
    def load(cls, name: str, instruments_file: Union[str, Path]) -> "VXInstruments":
        if isinstance(instruments_file, str):
            instruments_file = Path(instruments_file)

        if not instruments_file.exists():
            raise FileNotFoundError(f"{instruments_file} 不存在。")
        if instruments_file.suffix in {".csv"}:
            registrations = pl.read_csv(instruments_file)
        elif instruments_file.suffix in {".parquet"}:
            registrations = pl.read_parquet(instruments_file)
        else:
            raise ValueError(f"{instruments_file} 文件格式不支持。")

        return VXInstruments(name, registrations)

    def dump(
        self,
        instruments_file: Union[str, Path],
        *,
        file_suffix: Literal["csv", "parquet"] = "csv",
    ) -> "VXInstruments":
        """保存相关信息"""
        if isinstance(instruments_file, str):
            instruments_file = Path(instruments_file)

        if Path(instruments_file).is_dir():
            instruments_file = Path(instruments_file, f"{self._name}.{file_suffix}")

        if file_suffix == "csv":
            self._registrations.write_csv(instruments_file)
            logging.info(f"股票池:{self._name} 保存{instruments_file} 完成。")
        elif file_suffix == "parquet":
            self._registrations.write_parquet(instruments_file)
            logging.info(f"股票池:{self._name} 保存{instruments_file} 完成。")
        else:
            raise ValueError(f"{file_suffix} 文件格式不支持。")
        return self

    def rebuild(self) -> "VXInstruments":
        """重建登记表"""

        new_registrations = []
        temp_registrations = {}

        for rows in self._registrations.sort(by=["symbol", "start_date"]).iter_rows(
            named=True
        ):
            symbol = rows["symbol"]

            if symbol not in temp_registrations:
                temp_registrations[symbol] = rows
            elif (
                temp_registrations[symbol]["end_date"] + timedelta(days=1)
                >= rows["start_date"]
                and temp_registrations[symbol]["end_date"] < rows["end_date"]
            ):
                temp_registrations[symbol]["end_date"] = rows["end_date"]

            elif (temp_registrations[symbol]["end_date"]) < rows["start_date"]:
                new_registrations.append(temp_registrations[symbol])
                temp_registrations[symbol] = rows

        new_registrations.extend(temp_registrations.values())
        self._registrations = pl.DataFrame(new_registrations)

        return self

    def all_instruments(self) -> List[str]:
        return self._registrations["symbol"].unique().to_list()

    def union(self, *others: "VXInstruments") -> "VXInstruments":
        """合并另外一个股票池"""
        if len(others) == 1 and isinstance(others[0], (list, tuple)):
            others = others[0]

        registrations = [self._registrations] + [
            other._registrations for other in others
        ]
        self._registrations = pl.concat(registrations)
        self.rebuild()
        return self

    def intersect(self, other: "VXInstruments") -> "VXInstruments":
        """交集"""

        new_registrations: List[Dict[str, Any]] = []
        for rows in self.registrations.sort(["symbol", "start_date"]).iter_rows(
            named=True
        ):
            new_registrations.extend(
                {
                    "symbol": rows["symbol"],
                    "start_date": max(rows["start_date"], other_rows["start_date"]),
                    "end_date": min(rows["end_date"], other_rows["end_date"]),
                    # "weight": rows["weight"],
                }
                for other_rows in other.registrations.filter(
                    (pl.col("start_date") < rows["end_date"])
                    & (pl.col("end_date") > rows["start_date"])
                    & (pl.col("symbol") == rows["symbol"])
                ).iter_rows(named=True)
            )

        self._registrations = (
            pl.DataFrame(new_registrations)
            if new_registrations
            else pl.DataFrame(
                # {"symbol": [], "start_date": [], "end_date": [], "weight": []},
                {"symbol": [], "start_date": [], "end_date": [], "weight": []},
                schema={
                    "symbol": pl.Utf8,
                    "start_date": pl.Datetime,
                    "end_date": pl.Datetime,
                    # "weight": pl.Float64,
                },
            )
        )

        self.rebuild()
        return self

    def difference(self, other: "VXInstruments") -> "VXInstruments":
        """差集"""
        new_registrations = []
        for rows in self.registrations.sort(["symbol", "start_date"]).iter_rows(
            named=True
        ):
            for other_rows in (
                other.registrations.filter(
                    (pl.col("start_date") <= rows["end_date"])
                    & (pl.col("end_date") >= rows["start_date"])
                    & (pl.col("symbol") == rows["symbol"])
                )
                .sort("start_date")
                .iter_rows(named=True)
            ):
                if rows["start_date"] < other_rows["start_date"]:
                    new_registrations.append(
                        {
                            "symbol": rows["symbol"],
                            "start_date": rows["start_date"],
                            "end_date": other_rows["start_date"] - timedelta(days=1),
                        }
                    )

                rows["start_date"] = other_rows["end_date"] + timedelta(days=1)

                if rows["start_date"] > rows["end_date"]:
                    break

            if rows["start_date"] <= rows["end_date"]:
                new_registrations.append(rows)

        self._registrations = pl.DataFrame(new_registrations)
        self.rebuild()
        return self


class VXMarketPreset:
    t0_securities = T0_ETFLOF
    cash_securities = CASH_SECURITIES

    def __init__(self, symbol: Union[str, VXSymbol]) -> None:
        symbol = symbol if isinstance(symbol, VXSymbol) else symbol_parser(symbol)
        self.symbol = default_formatter(symbol)
        data = {"symbol": self.symbol}
        if (symbol.exchange, symbol.code[:3]) in DEFULAT_SYMBOL_MAP:
            data = DEFULAT_SYMBOL_MAP[(symbol.exchange, symbol.code[:3])]
        elif (symbol.exchange, symbol.code[:2]) in DEFULAT_SYMBOL_MAP:
            data = DEFULAT_SYMBOL_MAP[(symbol.exchange, symbol.code[:2])]
        else:
            data = DEFAULT_PRESET

        if self.symbol in self.t0_securities or (self.symbol in self.cash_securities):
            data["allow_t0"] = True

        for key, value in data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"< MarketPreset({self.symbol}):{to_json(self.__dict__)} >"


class VXSubPortfolio(VXDataModel):
    """子组合信息"""

    subportfolio_id: str = Field(..., description="子组合名称")
    strategy: str = Field(..., description="子组合策略")
    ratio: float = Field(..., description="子组合占比")
    weights: Dict[str, float] = Field(..., description="权重信息")

    def rebalance(
        self, weights: Optional[Dict[str, float]] = None, ratio: Optional[float] = None
    ) -> None:
        """调整权重"""
        if weights is not None:
            self.weights = weights

        if ratio is not None:
            self.ratio = ratio

    def update_weight(self, symbol: str, weight: float) -> None:
        """添加权重"""
        if weight != 0:
            self.weights[symbol] = weight
        else:
            self.weights.pop(symbol, None)


class VXPortfolio:
    """组合信息"""

    def __init__(
        self, subportfolios: Optional[Dict[str, VXSubPortfolio]] = None
    ) -> None:
        self._subportfolios: Dict[str, VXSubPortfolio] = {}
        if subportfolios:
            self._subportfolios.update(subportfolios)

    def __iter__(self) -> Iterator[VXSubPortfolio]:
        return iter(self._subportfolios.values())

    def __getitem__(self, key: str) -> VXSubPortfolio:
        return self._subportfolios[key]

    def __str__(self) -> str:
        return to_json(self.message)

    @classmethod
    def load(cls, config: Union[str, Path]) -> "VXPortfolio":
        """从配置文件中读取组合信息"""
        with open(config, "r") as f:
            data = json.load(f)
        for name, subportfolio in data.items():
            data[name] = VXSubPortfolio(**subportfolio)
        return cls(data)

    def dump(self, path: Union[str, Path]) -> None:
        """将组合信息保存到配置文件"""
        with open(path, "w") as f:
            f.write(to_json(self.message))

    def create_subportfolio(
        self,
        subportfolio_id: str,
        strategy: str,
        ratio: float,
        weights: Optional[Dict[str, float]] = None,
    ) -> VXSubPortfolio:
        """创建子组合"""
        subportfolio = VXSubPortfolio(
            subportfolio_id=subportfolio_id,
            strategy=strategy,
            ratio=ratio,
            weights=weights or {},
        )
        self._subportfolios[subportfolio_id] = subportfolio
        return subportfolio

    def remove_subportfolio(self, subportfolio_id: str) -> None:
        """删除子组合"""
        self._subportfolios.pop(subportfolio_id, None)

    def adjust_ratio(self, subportfolio_id: str, ratio: float) -> None:
        """调整子组合占比"""
        self._subportfolios[subportfolio_id].ratio = ratio

    def rebalance(
        self,
        subportfolio_id: str,
        weights: Optional[Dict[str, float]] = None,
        ratio: Optional[float] = None,
    ) -> None:
        """调整子组合权重"""
        self._subportfolios[subportfolio_id].rebalance(weights, ratio)

    def update_weight(self, subportfolio_id: str, symbol: str, weight: float) -> None:
        """更新子组合权重"""
        self._subportfolios[subportfolio_id].update_weight(symbol, weight)

    @property
    def position_ratio(self) -> float:
        """持仓占比"""
        return sum(sub.ratio for sub in self._subportfolios.values())

    @property
    def weights(self) -> pl.DataFrame:
        """转换为polars格式"""
        data = defaultdict(list)
        for sub in self:
            for symbol, weight in sub.weights.items():
                data["symbol"].append(symbol)
                data["subportfolio_id"].append(sub.subportfolio_id)
                data["strategy"].append(sub.strategy)
                data["ratio"].append(sub.ratio)
                data["weight"].append(weight)
        return (
            pl.DataFrame(data)
            .with_columns(
                [
                    pl.col("weight") / pl.sum("weight").over("subportfolio_id"),
                    (
                        pl.col("ratio")
                        * pl.col("weight")
                        / pl.sum("weight").over("subportfolio_id")
                    ).alias("target_weight"),
                ]
            )
            .group_by("symbol")
            .agg(pl.sum("target_weight").alias("weight"))
            .sort("weight", descending=True)
        )

    @property
    def message(self) -> Dict[str, Any]:
        """组合信息"""
        data = {}
        for name, subportfolio in self._subportfolios.items():
            data[name] = subportfolio.model_dump()

        return data

    def to_df(self) -> pl.DataFrame:
        data = defaultdict(list)
        for sub in self:
            for symbol, weight in sub.weights.items():
                data["symbol"].append(symbol)
                data["subportfolio_id"].append(sub.subportfolio_id)
                data["strategy"].append(sub.strategy)
                data["ratio"].append(sub.ratio)
                data["weight"].append(weight)

        return pl.DataFrame(data).sort(["subportfolio_id", "symbol"])
