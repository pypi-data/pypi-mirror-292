import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Union, Optional, Dict, List

import polars as pl
from tqdm import tqdm
from vxquant.__base import VXCalendar, VXInstruments
from vxutils import AbstractProvider, to_datetime


class VXDataProvider:
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def update_data(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


class VXStorageMixin:
    __storage__: Dict[str, Any]

    def save(self, data: pl.DataFrame, identify: str) -> Any:
        raise NotImplementedError

    def read(self, identify: str) -> Any:
        raise NotImplementedError

    def clear(self, identify: str) -> None:
        raise NotImplementedError


class VXLocalStorage(VXStorageMixin):

    __storage__: Dict[str, Any] = {"suffix": "csv", "data_dir": Path().home() / ".data"}

    @classmethod
    def init_storage(
        cls,
        data_dir: Optional[Path] = None,
        suffix: Optional[Literal["csv", "parquet"]] = None,
    ) -> None:
        cls.__storage__["suffix"] = suffix
        if data_dir is None:
            cls.__storage__["data_dir"] = Path().home() / ".data"
        else:
            cls.__storage__["data_dir"] = Path(data_dir)
        cls.__storage__["data_dir"].mkdir(exist_ok=True, parents=True)

    def save(self, data: pl.DataFrame, identify: str) -> None:
        if self.__storage__["suffix"] == "csv":
            data.write_csv(
                self.__storage__["data_dir"] / f"{identify}.csv",
                date_format="%Y-%m-%d",
                datetime_format="%Y-%m-%d %H:%M:%S",
            )
        else:
            data.write_parquet(
                self.__storage__["data_dir"] / f"{identify}.parquet",
            )

    def read(self, identify: str) -> pl.DataFrame:
        if self.__storage__["suffix"] == "csv":
            return pl.read_csv(self.__storage__["data_dir"] / f"{identify}.csv")
        else:
            return pl.read_parquet(self.__storage__["data_dir"] / f"{identify}.parquet")

    def clear(self, identify: str) -> None:
        (
            self.__storage__["data_dir"] / f"{identify}.{self.__storage__['suffix']}"
        ).unlink(missing_ok=True)


class VXCalendarProvider(VXDataProvider, VXStorageMixin):
    __identity__ = "calendar"

    def __call__(self) -> VXCalendar:
        cal = VXCalendar()
        try:
            trade_dates = self.read(self.__identity__).filter(
                pl.col("is_trade_day") == 1
            )["trade_date"]
            cal.update_data(trade_dates=trade_dates)
        except BaseException as err:
            logging.error(f"Failed to load calendar data: {err}")
        return cal

    def update_data(self, data: pl.DataFrame) -> None:
        cal = self.__call__()
        cal.update_data(
            trade_dates=data.filter(pl.col("is_trade_day") == 1)["trade_date"]
        )
        self.save(cal.data, self.__identity__)


class VXLocalCalendarProvider(VXCalendarProvider, VXLocalStorage):

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path().home() / ".data"
        self.init_storage(data_dir, "csv")


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


class VXLocalInstrumentsProvider(VXInstrumentsProvider, VXLocalStorage):
    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path().home() / ".data/instruments"
        self.init_storage(data_dir, "csv")


class VXHistoryProvider(VXDataProvider, VXStorageMixin):

    def __call__(
        self,
        symbols: List[str],
        start_date: Optional[pl.Datetime] = None,
        end_date: Optional[pl.Datetime] = None,
    ) -> pl.DataFrame:
        try:
            start_dt: datetime = (
                to_datetime(start_date)
                if start_date is not None
                else datetime(1990, 1, 1)
            )

            end_dt: datetime = (
                to_datetime(end_date) if end_date is not None else datetime.now()
            )
            unique_symbols = set(symbols)
            if len(unique_symbols) > 20:
                unique_symbols = tqdm(unique_symbols, desc="Loading history data")
            datas = []
            for symbol in unique_symbols:
                df = self.read(symbol)
                if df.is_empty():
                    continue
                datas.append(df)
            return pl.concat(datas).filter(
                pl.col("trade_date") >= start_dt, pl.col("trade_date") <= end_dt
            )
        except BaseException as err:
            logging.error(f"Failed to load history data: {err}", exc_info=True)
            return pl.DataFrame(
                {
                    "symbol": [],
                    "trade_date": [],
                    "open": [],
                    "high": [],
                    "low": [],
                    "close": [],
                    "volume": [],
                    "amount": [],
                    "yclose": [],
                }
            )

    def update_data(
        self,
        data: pl.DataFrame,
    ) -> None:
        old_datas = self.read(data["symbol"].to_list())
        data = pl.concat([old_datas, data])
        for symbol in data["symbol"].unique():
            self.save(data.filter(pl.col("symbol") == symbol), symbol)


if __name__ == "__main__":
    import re
    from vxutils import loggerConfig

    loggerConfig()
    name = "stock"
    df = (
        pl.read_csv(
            "C:\\Users\\vex10\\.data\\all.csv",
        )
        .filter(pl.col("sec_type") == name)
        .select(
            pl.col("symbol"),
            start_date=pl.col("list_date").map_elements(
                to_datetime, return_dtype=pl.Datetime
            ),
            end_date=pl.col("delist_date").map_elements(
                to_datetime, return_dtype=pl.Datetime
            ),
        )
    )
    for f in (Path().home() / ".data/instruments/").glob("[cbond.csv|stock.csv]"):
        print(f)

    # provider = VXLocalInstrumentsProvider()
    # provider.update_data(name, df)
    # instruments = provider(name)
    # print(len(instruments.list_instruments()))
