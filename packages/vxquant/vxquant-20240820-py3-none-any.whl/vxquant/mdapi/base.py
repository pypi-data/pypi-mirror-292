"""基类"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Union, Optional, Dict, List

import polars as pl
from tqdm import tqdm
from vxutils import to_datetime, Datetime, import_by_config
from vxquant.mdapi.models import VXCalendar, VXInstruments, VXMarketPreset


class VXDataProvider:
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def update_data(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


class VXStorageMixin:
    __storage__: Dict[str, Any]

    def save(self, data: pl.DataFrame, identify: str) -> Any:
        """保存到本地

        Arguments:
            data {pl.DataFrame} -- 带保存的数据
            identify {str} -- 标识符
        """
        raise NotImplementedError

    def read(self, identify: str) -> Any:
        """读取数据

        Arguments:
            identify {str} -- 标识符

        Returns:
            Any -- _description_
        """
        raise NotImplementedError

    def clear(self, identify: str) -> None:
        """清除数据

        Arguments:
            identify {str} -- 标识符

        """
        raise NotImplementedError


class VXCalendarProvider(VXDataProvider, VXStorageMixin):

    def __call__(self) -> VXCalendar:
        cal = VXCalendar()
        try:

            trade_dates = self.read("calendar").filter(pl.col("is_trade_day") == 1)[
                "trade_date"
            ]
            cal.update_data(trade_dates=trade_dates)
        except BaseException as err:
            logging.error(f"Failed to load calendar data: {err}", exc_info=True)
        return cal

    def update_data(self, data: pl.DataFrame) -> None:
        cal = self.__call__()
        cal.update_data(
            trade_dates=data.filter(pl.col("is_trade_day") == 1)["trade_date"]
        )
        self.save(cal.data, "calendar")


class VXInstrumentsProvider(VXDataProvider, VXStorageMixin):
    def __call__(
        self,
        name: str,
    ) -> VXInstruments:

        try:
            registrations = self.read(name)
            return VXInstruments(name=name, registrations=registrations)
        except BaseException as err:
            logging.error(f"Failed to load instruments data: {err}", exc_info=True)
            return VXInstruments(name=name)

    def update_data(self, name: str, data: pl.DataFrame) -> None:
        instruments = VXInstruments(name=name, registrations=data)
        self.save(data=instruments.registrations, identify=name)


class VXHistoryProvider(VXDataProvider, VXStorageMixin):
    __identity__ = ""

    def __call__(
        self,
        symbols: List[str],
        start_date: Optional[Datetime] = None,
        end_date: Optional[Datetime] = None,
    ) -> pl.DataFrame:

        start_dt: datetime = (
            to_datetime(start_date) if start_date is not None else datetime(1990, 1, 1)
        )

        end_dt: datetime = (
            to_datetime(end_date) if end_date is not None else datetime.now()
        )
        unique_symbols = set(symbols)
        if len(unique_symbols) > 200:
            unique_symbols = tqdm(unique_symbols, desc="Loading history data")
        datas = []
        for symbol in unique_symbols:
            data = self.read(symbol)
            if not data.is_empty():
                datas.append(data)
        df = (
            (
                pl.concat(datas)
                .filter(
                    pl.col("trade_date") >= start_dt, pl.col("trade_date") <= end_dt
                )
                .sort(["symbol", "trade_date"])
            )
            if datas
            else pl.DataFrame({})
        )
        return df

    def update_data(
        self,
        data: pl.DataFrame,
    ) -> None:
        pbar = tqdm(data["symbol"].unique())
        for symbol in pbar:
            new_data = data.filter(pl.col("symbol") == symbol)
            if new_data.is_empty():
                continue
            pbar.set_description(f"Updating {symbol} {new_data.shape[0]} records")
            old_data = self.__call__([symbol])
            if old_data.is_empty():
                df = new_data
                self.save(data=df, identify=symbol)
            else:
                df = (
                    pl.concat([old_data, new_data])
                    .sort("trade_date")
                    .with_columns(
                        [
                            pl.when(
                                pl.col("trade_date") == pl.col("trade_date").shift(-1)
                            )
                            .then(pl.lit(True))
                            .otherwise(pl.lit(False))
                            .alias("is_duplicate")
                        ]
                    )
                    .filter(pl.col("is_duplicate").not_())
                    .select(pl.exclude("is_duplicate"))
                    .drop_nulls()
                )
                if not df.is_empty():
                    self.save(data=df, identify=symbol)


class VXDayHistoryProvider(VXHistoryProvider):
    __identity__ = "day"


class VXMinHistoryProvider(VXHistoryProvider):
    __identity__ = "min"


class VXFactorProvider(VXDataProvider, VXStorageMixin):
    def __call__(
        self,
        symbols: List[str],
        factor_name: str,
        start_date: Optional[pl.Datetime] = None,
        end_date: Optional[pl.Datetime] = None,
    ) -> Any:

        start_dt = (
            to_datetime(start_date) if start_date is not None else datetime(1990, 1, 1)
        )
        end_dt = to_datetime(end_date) if end_date is not None else datetime.now()
        data = self.read(factor_name)
        if data.is_empty():
            return pl.DataFrame({})
        return data.filter(
            pl.col("symbol").is_in(symbols),
            pl.col("trade_date") >= start_dt,
            pl.col("trade_date") <= end_dt,
        )

    def update_data(self, data: pl.DataFrame, factor_name: str) -> None:
        """更新因子数据

        Arguments:
            data {pl.DataFrame} -- 因子数据
            factor_name {str} -- 因子名称
        """
        if len(set(data.columns) - set(["symbol", "trade_date", factor_name])) != 0:
            raise ValueError(
                f"Data must have columns: symbol, trade_date, and {factor_name}, but got {set(data.columns)}",
            )

        old_data = self.read(factor_name)
        if old_data.is_empty():

            self.save(data.drop_nulls(), factor_name)
        else:
            df = (
                pl.concat([old_data, data])
                .sort(["trade_date", "symbol"])
                .with_columns(
                    [
                        pl.when(
                            (pl.col("trade_date") == pl.col("trade_date").shift(-1))
                            & (pl.col("symbol") == pl.col("symbol").shift(-1))
                        )
                        .then(pl.lit(True))
                        .otherwise(pl.lit(False))
                        .alias("is_duplicate")
                    ]
                )
                .filter(pl.col("is_duplicate").not_())
                .select(pl.exclude("is_duplicate"))
                .drop_nulls()
            )
            if not df.is_empty():
                print("saving data...")
                self.save(df, factor_name)


class VXMdAPI:
    def __init__(self, **params: Any) -> None:
        if "calendar" in params:
            self._calendar_provider = import_by_config(params["calendar"])
        else:
            self._calendar_provider = VXCalendarProvider()

        if "instruments" in params:
            self._instruments_provider = import_by_config(params["instruments"])
        else:
            self._instruments_provider = VXInstrumentsProvider()

        if "day_history" in params:
            self._day_history_provider = import_by_config(params["day_history"])
        else:
            self._day_history_provider = VXDayHistoryProvider()

        if "min_history" in params:
            self._min_history_provider = import_by_config(params["min_history"])
        else:
            self._min_history_provider = VXMinHistoryProvider()

        if "factor" in params:
            self._factor_provider = import_by_config(params["factor"])
        else:
            self._factor_provider = VXFactorProvider()

    def market_preset(self, symbol: str) -> VXMarketPreset:
        return VXMarketPreset(symbol)

    @property
    def calendar(self) -> VXCalendarProvider:
        return self._calendar_provider

    @property
    def instruments(self) -> VXInstrumentsProvider:
        return self._instruments_provider

    @property
    def day_history(self) -> VXDayHistoryProvider:
        return self._day_history_provider

    @property
    def min_history(self) -> VXMinHistoryProvider:
        return self._min_history_provider

    @property
    def factor(self) -> VXFactorProvider:
        return self._factor_provider


if __name__ == "__main__":
    config = {
        "calendar": {
            "mod_path": "vxquant.mdapi.local.VXLocalCalendarProvider",
            "params": {},
        },
        "instruments": {
            "mod_path": "vxquant.mdapi.local.VXLocalInstrumentsProvider",
            "params": {},
        },
        "day_history": {
            "mod_path": "vxquant.mdapi.local.VXLocalDayHistoryProvider",
            "params": {},
        },
        "min_history": {
            "mod_path": "vxquant.mdapi.local.VXLocalMinHistoryProvider",
            "params": {},
        },
        "factor": {
            "mod_path": "vxquant.mdapi.local.VXLocalFactorProvider",
            "params": {},
        },
    }
    mdapi = VXMdAPI(**config)
    print(mdapi.calendar().next_n_trade_day(n=6))
    symbols = mdapi.instruments("stock").list_instruments()

    for symbol in symbols:
        print(mdapi.market_preset(symbol))
        break

    print(mdapi.day_history(symbols))
