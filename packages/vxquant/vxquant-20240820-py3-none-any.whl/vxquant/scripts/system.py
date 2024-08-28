"""系统设置"""

import subprocess
import logging
from datetime import datetime, timedelta
from vxsched.core import ON_EXIT_EVENT, ON_INIT_EVENT
from vxsched import vxsched, EVERY, DAILY, ONCE, VXEvent
from vxutils import VXContext, to_today, import_by_config
from vxquant.mdapi.base import VXMdAPI

__all__ = ["init_system", "daily_init_system", "before_trade_system"]

DAILY_INIT_EVENT = "__DAILY_INIT__"
EVERY_SECONDS_EVENT = "__EVERY_SECONDS__"


@vxsched.register(ON_INIT_EVENT)
def init_system(context: VXContext, event: VXEvent) -> None:
    """初始化系统"""
    # 初始化微信通知
    context.notify_messages = []
    if "wechat_bot" in context.settings and context.settings["wechat_bot"]:
        from vxutils.networking.wechat import vxWeChatBot

        context.wechat_bot = vxWeChatBot(context.settings["wechat_bot"])
        logging.info(f"初始化微信通知: url={context.settings['wechat_bot'][:-20]}***")
    else:
        context.wechat_bot = None

    # 初始化mdapi
    if "mdapi" in context.settings and context.settings["mdapi"]:
        context.mdapi = VXMdAPI(**context.settings["mdapi"])
    else:
        from vxquant.mdapi.local import LOCAL_CONFIG

        context.mdapi = VXMdAPI(**LOCAL_CONFIG)
    logging.info(
        f"测试今天是否交易日: {datetime.now():%Y-%m-%d} ==> {context.mdapi.calendar().is_trade_day(datetime.now())}"
    )

    # 初始化tdapi
    if "tdapi" in context.settings and context.settings["tdapi"]:
        context.tdapi = import_by_config(context.settings["tdapi"])

    logging.info(f"添加{DAILY_INIT_EVENT}事件 每日09:00:00触发")
    vxsched.publish(
        DAILY_INIT_EVENT, channel="system", priority=0, trigger=DAILY("09:00:00")
    )
    vxsched.publish(
        EVERY_SECONDS_EVENT,
        channel="system",
        priority=0,
        trigger=EVERY(1),
    )

    if to_today("09:00:01") < datetime.now():
        logging.info(f"添加{DAILY_INIT_EVENT}事件 立即09:00:00触发")
        vxsched.publish(
            DAILY_INIT_EVENT,
            channel="no_normal",
            priority=0,
        )


@vxsched.register(DAILY_INIT_EVENT)
def daily_init_system(context: VXContext, event: VXEvent) -> None:
    """每日初始化系统"""
    if not context.mdapi.calendar().is_trade_day(datetime.now()):
        if context.wechat_bot:
            context.wechat_bot.send_text(
                f"今日非交易日,下一个交易日是: {context.mdapi.calendar.next_n_trade_day()}"
            )

        logging.info(
            "今日非交易日,下一个交易日是: %s ",
            context.mdapi.calendar.next_n_trade_day(),
        )
        return
    logging.info(f"今日是交易日： {datetime.now():%Y-%m-%d}")

    if "events" not in context.settings or len(context.settings["events"]) == 0:
        raise ValueError("未配置events, 请检查配置文件")

    # 初始化mdapi
    if "mdapi" in context.settings and context.settings["mdapi"]:
        context.mdapi = VXMdAPI(**context.settings["mdapi"])
    else:
        from vxquant.mdapi.local import LOCAL_CONFIG

        context.mdapi = VXMdAPI(**LOCAL_CONFIG)
    logging.info(
        f"测试今天是否交易日: {datetime.now():%Y-%m-%d} ==> {context.mdapi.calendar().is_trade_day(datetime.now())}"
    )

    # 初始化tdapi
    if "tdapi" in context.settings and context.settings["tdapi"]:
        context.tdapi = import_by_config(context.settings["tdapi"])

    for event_type, rum_timestr in context.settings["events"].items():
        trigger_dt = to_today(rum_timestr)
        if trigger_dt < datetime.now():
            logging.warning(f"事件{event_type}触发时间已过: {trigger_dt}")
            continue

        logging.info(f"添加{event_type}事件 每日{rum_timestr}触发")
        vxsched.publish(
            event_type,
            channel="system",
            priority=0,
            trigger=ONCE(to_today(rum_timestr)),
        )

    logging.info("添加on_tick事件 每3秒触发一次")
    vxsched.publish(
        "on_tick",
        channel="system",
        priority=0,
        trigger=EVERY(
            3,
            start_dt=to_today("09:30:00"),
            end_dt=to_today("11:31:00"),
        ),
    )

    vxsched.publish(
        "on_tick",
        channel="system",
        priority=0,
        trigger=EVERY(
            3,
            start_dt=to_today("13:00:00"),
            end_dt=to_today("15:00:00"),
        ),
    )

    logging.info("添加on_min事件 每60秒触发一次")
    vxsched.publish(
        "on_min",
        channel="system",
        priority=0,
        trigger=EVERY(
            60,
            start_dt=to_today("09:30:00"),
            end_dt=to_today("11:31:00"),
        ),
    )

    vxsched.publish(
        "on_min",
        channel="system",
        priority=0,
        trigger=EVERY(
            60,
            start_dt=to_today(timestr="13:00:00"),
            end_dt=to_today(timestr="15:00:00"),
        ),
    )

    if to_today("09:00:00") < datetime.now() < to_today("15:00:00"):
        vxsched.publish(
            "before_trade",
            channel="not_normal",
            priority=0,
            trigger=ONCE(to_today("09:10:00")),
        )


@vxsched.register("before_trade")
def before_trade_system(context: VXContext, event: VXEvent) -> None:
    """开盘前执行系统任务"""
    logging.error(f"开盘前执行系统任务 {event}")


@vxsched.register(EVERY_SECONDS_EVENT)
def on_event_second_system(context: VXContext, event: VXEvent) -> None:
    """每秒执行系统任务"""
    if context.wechat_bot:
        messages = context.notify_messages[:5]
        context.notify_messages = context.notify_messages[5:]
        for msg in messages:
            context.wechat_bot.send_text(msg)
    else:
        logging.warning(f"抛弃微信消息: {context.wechat_msgs}")
        context.notify_messages = []


@vxsched.register("on_settle")
def on_settle(context: VXContext, event: VXEvent) -> None:
    """结算"""
    # 检查数据中日历是否有更新
    calendar = context.mdapi.calendar()
    if (calendar.max - datetime.today()).days() < 7:
        vxsched.publish(
            "update_calendar_data",
            data={"start": calendar.max, "end": calendar.max + timedelta(days=365)},
            channel="data",
            priority=100,
        )

    # 更新instruments 数据
    vxsched.publish(
        "update_instruments_data",
        channel="data",
        priority=100,
    )

    # 更新day_history 数据
    vxsched.publish(
        "update_day_history_data",
        channel="data",
        priority=100,
    )

    # 更新min_history 数据
    vxsched.publish(
        "update_min_history_data",
        channel="data",
        priority=100,
    )

    # 更新factor 数据
    vxsched.publish(
        "update_factor_data",
        channel="data",
        priority=100,
    )
