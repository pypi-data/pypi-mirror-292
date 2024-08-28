import logging
from pathlib import Path
from typing import Literal, Optional
import polars as pl


from .base import (
    VXCalendarProvider,
    VXStorageMixin,
    VXDayHistoryProvider,
    VXFactorProvider,
    VXMinHistoryProvider,
    VXInstrumentsProvider,
)


class VXLocalStorage(VXStorageMixin):

    __data_dir__: Path = Path().home() / ".data"
    __suffix__: Literal["csv", "parquet"] = "csv"

    @classmethod
    def init_storage(
        cls,
        data_dir: Optional[Path] = None,
        suffix: Optional[Literal["csv", "parquet"]] = None,
    ) -> None:
        cls.__suffix__ = suffix if suffix is not None else "csv"
        if data_dir:
            cls.__data_dir__ = Path(data_dir)
        else:
            cls.__data_dir__ = Path().home() / ".data"

        cls.__data_dir__.mkdir(exist_ok=True, parents=True)

    def save(self, data: pl.DataFrame, identify: str) -> None:

        if self.__suffix__ == "csv":
            data.write_csv(
                self.__data_dir__ / f"{identify}.csv",
                date_format="%Y-%m-%d",
                datetime_format="%Y-%m-%d %H:%M:%S",
            )
        else:
            data.write_parquet(
                self.__data_dir__ / f"{identify}.parquet",
            )

    def read(self, identify: str) -> pl.DataFrame:

        filename = self.__data_dir__ / f"{identify}.{self.__suffix__}"

        if not filename.exists():
            logging.debug(f"File {filename} not exists. ")
            return pl.DataFrame({})

        return (
            pl.read_csv(self.__data_dir__ / f"{identify}.csv")
            if self.__suffix__ == "csv"
            else pl.read_parquet(self.__data_dir__ / f"{identify}.parquet")
        )

    def clear(self, identify: str) -> None:
        (self.__data_dir__ / f"{identify}.{self.__suffix__}").unlink(missing_ok=True)


class VXLocalCalendarProvider(VXCalendarProvider, VXLocalStorage):

    def __init__(self, data_root: Optional[Path] = None) -> None:
        if data_root:
            data_dir = Path(data_root)
        else:
            data_dir = Path().home() / ".data"

        self.init_storage(data_dir, "csv")


class VXLocalInstrumentsProvider(VXInstrumentsProvider, VXLocalStorage):

    def __init__(self, data_root: Optional[Path] = None) -> None:
        if data_root:
            data_dir = Path(data_root) / "instruments"
        else:
            data_dir = Path().home() / ".data/instruments"

        self.init_storage(data_dir, "csv")


class VXLocalDayHistoryProvider(VXDayHistoryProvider, VXLocalStorage):

    def __init__(self, data_root: Optional[Path] = None) -> None:
        if data_root:
            data_dir = Path(data_root) / f"history/{self.__identity__}/"
        else:
            data_dir = Path().home() / f".data/history/{self.__identity__}/"
        self.init_storage(data_dir=data_dir, suffix="parquet")


class VXLocalMinHistoryProvider(VXMinHistoryProvider, VXLocalStorage):

    def __init__(self, data_root: Optional[Path] = None) -> None:
        if data_root:
            data_dir = Path(data_root) / f"history/{self.__identity__}/"
        else:
            data_dir = Path().home() / f".data/history/{self.__identity__}/"

        self.init_storage(data_dir=data_dir, suffix="parquet")


class VXLocalFactorProvider(VXFactorProvider, VXLocalStorage):

    def __init__(self, data_root: Optional[Path] = None) -> None:
        if data_root:
            data_dir = Path(data_root) / "factors"
        else:
            data_dir = Path().home() / ".data/factors"

        self.init_storage(data_dir, "parquet")


DEFAULT_DATA_ROOT = Path().home() / ".data"

LOCAL_CONFIG = {
    "calendar": {
        "mod_path": "vxquant.mdapi.local.VXLocalCalendarProvider",
        "params": {"data_root": DEFAULT_DATA_ROOT},
    },
    "instruments": {
        "mod_path": "vxquant.mdapi.local.VXLocalInstrumentsProvider",
        "params": {"data_root": DEFAULT_DATA_ROOT},
    },
    "day_history": {
        "mod_path": "vxquant.mdapi.local.VXLocalDayHistoryProvider",
        "params": {"data_root": DEFAULT_DATA_ROOT},
    },
    "min_history": {
        "mod_path": "vxquant.mdapi.local.VXLocalMinHistoryProvider",
        "params": {"data_root": DEFAULT_DATA_ROOT},
    },
    "factor": {
        "mod_path": "vxquant.mdapi.local.VXLocalFactorProvider",
        "params": {"data_root": DEFAULT_DATA_ROOT},
    },
}
