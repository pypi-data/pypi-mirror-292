"""运行脚本"""

try:
    import simplejson as json
except ImportError:
    import json

import logging
from pathlib import Path
from argparse import ArgumentParser, Namespace
from typing import Dict, Any
from vxsched import vxsched, load_modules
from vxutils import loggerConfig, VXContext
from vxquant.mdapi.local import DEFAULT_DATA_ROOT

__default_config__ = {
    "events": {
        "before_trade": "09:10:00",
        "on_trade": "09:30:00",
        "on_hans": "10:00:00",
        "on_noon_break": "11:30:00",
        "after_noon_break": "13:00:00",
        "before_close": "14:50:00",
        "on_close": "15:00:00",
        "after_close": "15:30:00",
        "on_repo": "15:05:00",
        "on_settle": "22:00:00",
    },
    "wechat_bot": "",
    "mdapi": {
        "calendar": {
            "mod_path": "vxquant.mdapi.local.VXLocalCalendarProvider",
            "params": {"data_root": DEFAULT_DATA_ROOT.as_posix()},
        },
        "instruments": {
            "mod_path": "vxquant.mdapi.local.VXLocalInstrumentsProvider",
            "params": {"data_root": DEFAULT_DATA_ROOT.as_posix()},
        },
        "day_history": {
            "mod_path": "vxquant.mdapi.local.VXLocalDayHistoryProvider",
            "params": {"data_root": DEFAULT_DATA_ROOT.as_posix()},
        },
        "min_history": {
            "mod_path": "vxquant.mdapi.local.VXLocalMinHistoryProvider",
            "params": {"data_root": DEFAULT_DATA_ROOT.as_posix()},
        },
        "factor": {
            "mod_path": "vxquant.mdapi.local.VXLocalFactorProvider",
            "params": {"data_root": DEFAULT_DATA_ROOT.as_posix()},
        },
    },
    "tdapi": {},
}


def init(args: Namespace) -> None:
    loggerConfig()
    target = Path(args.target).absolute()
    logging.info("初始化模块: %s", target)

    for d in ["mod", "etc", "data", "log"]:
        if (target / d).exists():
            logging.warning("目录已存在: %s", target / d)
        else:
            (target / d).mkdir(parents=True)
            logging.info("创建目录: %s", target / d)

    if not (target / "etc/default_config.json").exists():
        with open(target / "etc/default_config.json", "w") as f:
            json.dump(__default_config__, f, indent=4)
            logging.info("创建默认配置文件: %s", target / "etc/default_config.json")


def run_strategy(args: Namespace) -> None:

    level = "DEBUG" if args.verbose else "INFO"
    if args.log:
        loggerConfig(level=level, filename=args.log)
        logging.debug("启用日志文件: %s", args.log)
    else:
        loggerConfig(level=level, colored=True)

    configfile = Path(args.config)
    config: Dict[str, Any] = {"settings": {}}
    if configfile.exists():
        with open(configfile, "r") as f:
            settings = json.load(f)
            config["settings"] = settings

    context = VXContext(**config)
    vxsched.set_context(context)
    mod = Path(args.mod)
    if mod.exists():
        from vxquant.scripts.system import (
            init_system,
            before_trade_system,
            daily_init_system,
        )

        load_modules(mod_path=mod)
        vxsched.run()
    else:
        logging.error("模块目录不存在: %s", mod)


def main() -> None:
    parser = ArgumentParser(description="vxquant运行脚本")
    subparser = parser.add_subparsers(description="运行子命令")

    # 初始化模块
    init_parser = subparser.add_parser("init", help="初始化模块")
    init_parser.add_argument("target", type=str, default=".", help="目标目录")
    init_parser.set_defaults(func=init)

    # 运行策略模块
    run_parser = subparser.add_parser("strategy", help="运行模块")
    run_parser.add_argument(
        "-c", "--config", default="etc/config.json", help="配置文件"
    )
    run_parser.add_argument("-m", "--mod", default="mod", help="事件列表")
    run_parser.add_argument("-l", "--log", default="", help="日志目录")
    run_parser.add_argument(
        "-v", "--verbose", default=False, help="调试模式", action="store_true"
    )
    run_parser.set_defaults(func=run_strategy)

    # 数据管理模块

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
