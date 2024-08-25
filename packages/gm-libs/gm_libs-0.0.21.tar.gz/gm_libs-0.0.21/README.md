# 掘金量化的简化函数包（第三方）

个人自用包，出问题了欢迎提 Issue。

## 功能列表

### A 股

#### 获取信息

1. 获取所有指数（股票市场、当前有效）: get_all_index
2. 获取所有股票（股票市场、当前有效）: get_all_security
3. ~~获取龙虎榜股票列表: get_dragon_tiger_list~~
4. 获取交易量统计: l_get_day_volume
5. 获取今日价格信息: l_get_one_day_price
5. 获取当前是否实盘: is_live
6. 获取历史数据: l_history_n

#### 执行交易

1. 买指定数量的股票: `buy_count(stock: str, count: int, price: float)`
2. 卖指定数量的股票: `sell_count(stock: str, count: int, price: float)`
3. 调整仓位（到特定数量）: `order_target_count(stock: str, volume: int, price: float)`
4. 调整仓位（到特定价值）: `order_target_money(stock: str, worth: int, price: float)`

#### 统计模块

【必须】进行初始化：`l_static_init(context)`

执行某个统计：

将 `schedule(statistic_func, date_rule="1d", time_rule="07:00:00")` 放在初始化区域，其中 `statistic_func` 是你期望进行的统计项。

月度统计：

1. 近期净值变动: `l_static_month_rate(context)`

日度统计：

1. 回撤区间统计：`l_static_day_back(context)`，到达历史最高净值后回落，开始计算回撤区间，下次突破最高净值时，记“起点、终点、区间最大回撤比例”为一次回撤区间

#### 记录日志

1. 日志输出且保存: `log_all(level: str, info: str, source: str = "", filetype: str = "")`
2. 日志不输出仅保存: `log_save(level: str, info: str, source: str = "", filetype: str = "")`
3. 日志输出不保存，`gm.print` 即可
4. 获取日志地址: `l_get_log_path()`

## 打包

1. 更新 [pyproject.toml](pyproject.toml) 文件
2. 执行 `./build.sh`
3. 输入 API token

旧的打包方式：

1. 更新 [pyproject.toml](pyproject.toml) 文件
2. 执行 `python -m build`
3. 执行 `python -m pip install twine upload dist/*`
4. 对输入框，输入账号: `__token__` 并回车
5. 最后输入 API token 即可
