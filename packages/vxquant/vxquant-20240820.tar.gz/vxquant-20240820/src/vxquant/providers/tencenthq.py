import re
import time
import logging
import requests
import polars as pl
from itertools import chain
from typing import Dict, List
from concurrent.futures import Future
from vxutils import VXContext
from vxutils.executor import VXBasicPool, VXBasicWorkerFactory, VXTaskItem
from vxquant.models.nomalize import to_symbol


_TENCENT_HQ_URL = "https://qt.gtimg.cn/q=%s&timestamp=%s"
_HEADERS = {
    "Accept-Encoding": "gzip, deflate, sdch",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/54.0.2840.100 "
        "Safari/537.36"
    ),
}


def tencent_formatter(exchange: str, code: str) -> str:
    """腾讯证券代码格式化"""
    exchange = exchange.replace("SE", "").lower()
    return f"{exchange}{code}"


_TENCENT_COLS = [
    "symbol",  # *  0: 未知
    "name",  # *  1: 名字
    "code",  # *  2: 代码
    "lasttrade",  # *  3: 当前价格
    "yclose",  # *  4: 昨收
    "open",  # *  5: 今开
    "volume",  # *  6: 成交量（手）
    "out_volume",  # *  7: 外盘
    "in_volume",  # *  8: 内盘
    "bid1_p",  # *  9: 买一
    "bid1_v",  # * 10: 买一量（手）
    "bid2_p",  # * 11: 买二
    "bid2_v",  # * 12: 买二量（手）
    "bid3_p",  # * 13: 买三
    "bid3_v",  # * 14: 买三量（手）
    "bid4_p",  # * 15: 买四
    "bid4_v",  # * 16: 买四量（手）
    "bid5_p",  # * 17: 买五
    "bid5_v",  # * 18: 买五量（手）
    "ask1_p",  # * 19: 卖一
    "ask1_v",  # * 20: 卖一量
    "ask2_p",  # * 21: 卖二
    "ask2_v",  # * 22: 卖二量
    "ask3_p",  # * 23: 卖三
    "ask3_v",  # * 24: 卖三量
    "ask4_p",  # * 25: 卖四
    "ask4_v",  # * 26: 卖四量
    "ask5_p",  # * 27: 卖五
    "ask5_v",  # * 28: 卖五量
    "last_vol",  # * 29: 最近逐笔成交
    "created_dt",  # * 30: 时间
    "pct_change_p",  # * 31: 涨跌
    "pct_change",  # * 32: 涨跌%
    "high",  # * 33: 最高
    "low",  # * 34: 最低
    "p_v_a",  # * 35: 价格/成交量（手）/成交额
    "volume2",  # * 36: 成交量（手）
    "amount",  # * 37: 成交额（万）
    "turnover_rate",  # * 38: 换手率
    "pe_ttm",  # * 39: 市盈率
    "unknow2",  # * 40:
    "high2",  # * 41: 最高
    "low2",  # * 42: 最低
    "amplitude",  # * 43: 振幅
    "circ_mv",  # * 44: 流通市值
    "total_mv",  # * 45: 总市值
    "pb_mrq",  # * 46: 市净率
    "uplimit",  # * 47: 涨停价
    "downlimit",  # * 48: 跌停价
    "vr",  # * 量比
]


def tencent_tick_parser(stock_line: str) -> Dict[str, str]:
    """解析程序

    Arguments:
        stock_line {str} -- 股票信息行

    Returns:
        Dict[str, vxTick] -- vxticks data
    """

    stock = stock_line.split("~")
    # for i, d in enumerate(stock):
    #    print(i, d)
    if len(stock) <= 49:
        logging.warning(f"skip stock line: {len(stock_line)}")
        return dict()

    return dict(zip(_TENCENT_COLS, stock))


class VXTencentHQTaskItem(VXTaskItem):
    def __init__(self, symbols: List[str]) -> None:
        self.symbols = symbols
        self.future = Future()

    def __call__(self, context: VXContext) -> None:
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            url = _TENCENT_HQ_URL % (
                ",".join(
                    map(
                        lambda s: to_symbol(s, formatter=tencent_formatter),
                        self.symbols,
                    )
                ),
                int(time.time() * 1000),
            )

            resq = context.session.get(url, timeout=0.5)
            resq.raise_for_status()
            text = resq.text.strip()
            result = [
                tencent_tick_parser(stock_line) for stock_line in text.split(";")[:-1]
            ]
            self.future.set_result(result)

        except requests.exceptions.HTTPError as e:
            logging.error(f"获取{url}数据出错: {e}.")
            self.future.set_exception(e)
        except BaseException as e:
            self.future.set_exception(e)


class VXTencentHQSessionWorker(VXBasicWorkerFactory):
    def pre_run(self) -> None:
        self._context.session = requests.Session()
        self._context.session.headers.update(_HEADERS)
        resq = self._context.session.get(
            "https://stockapp.finance.qq.com/mstats/#", timeout=1
        )
        resq.raise_for_status()
        logging.debug(f"网络连通成功{resq.status_code}...")

    def post_run(self) -> None:
        self._context.session.close()
        logging.debug("网络连接关闭...")


class VXTencentHQ:
    def __init__(self, worker_cnt: int = 5) -> None:
        self._sessionpool = VXBasicPool(
            worker_cnt, "TencentHQPool", worker_factory=VXTencentHQSessionWorker
        )
        self._grep_stock_code = re.compile(r"(?<=_)\w+")

    def __call__(self, symbols: List[str]) -> pl.DataFrame:
        """获取最新的ticks 数据

        Returns:
            Dict[str,vxTick] -- 返回最新的tick数据
        """

        tasks = [
            VXTencentHQTaskItem(symbols[i : i + 500])
            for i in range(0, len(symbols), 500)
        ]

        stock_lines = self._sessionpool.map(tasks)

        return (
            pl.DataFrame([data for data in chain(*stock_lines) if data])
            .select(
                pl.exclude(
                    [
                        "code",
                        "unknow2",
                        "high2",
                        "low2",
                        "volume2",
                        "p_v_a",
                        "pct_change_p",
                    ]
                ),
            )
            .with_columns(
                [
                    pl.col("symbol").map_elements(
                        lambda s: to_symbol(self._grep_stock_code.search(s).group()),
                        return_dtype=pl.Utf8,
                    ),
                    pl.exclude(
                        [
                            "symbol",
                            "name",
                            "created_dt",
                        ]
                    ).cast(pl.Float64, strict=False),
                ]
            )
            .with_columns(
                [
                    pl.col(
                        [
                            "volume",
                            "ask1_v",
                            "ask2_v",
                            "ask3_v",
                            "ask4_v",
                            "ask5_v",
                            "bid1_v",
                            "bid2_v",
                            "bid3_v",
                            "bid4_v",
                            "bid5_v",
                            "last_vol",
                        ]
                    )
                    * 100,
                    pl.col(["amount"]) * 10000,
                    pl.col("created_dt").str.to_datetime("%Y%m%d%H%M%S"),
                ]
            )
        )
