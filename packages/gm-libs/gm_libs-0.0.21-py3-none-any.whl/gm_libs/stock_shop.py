# coding=utf-8
from __future__ import print_function, absolute_import

import random
import os
import pandas as pd
from datetime import datetime, timedelta
from shutil import copyfile
from os import getcwd
from gm.api import *


# 初始化 #
l_config = {"is_live": False}


# 运行初始化
def l_init_run(c):
    # type: (Context) -> None
    global l_config
    l_config["is_live"] = c.mode == MODE_LIVE

    c.l_statics = {
        "month": 0,  # 昨日月份
        "nav": [],  # 获得收益
    }

    # 将代码快照保存一份
    filename = "main.py"
    filepath = "%s/%s" % (getcwd(), filename)
    c.today = None
    l_copy_file_to_log(filepath, filename)


# 每日初始化
def l_init_day(context):
    if context.today is None:
        yesterday = context.now - timedelta(days=1)
        context.today = yesterday
        context.today_str = yesterday.strftime("%Y-%m-%d")

    context.previous = context.today
    context.previous_str = context.today_str

    context.today = context.now
    context.today_str = context.now.strftime("%Y-%m-%d")


# 结束输出
def l_finished(context):
    print("回测完成，请前往\"", l_get_log_path(), "\"查看相关日志。")


# 交易部分 #

# 获取价格
def get_price(stock: str, price: float = 0, offset_price: float = 0):
    if price == 0:
        price_current = current(stock, 'close')
        if len(price_current) == 0:
            log_all("warn", "%s 未能获取到最新价格" % stock, "debug")
            return 0
        price = price_current[0].price + price_current[0].price * 0.03 + offset_price

    return price


# 买指定数量的股票
def buy_count(stock: str, count: int, price: float = 0, offset_price: float = 0):
    return l_buy_count(stock, count, price, offset_price)


# 买指定数量的股票
def l_buy_count(stock: str, count: int, price: float = 0, offset_price: float = 0):
    price = get_price(stock, price, offset_price)
    return order_volume(symbol=stock, volume=count, price=price, order_type=OrderType_Market, side=OrderSide_Buy,
                        position_effect=PositionEffect_Open)


# 卖指定数量的股票
def sell_count(stock: str, count: int, price: float = 0, offset_price: float = 0):
    return l_sell_count(stock, count, price, offset_price)


# 卖指定数量的股票
def l_sell_count(stock: str, count: int, price: float = 0, offset_price: float = 0):
    price = get_price(stock, price, offset_price)

    return order_volume(symbol=stock, volume=count, price=price, order_type=OrderType_Market, side=OrderSide_Sell,
                        position_effect=PositionEffect_Close)


# 调整仓位（到特定数量）
def order_target_count(stock: str, volume: int, price: float = 0, offset_price: float = 0):
    return l_order_target_count(stock, volume, price, offset_price)


# 调整仓位（到特定数量）
def l_order_target_count(stock: str, volume: int, price: float = 0, offset_price: float = 0):
    price = get_price(stock, price, offset_price)

    order_cancel_all()
    return order_target_volume(symbol=stock, volume=volume, price=price, order_type=OrderType_Market,
                               position_side=PositionSide_Long)


# 调整仓位（到特定价值）
def order_target_money(stock: str, worth: int, price: float = 0, offset_price: float = 0):
    return l_order_target_money(stock, worth, price, offset_price)


# 调整仓位（到特定价值）
def l_order_target_money(stock: str, worth: int, price: float = 0, offset_price: float = 0):
    price = get_price(stock, price, offset_price)

    order_cancel_all()
    return order_target_value(symbol=stock, value=worth, price=price, order_type=OrderType_Market,
                              position_side=PositionSide_Long)


# 行情部分 #

# 获取交易量统计
# 掘金的 cur_volume，完全是按照本地数据取的，就没考虑本地数据缺失
def l_get_one_day_volume(symbol: str, end_time: datetime):
    volumes = history(symbol=symbol, frequency="60s", start_time=end_time.replace(hour=9, minute=20),
                      end_time=end_time,
                      fields="volume", skip_suspended=True, fill_missing=None, adjust=ADJUST_NONE,
                      adjust_end_time='', df=True)
    if len(volumes) == 0:
        return 0
    return volumes["volume"].sum()


# 获取今日价格信息
def l_get_one_day_price(symbol: str, end_time: datetime):
    data = history(symbol=symbol, frequency="60s", start_time=end_time.replace(hour=9, minute=20),
                   end_time=end_time,
                   fields="open, close, low, high", skip_suspended=True, fill_missing=None, adjust=ADJUST_NONE,
                   adjust_end_time='', df=True)
    return {
        "open": data["open"].iloc[0],
        "close": data["close"].iloc[-1],
        "low": data["low"].min(),
        "high": data["high"].max(),
    }


# 获取当前是否实盘(Context 解耦)
def l_is_live():
    # type: () -> bool
    global l_config

    return l_config["is_live"]


# 获取当前是否实盘
def is_live(c):
    # type: (Context) -> bool
    return c.mode == MODE_LIVE


# 获取历史数据
def l_history_n(symbol, count, end_time, frequency='1d', fields='close', df=False):
    # type: (str, int, datetime, str, str, bool) -> pd.DataFrame | list
    if l_is_live() is False:
        end_time = end_time - timedelta(days=1)

    return history_n(symbol=symbol, count=count, frequency=frequency, fields=fields, end_time=end_time, df=df)


# 获取 price
def l_current_price(c, stock):
    # type: (Context, str) -> float
    key = ""
    price = []
    if l_is_live():
        price = current(stock, 'price')
        key = "price"
    else:
        price = l_history_n(c, stock, 1, c.now, frequency='60s', fields='close', df=True)
        key = "close"
    if len(price) == 0:
        log_all("warn", "%s 未能获取到最新价格（live）" % stock, "debug")
        return 0

    return price[0][key]


# 日志部分 #

_gm_libs_logs = {
    "dir_path": "",
    "snapshot": "",
}


# 获取日志地址
def l_get_log_path():
    global _gm_libs_logs
    strategy_dir = os.path.basename(os.path.normpath(os.getcwd()))

    if _gm_libs_logs["dir_path"] == "":
        parent_path = r"C:\Users\Public\gm_libs"
        strategy_path = r"C:\Users\Public\gm_libs\%s" % strategy_dir
        _gm_libs_logs["dir_path"] = r"{}\{}\{}".format(parent_path, strategy_dir,
                                                       datetime.today().strftime(
                                                           '%Y-%m-%d %H.%M.%S ') + "%s" % random.randint(1000000,
                                                                                                         9999999)
                                                       )
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)
        if not os.path.exists(strategy_path):
            os.mkdir(strategy_path)
        if not os.path.exists(_gm_libs_logs["dir_path"]):
            os.mkdir(_gm_libs_logs["dir_path"])

    return _gm_libs_logs["dir_path"]


# 日志输出且保存
def log_all(level: str, info: str, source: str = "common"):
    log(level=level, msg=info, source=source)
    text = "【{}】 {}".format(level, info)
    print(text)
    append(text, source)


# 日志不输出仅保存
def log_save(level: str, info: str, source: str = "common"):
    log(level=level, msg=info, source=source)
    text = "【{}】 {}".format(level, info)
    append(text, source)


# 复制文件到日志文件夹
def l_copy_file_to_log(filepath: str, filename: str):
    copyfile(filepath, l_get_log_path() + "\\" + filename)


# 追加信息到日志文件
def append(text: str, source: str = ""):
    global _gm_libs_logs
    all_path = l_get_log_path()

    if source not in _gm_libs_logs:
        _gm_libs_logs[source] = True
        log_file = open(r"{}\{}.log".format(all_path, source), "w+", encoding="utf-8")
    else:
        log_file = open(r"{}\{}.log".format(all_path, source), "a", encoding="utf-8")

    log_file.writelines("{}\n".format(text))
    log_file.close()


# 时间函数 #

# 获取去年时间（day 大于本月最后一天时，取本月最后一天）
def l_get_last_year(now: datetime, day: int = 0):
    now.replace(year=now.year - 1)

    return now


# 获取上个季度时间（day 大于本月最后一天时，取本月最后一天）
def l_get_last_season(now: datetime, day: int = 0):
    now = l_get_last_month(now, day)
    now = l_get_last_month(now, day)
    now = l_get_last_month(now, day)

    return now


# 获取上月时间（day 大于本月最后一天时，取本月最后一天）
def l_get_last_month(now: datetime, day: int = 0):
    result = now.replace(day=1) - timedelta(days=1)

    if day == 0:
        day = now.day
    max_day = get_month_max_day(now.year, now.month)
    if max_day < day:
        day = max_day

    result.replace(day)
    return result


# 获取当月最大天数
def get_month_max_day(year: int, month: int):
    if (month == 2) and ((year % 4 == 0) or ((year % 100 == 0) and (year % 400 == 0))):
        return 29
    elif month == 2:
        return 28
    elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 31
    else:
        return 30


# 统计函数 #
# 计算近期净值变动率（3、6、12 月）
def l_static_month_rate(context):
    context.l_statics["nav"].append(context.account().cash.nav)
    if len(context.l_statics["nav"]) > 12:
        del context.l_statics["nav"][0]

    # 输出日志
    nav_len = len(context.l_statics["nav"])
    year_rate = 0
    half_year_rate = 0
    season_rate = 0
    if nav_len >= 12:
        year_rate = context.l_statics["nav"][nav_len - 1] / context.l_statics["nav"][nav_len - 12] * 100
    if nav_len >= 6:
        half_year_rate = context.l_statics["nav"][nav_len - 1] / context.l_statics["nav"][nav_len - 6] * 100
    if nav_len >= 3:
        season_rate = context.l_statics["nav"][nav_len - 1] / context.l_statics["nav"][nav_len - 3] * 100

    log_all("static", "【基准收益】日期: %s | 净值: %d | 12月: %.1f%% | 6月: %.1f%% | 3月: %.1f%%" % (
        context.today_str, context.account().cash.nav, year_rate, half_year_rate, season_rate))


# 按日计算回撤区间
def l_static_day_back(context):
    # todo 如果有回撤起点：相比昨日，今天跌，记录回撤起点（昨日净值）
    # todo 如果无回撤起点：相比昨日，今天涨，记录回撤日志，清理回撤起点
    pass
