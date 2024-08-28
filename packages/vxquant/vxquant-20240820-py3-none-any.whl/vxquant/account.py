"""账户信息"""

import polars as pl
from pathlib import Path
from datetime import datetime
from threading import Lock
from typing import Optional, Union, Literal, Union
from vxquant.models import VXPosition, VXCashInfo, VXOrder, VXExecRpt

_EMPTY_ACCOUNTS = pl.DataFrame(
    {
        "account_id": [],
        "balance": [],
        "ynav": [],
        "channel": [],
        "settle_dt": [],
    },
    schema={
        "account_id": pl.Utf8,
        "balance": pl.Float64,
        "ynav": pl.Float64,
        "channel": pl.Utf8,
        "settle_dt": pl.Datetime,
    },
)
_EMPTY_POSITIONS = pl.DataFrame(
    {
        k: [v]
        for k, v in VXPosition(account_id="", symbol="000001.SH").model_dump().items()
    },
).clear()

_EMPTY_ORDERS = pl.DataFrame(
    {k: [v] for k, v in VXOrder().model_dump().items()},
).clear()

_EMPTY_EXEC_RPTS = pl.DataFrame(
    {k: [v] for k, v in VXExecRpt().model_dump().items()},
).clear()

_EMPTY_HISTORY = pl.DataFrame(
    {
        "account_id": [],
        "balance": [],
        "ynav": [],
        "channel": [],
        "settle_dt": [],
        "market_value": [],
        "fpnl": [],
        "frozen": [],
        "nav": [],
    },
    schema={
        "account_id": pl.Utf8,
        "balance": pl.Float64,
        "ynav": pl.Float64,
        "channel": pl.Utf8,
        "settle_dt": pl.Datetime,
        "market_value": pl.Float64,
        "fpnl": pl.Float64,
        "frozen": pl.Float64,
        "nav": pl.Float64,
    },
)


class VXPortfolio:
    def __init__(
        self,
        accounts: Optional[pl.DataFrame] = None,
        positions: Optional[pl.DataFrame] = None,
        orders: Optional[pl.DataFrame] = None,
        exec_rpts: Optional[pl.DataFrame] = None,
        history: Optional[pl.DataFrame] = None,
    ) -> None:

        self._accounts = (
            _EMPTY_ACCOUNTS.clone()
            if accounts is None
            else accounts.select(
                ["account_id", "balance", "ynav", "channel", "settle_dt"]
            )
        )
        self._positions = _EMPTY_POSITIONS.clone() if positions is None else positions
        self._orders = _EMPTY_ORDERS.clone() if orders is None else orders
        self._exec_rpts = _EMPTY_EXEC_RPTS.clone() if exec_rpts is None else exec_rpts
        self._history = _EMPTY_HISTORY.clone() if history is None else history
        self._lock = Lock()

    def save(self, dir_root: Union[str, Path]) -> None:
        if dir_root is None:
            dir_root = Path().home() / ".data/portfolio"

        if isinstance(dir_root, str):
            dir_root = Path(dir_root)
        dir_root.mkdir(exist_ok=True, parents=True)

        # 全量更新
        if self._accounts.shape[0] > 0:
            self._accounts.write_csv(dir_root / "accounts.csv")

        # 全量更新
        if self._positions.shape[0] > 0:
            self._positions.write_csv(dir_root / "positions.csv")

        # 增量更新
        if (dir_root / "orders.csv").exists():
            orders = pl.read_csv(dir_root / "orders.csv", try_parse_dates=True)
            orders = pl.concat(
                [
                    orders.filter(
                        pl.col("order_id").is_in(self._orders["order_id"]).not_()
                    ),
                    self._orders,
                ]
            )
        else:
            orders = self._orders
        if orders.shape[0] > 0:
            orders.write_csv(dir_root / "orders.csv")

        # 增量更新
        if (dir_root / "exec_rpts.csv").exists():
            exec_rpts = pl.read_csv(dir_root / "exec_rpts.csv", try_parse_dates=True)
            exec_rpts = pl.concat(
                [
                    exec_rpts.filter(
                        pl.col("execrpt_id").is_in(self._exec_rpts["execrpt_id"]).not_()
                    ),
                    self._exec_rpts,
                ]
            )
        else:
            exec_rpts = self._exec_rpts
        if exec_rpts.shape[0] > 0:
            exec_rpts.write_csv(dir_root / "exec_rpts.csv")

        if (dir_root / "history.csv").exists():
            history = pl.read_csv(dir_root / "history.csv", try_parse_dates=True)
            history = (
                pl.concat([history, self._history])
                if history.shape[0] > 0
                else self._history
            )
        else:
            history = self._history

        history = (
            history.sort(["account_id", "settle_dt"])
            .with_columns(
                is_dupplicated=pl.when(
                    (pl.col("account_id") == pl.col("account_id").shift(-1))
                    & (pl.col("settle_dt") == pl.col("settle_dt").shift(-1))
                )
                .then(pl.lit(True))
                .otherwise(pl.lit(False))
            )
            .filter(pl.col("is_dupplicated").not_())
            .select(pl.exclude(["is_dupplicated"]))
        )

        if history.shape[0] > 0:
            history.write_csv(dir_root / "history.csv")

    @classmethod
    def load(cls, dir_root: Union[str, Path]) -> "VXPortfolio":
        if isinstance(dir_root, str):
            dir_root = Path(dir_root)

        accounts = (
            pl.read_csv(
                dir_root / "accounts.csv",
                try_parse_dates=True,
                schema=_EMPTY_ACCOUNTS.schema,
            )
            if (dir_root / "accounts.csv").exists()
            else None
        )
        positions = (
            pl.read_csv(
                dir_root / "positions.csv",
                try_parse_dates=True,
                truncate_ragged_lines=True,
                schema=_EMPTY_POSITIONS.schema,
            )
            if (dir_root / "positions.csv").exists()
            else None
        )
        orders = (
            pl.read_csv(
                dir_root / "orders.csv",
                try_parse_dates=True,
                schema=_EMPTY_ORDERS.schema,
            )
            if (dir_root / "orders.csv").exists()
            else None
        )
        exec_rpts = (
            pl.read_csv(
                dir_root / "exec_rpts.csv",
                try_parse_dates=True,
                schema=_EMPTY_EXEC_RPTS.schema,
            )
            if (dir_root / "exec_rpts.csv").exists()
            else None
        )
        history = (
            pl.read_csv(
                dir_root / "history.csv",
                try_parse_dates=True,
                # truncate_ragged_lines=True,
                schema=_EMPTY_HISTORY.schema,
            )
            if (dir_root / "history.csv").exists()
            else None
        )
        return cls(accounts, positions, orders, exec_rpts, history)

    def create_account(
        self,
        account_id: str,
        balance: float = 1000000,
        channel: str = "local",
        if_exists: Literal["ignore", "replace"] = "ignore",
    ) -> None:
        with self._lock:
            if (if_exists == "replace") or (
                account_id not in self._accounts["account_id"]
            ):
                self._accounts = pl.concat(
                    [
                        self._accounts.filter(pl.col("account_id") != account_id),
                        pl.DataFrame(
                            {
                                "account_id": [account_id],
                                "balance": [balance],
                                "ynav": [balance],
                                "channel": [channel],
                                "settle_dt": [datetime.now()],
                            },
                            schema={
                                "account_id": pl.Utf8,
                                "balance": pl.Float64,
                                "ynav": pl.Float64,
                                "channel": pl.Utf8,
                                "settle_dt": pl.Datetime,
                            },
                        ),
                    ]
                )

    def get_account(self, account_id: str) -> Optional[VXCashInfo]:
        df = self._accounts.filter(pl.col("account_id") == account_id)
        if df.shape[0] == 0:
            return None
        cash = VXCashInfo(**df.to_dicts()[0])
        cash.market_value = self._positions.filter(pl.col("account_id") == account_id)[
            "market_value"
        ].sum()
        cash.fpnl = self._positions.filter(pl.col("account_id") == account_id)[
            "fpnl"
        ].sum()
        cash.order_frozen = round(
            self._orders.filter(
                pl.col("account_id") == account_id,
                pl.col("status").is_in(
                    [
                        "PendingNew",
                        "New",
                        "PartiallyFilled",
                    ]
                ),
            )
            .select(frozen=pl.col("volume") * pl.col("price") * 1.003)["frozen"]
            .sum(),
            2,
        )
        return cash

    def get_order(self, order_id: str) -> Optional[VXOrder]:
        df = self._orders.filter(pl.col("order_id") == order_id)
        if df.shape[0] > 0:
            return VXOrder(**df.to_dicts()[0])
        return None

    def get_position(self, account_id: str, symbol: str) -> VXPosition:
        """获取持仓信息，如果没有仓位，则返回空仓位信息

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 证券代码

        Returns:
            VXPosition -- 持仓信息
        """

        df = self._positions.filter(
            (pl.col("account_id") == account_id) & (pl.col("symbol") == symbol)
        )
        if df.shape[0] > 0:
            return VXPosition(**df.to_dicts()[0])
        return VXPosition(account_id=account_id, symbol=symbol)

    def on_settle(
        self, settle_date: Optional[datetime] = None, dir_root: Union[str, Path] = None
    ) -> None:
        """日结处理

        Arguments:
            settle_date {datetime} -- 日结日期
        """
        if settle_date is None:
            settle_date = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=999
            )

        # 更新委托订单，未成交的订单
        self._orders = self._orders.with_columns(
            status=pl.when(
                pl.col("status").is_in(["PendingNew", "New", "PartiallyFilled"])
            )
            .then(pl.lit("Expired"))
            .otherwise(pl.col("status")),
        )

        # 更新positios的volume volume_his,volume_today
        self._positions = self._positions.with_columns(
            volumt_today=pl.lit(0),
            volume_his=pl.col("volume_today") + pl.col("volume_his"),
            volume=pl.col("volume_today") + pl.col("volume_his"),
        )

        df = self._positions.group_by("account_id").agg(
            market_value=pl.sum("market_value"),
            fpnl=pl.sum("fpnl"),
        )

        self._history = pl.concat(
            [
                self._history,
                self._accounts.join(df, on="account_id")
                .fill_null(0)
                .with_columns(
                    settle_dt=pl.lit(
                        settle_date.replace(
                            hour=23, minute=59, second=59, microsecond=999
                        )
                    ),
                    frozen=pl.lit(0.0),
                    nav=pl.col("balance") + pl.col("market_value"),
                ),
            ]
        )

        if dir_root is None:
            dir_root = Path().home() / ".data/portfolio"
        self.save(dir_root)

    def on_price_change(self, ticks: pl.DataFrame) -> None:
        """价格变动更新

        Arguments:
            ticks {pl.DataFrame} -- 最新价格数据
        """
        with self._lock:
            ticks = ticks.select(
                pl.col("symbol"), pl.col("lasttrade").alias("new_lasttrade")
            )
            self._positions = (
                self._positions.join(ticks, on="symbol")
                .with_columns(
                    market_value=pl.when(pl.col("new_lasttrade").is_not_null())
                    .then(pl.col("new_lasttrade") * pl.col("volume"))
                    .otherwise(pl.col("market_value")),
                    lasttrade=pl.when(pl.col("new_lasttrade").is_not_null())
                    .then(pl.col("new_lasttrade"))
                    .otherwise(pl.col("lasttrade")),
                    fpnl=pl.when(pl.col("new_lasttrade").is_not_null())
                    .then(pl.col("new_lasttrade") * pl.col("volume") - pl.col("cost"))
                    .otherwise(pl.col("fpnl")),
                )
                .select(pl.exclude(["new_lasttrade"]))
            )

    def on_order_status(self, order: VXOrder) -> None:
        """成交状态更新

        Arguments:
            order {VXOrder} -- 成交信息
        """
        with self._lock:
            update_order = self.get_order(order.order_id)
            if (
                update_order is None
                or update_order.filled_volume < order.filled_volume
                or order.status
                in [
                    "Filled",
                    "Canceled",
                    "Expired",
                    "Rejected",
                ]
            ):
                update_order = order
                self._orders = pl.concat(
                    [
                        self._orders.filter(pl.col("order_id") != order.order_id),
                        pl.DataFrame([order.model_dump()], schema=self._orders.schema),
                    ]
                )

    def on_execution_report(self, exec_rpt: VXExecRpt) -> None:
        """更新成交状态

        Arguments:
            exec_rpt {VXExecRpt} -- _description_
        """
        if exec_rpt.execrpt_id in self._exec_rpts["execrpt_id"]:
            return

        with self._lock:
            position = self.get_position(exec_rpt.account_id, exec_rpt.symbol)
            self._exec_rpts = pl.concat(
                [
                    self._exec_rpts,
                    pl.DataFrame(
                        [exec_rpt.model_dump()], schema=self._exec_rpts.schema
                    ),
                ]
            )

            position.lasttrade = exec_rpt.price
            if exec_rpt.order_side == "Buy":
                position.volume_today += exec_rpt.volume
                position.cost += exec_rpt.volume * exec_rpt.price + exec_rpt.commission
                self._accounts = self._accounts.with_columns(
                    pl.when(pl.col("account_id") == exec_rpt.account_id)
                    .then(
                        pl.col("balance")
                        - exec_rpt.volume * exec_rpt.price
                        - exec_rpt.commission
                    )
                    .otherwise(pl.col("balance"))
                )
            elif exec_rpt.order_side == "Sell":
                position.volume_today -= exec_rpt.volume
                position.cost -= exec_rpt.volume * exec_rpt.price - exec_rpt.commission
                self._accounts = self._accounts.with_columns(
                    pl.when(pl.col("account_id") == exec_rpt.account_id)
                    .then(
                        pl.col("balance")
                        + exec_rpt.volume * exec_rpt.price
                        - exec_rpt.commission
                    )
                    .otherwise(pl.col("balance"))
                )
            self._positions = pl.concat(
                [
                    self._positions.filter(
                        pl.col("account_id") != exec_rpt.account_id,
                        pl.col("symbol") != exec_rpt.symbol,
                    ),
                    pl.DataFrame(
                        [position.model_dump()], schema=self._positions.schema
                    ),
                ]
            )


if __name__ == "__main__":

    portfilio = VXPortfolio.load(Path().home() / ".data/portfolio")
    portfilio.on_settle(datetime.now())
    portfilio.create_account("A0001", 1_00000)
    # print(portfilio._accounts)
    # print(portfilio._positions)
    # print(portfilio._orders)
    # print(portfilio._exec_rpts)
    # portfilio.create_account("A0001", 2_00000, if_exists="ignore")

    # print(portfilio.get_position("A0001", "000001.SH"))
    order = VXOrder(
        order_id="O0002",
        account_id="A0001",
        symbol="000001.SH",
        order_side="Buy",
        order_type="Limit",
        price=11,
        volume=1000,
        order_remark="A0001",
    )
    portfilio.on_order_status(order)
    print(portfilio.get_order("O0002"))
    order.filled_volume = 11
    order.filled_amount = 10000
    order.filled_commission += 1
    exec_rpt = VXExecRpt(
        account_id="A0001",
        execrpt_id="E0002",
        symbol="000001.SH",
        order_id="O0001",
        order_side="Buy",
        price=9.89,
        volume=100,
        commission=1,
    )
    # *
    portfilio.on_execution_report(exec_rpt)
    print(portfilio.get_position("A0001", "000001.SH"))
    # *print(portfilio.get_account("A0001"))
    portfilio.save(Path().home() / ".data/portfolio")
