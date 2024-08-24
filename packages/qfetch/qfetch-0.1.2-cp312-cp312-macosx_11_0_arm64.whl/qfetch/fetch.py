from datetime import date, datetime
from typing import List, Dict, Union, Optional, Set


import qfetch.qfetch as fetch
from qfetch.qfetch import to_std_code


import pandas as pd


def _str_to_datetime(d: str) -> datetime:
    nd = None
    for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y-%m-%d %H', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']:
        try:
            nd = datetime.strptime(d, fmt)
            return nd
        except ValueError:
            pass
    if nd == None:
        raise Exception('date format invalid: {}'.format(d))


def _to_dataframe(to_frame, data):
    if to_frame and data is not None:
        data = pd.DataFrame(data)
    return data


def _utc_ts_to_datetime(df: Optional[pd.DataFrame], field: str):
    if df is not None and type(df) != list and len(df) > 0:
        df[field] = df[field].map(lambda date: datetime.strptime(
            '{}'.format(date), '%Y%m%d%H%M%S'))
    return df


async def fetch_trade_date(*, to_frame=True) -> Union[Set[int], pd.DataFrame]:
    """获取交易日

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True.

    Returns:
        Union[Set[int], pd.DataFrame]: [trade_date]
    """
    data = await fetch.fetch_trade_date()
    data = _to_dataframe(to_frame, data)
    data.columns = ['trade_date']
    return data


def block_fetch_trade_date(*, to_frame=True) -> Union[Set[int], pd.DataFrame]:
    """获取交易日(阻塞版本)

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[Set[int], pd.DataFrame]: [trade_date]
    """
    data = fetch.block_fetch_trade_date()
    if to_frame:
        data = pd.DataFrame(data)
    data.columns = ['trade_date']
    return data


async def fetch_next_trade_date(*, date: Union[date, datetime, str]) -> date:
    """获取下一个交易日

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        date: 下一个交易日
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    data = await fetch.fetch_next_trade_date(date)
    return datetime.strptime('{} 00:00:00'.format(data), '%Y%m%d %H:%M:%S').date()


def block_fetch_next_trade_date(*, date: Union[date, datetime, str]) -> date:
    """获取下一个交易日(阻塞版本)

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        date: 下一个交易日
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    data = fetch.block_fetch_next_trade_date(date)
    return datetime.strptime('{} 00:00:00'.format(data), '%Y%m%d %H:%M:%S').date()


async def fetch_prev_trade_date(*, date: Union[date, datetime, str]) -> date:
    """获取前一个交易日

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        date: 前一个交易日
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    data = await fetch.fetch_prev_trade_date(date)
    return datetime.strptime('{} 00:00:00'.format(data), '%Y%m%d %H:%M:%S').date()


def block_fetch_prev_trade_date(*, date: Union[date, datetime, str]) -> date:
    """获取前一个交易日(阻塞版本)

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        date: 前一个交易日
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    data = fetch.block_fetch_prev_trade_date(date)
    return datetime.strptime('{} 00:00:00'.format(data), '%Y%m%d %H:%M:%S').date()


async def fetch_is_trade_date(*, date: Union[date, datetime, str]) -> bool:
    """判断是否是交易日

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        bool: True/False
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    return await fetch.fetch_is_trade_date(date)


def block_fetch_is_trade_date(*, date: Union[date, datetime, str]) -> bool:
    """判断是否是交易日（阻塞版本）

    Args:
        date (Union[date, datetime, str]): 参考交易日

    Returns:
        bool: True/False
    """
    date = _str_to_datetime(date) if type(date) == type('') else date
    return fetch.block_fetch_is_trade_date(date)


async def fetch_rt_quot(*, code: Union[str, List[str]], to_frame=True) -> Union[Dict[str, Dict], pd.DataFrame]:
    """获取实时行情

    Args:
        code (Union[str, List[str]]): 代码或代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[Dict[str, Dict], pd.DataFrame]: 
    """
    if type(code) == type(''):
        code = [code]
    data = await fetch.fetch_rt_quot(code)
    if to_frame and data != None and len(data) > 0:
        data = pd.DataFrame([v for v in data.values()])
    return data


def block_fetch_rt_quot(*, code: Union[str, List[str]], to_frame=True) -> Union[Dict[str, Dict], pd.DataFrame]:
    """获取实时行情（阻塞版本）

    Args:
        code (Union[str, List[str]]): 代码或代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[Dict[str, Dict], pd.DataFrame]: 
    """
    if type(code) == type(''):
        code = [code]
    data = fetch.block_fetch_rt_quot(code)
    if to_frame and data != None and len(data) > 0:
        data = pd.DataFrame([v for v in data.values()])
    return data


async def fetch_stock_rt_quot(*, codes: Optional[Union[str, List[str]]], to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """全量股票行情，注意调用频率，有可能被封

    Args:
        codes (Optional[Union[str, List[str]]]): 股票代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    if type(codes) == type(''):
        codes = [codes]
    data = await fetch.fetch_stock_rt_quot(codes)
    return _to_dataframe(to_frame, data=data)


def block_fetch_stock_rt_quot(*, codes: Optional[Union[str, List[str]]], to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """全量股票行情，注意调用频率，有可能被封（阻塞版本）

    Args:
        codes (Optional[Union[str, List[str]]]): 股票代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    if type(codes) == type(''):
        codes = [codes]
    data = fetch.block_fetch_stock_rt_quot(codes)
    return _to_dataframe(to_frame, data=data)

# bond


async def fetch_bond_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取可转债信息

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_bond_info())


def block_fetch_bond_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取可转债信息（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_bond_info())


async def fetch_bond_bar(*, code: str, name: str,
                         stock_code: str, stock_name: str,
                         freq: Optional[int] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         skip_rt: bool = True,
                         to_frame=True, ) -> Dict:
    """获取可转债K线信息

    Args:
        code (str): 代码
        name (str): 名称
        stock_code (str): 股票代码
        stock_name (str): 股票名称
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Dict: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_bond_bar(code=code, name=name,
                                      stock_code=stock_code, stock_name=stock_name,
                                      freq=freq, start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_bond_bar(*, code: str, name: str,
                         stock_code: str, stock_name: str,
                         freq: Optional[int] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         skip_rt: bool = True,
                         to_frame=True, ) -> Dict:
    """获取可转债K线信息（阻塞版本）

    Args:
        code (str): 代码
        name (str): 名称
        stock_code (str): 股票代码
        stock_name (str): 股票名称
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Dict: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = fetch.block_fetch_bond_bar(code=code, name=name,
                                      stock_code=stock_code, stock_name=stock_name,
                                      freq=freq, start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data

# fund


async def fetch_fund_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取etf基金信息

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_fund_info())


def block_fetch_fund_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取etf基金信息（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_fund_info())


async def fetch_fund_net(*, code: str, name: Optional[str] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取基金净值

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    return _to_dataframe(to_frame,
                         await fetch.fetch_fund_net(code=code, name=name,
                                                    start=start, end=end))


def block_fetch_fund_net(*, code: str, name: Optional[str] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取基金净值（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    return _to_dataframe(to_frame,
                         fetch.block_fetch_fund_net(code=code, name=name,
                                                    start=start, end=end))


async def fetch_fund_bar(*, code: str, name: Optional[str] = None,
                         freq: Optional[int] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         skip_rt: bool = True,
                         to_frame=True) -> Dict:
    """获取基金k线

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_fund_bar(code=code, name=name,
                                      freq=freq, start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_fund_bar(*, code: str, name: Optional[str] = None,
                         freq: Optional[int] = None,
                         start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                         skip_rt: bool = True,
                         to_frame=True) -> Dict:
    """获取基金k线（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = fetch.block_fetch_fund_bar(code=code, name=name,
                                      freq=freq, start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data

# stock


async def fetch_index_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取指数信息

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_index_info())


def block_fetch_index_info(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取指数信息（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_index_info())


async def fetch_index_bar(*, code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                          skip_rt: bool = True, to_frame=True) -> Dict:
    """获取指数k线

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_stock_bar(code=code, name=name,
                                       freq=freq, start=start, end=end,
                                       skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_index_bar(*, code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                          skip_rt: bool = True, to_frame=True) -> Dict:
    """获取指数k线（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 基金名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = fetch.block_fetch_stock_bar(code=code, name=name,
                                       freq=freq, start=start, end=end,
                                       skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


async def fetch_stock_info(*, market: int = None, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票信息

    Args:
        market (int): 市场，默认全市场
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_info(market))


def block_fetch_stock_info(*, market: int = None, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票信息（阻塞版本）

    Args:
        market (int): 市场，默认全市场
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_info(market))


async def fetch_stock_is_margin(*, to_frame=True) -> Union[Set[str], pd.DataFrame]:
    """获取股票是否融资融券标的

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    data = await fetch.fetch_stock_is_margin()
    if to_frame:
        data = pd.DataFrame(data)
        data.columns = ['code']
    return data


def block_fetch_stock_is_margin(*, to_frame=True) -> Union[Set[str], pd.DataFrame]:
    """获取股票是否融资融券标的（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    data = fetch.block_fetch_stock_is_margin()
    if to_frame:
        data = pd.DataFrame(data)
        data.columns = ['code']
    return data


async def fetch_stock_bar(*, code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                          skip_rt: bool = True,
                          to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取股票k线

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_stock_bar(code=code, name=name,
                                       freq=freq, start=start, end=end,
                                       skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_stock_bar(*, code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                          skip_rt: bool = True,
                          to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取股票k线（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        freq (Optional[int], optional): 频率，默认 None，即日频
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    data = fetch.block_fetch_stock_bar(code=code, name=name,
                                       freq=freq, start=start, end=end,
                                       skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


async def fetch_stock_index(*, index_date: Optional[Union[date, str]] = None, to_frame=True) -> Union[Dict[str, Dict], pd.DataFrame]:
    """获取股票指标

    Args:
        index_date (Optional[Union[date, str]], optional): 指标日期，默认 None，即当天
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[Dict[str, Dict], pd.DataFrame]: _description_
    """
    index_date = _str_to_datetime(index_date) if type(
        index_date) == type('') else index_date
    data = await fetch.fetch_stock_index(index_date)
    if to_frame:
        data = pd.DataFrame(list(data.values()))
    return data


def block_fetch_stock_index(*, index_date: Optional[date] = None, to_frame=True) -> Union[Dict[str, Dict], pd.DataFrame]:
    """获取股票指标（阻塞版本）

    Args:
        index_date (Optional[Union[date, str]], optional): 指标日期，默认 None，即当天
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[Dict[str, Dict], pd.DataFrame]: _description_
    """
    data = fetch.block_fetch_stock_index(index_date)
    if to_frame:
        data = pd.DataFrame(list(data.values()))
    return data


async def fetch_stock_industry(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取行业信息

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_industry())


def block_fetch_stock_industry(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取行业信息（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_industry())


async def fetch_stock_industry_detail(*, code: Optional[str] = None,
                                      name: Optional[str] = None,
                                      to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取行业明细

    Args:
        code (bool, optional): 代码，默认空，即所有行业
        name (str, optional): 名称，默认空，即忽略名称
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_industry_detail(code, name))


def block_fetch_stock_industry_detail(*, code: Optional[str] = None,
                                      name: Optional[str] = None,
                                      to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取行业明细（阻塞版本）

    Args:
        code (bool, optional): 代码，默认空，即所有行业
        name (str, optional): 名称，默认空，即忽略名称
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_industry_detail(code, name))


async def fetch_stock_industry_daily(*, code: str, name: Optional[str] = None,
                                     start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                                     skip_rt: bool = True,
                                     to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取行业k线

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_stock_industry_daily(code=code, name=name,
                                                  start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_stock_industry_daily(*, code: str, name: Optional[str] = None,
                                     start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                                     skip_rt: bool = True,
                                     to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取行业k线（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = fetch.block_fetch_stock_industry_daily(code=code, name=name,
                                                  start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


async def fetch_stock_concept(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取概念信息

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_concept())


def block_fetch_stock_concept(*, to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取概念信息（阻塞版本）

    Args:
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_concept())


async def fetch_stock_concept_detail(*, code: Optional[str] = None, name: Optional[str] = None,
                                     to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取概念明细

    Args:
        code (bool, optional): 代码，默认空，即所有行业
        name (str, optional): 名称，默认空，即忽略名称
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_concept_detail(code, name))


def block_fetch_stock_concept_detail(*, code: Optional[str] = None, name: Optional[str] = None,
                                     to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取概念明细（阻塞版本）

    Args:
        code (bool, optional): 代码，默认空，即所有行业
        name (str, optional): 名称，默认空，即忽略名称
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_concept_detail(code, name))


async def fetch_stock_concept_daily(*, code: str, name: Optional[str] = None,
                                    start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                                    skip_rt: bool = True,
                                    to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取概念k线

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = await fetch.fetch_stock_industry_daily(code=code, name=name,
                                                  start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


def block_fetch_stock_concept_daily(*, code: str, name: Optional[str] = None,
                                    start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                                    skip_rt: bool = True,
                                    to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取概念k线（阻塞版本）

    Args:
        code (str): 代码
        name (Optional[str], optional): 名称，空就是没有
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        skip_rt (bool, optional): 是否忽略实时交易部分的数据，默认 True
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    data = fetch.block_fetch_stock_industry_daily(code=code, name=name,
                                                  start=start, end=end, skip_rt=skip_rt)
    data['bars'] = _utc_ts_to_datetime(
        _to_dataframe(to_frame, data['bars']), 'trade_date')
    return data


async def fetch_stock_yjbb(*, year: int, season: int,
                           to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票业绩报表

    Args:
        year (int): 年份
        season (int): 季度
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_yjbb(year, season))


def block_fetch_stock_yjbb(*, year: int, season: int,
                           to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票业绩报表（阻塞版本）

    Args:
        year (int): 年份
        season (int): 季度
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_yjbb(year, season))


async def fetch_stock_margin(*, code: str, start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                             to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票融资融券信息

    Args:
        code (str): 代码
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    return _to_dataframe(to_frame,
                         await fetch.fetch_stock_margin(code, start, end))


def block_fetch_stock_margin(*, code: str, start: Optional[Union[date, str]] = None, end: Optional[Union[date, str]] = None,
                             to_frame=True) -> Union[List[Dict], pd.DataFrame]:
    """获取股票融资融券信息（阻塞版本）

    Args:
        code (str): 代码
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    start = _str_to_datetime(start) if type(start) == type('') else start
    end = _str_to_datetime(end) if type(end) == type('') else end
    return _to_dataframe(to_frame,
                         fetch.block_fetch_stock_margin(code, start, end))


async def fetch_stock_hot_rank(*, code: Union[str, list],
                               to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取股票排名

    Args:
        code (Union[str, list]): 代码或代码列表
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    codes = code
    if type(code) == type(''):
        codes = [code]
    datas = []
    for code in codes:
        data = await fetch.fetch_stock_hot_rank(code=code)
        datas.append(data)
    return _to_dataframe(to_frame, data=datas)


def block_fetch_stock_hot_rank(*, code: Union[str, list],
                               to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取股票排名（阻塞版本）

    Args:
        code (Union[str, list]): 代码或代码列表
        start (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        end (Optional[Union[date, str]], optional): 开始时间，默认 None，即当日
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    codes = code
    if type(code) == type(''):
        codes = [code]
    datas = []
    for code in codes:
        data = fetch.block_fetch_stock_hot_rank(code=code)
        datas.append(data)
    return _to_dataframe(to_frame, data=datas)


async def fetch_stock_comment(*, code: Optional[Union[List[str], str]] = None,
                              to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取千股千评信息

    Args:
        code (Union[str, list]): 代码或代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    codes = code
    if type(code) == type(''):
        codes = [code]
    return _to_dataframe(to_frame, await fetch.fetch_stock_comment(codes=codes))


def block_fetch_stock_comment(*, code: Optional[Union[List[str], str]] = None,
                              to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取千股千评信息（阻塞版本）

    Args:
        code (Union[str, list]): 代码或代码列表
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    codes = code
    if type(code) == type(''):
        codes = [code]
    return _to_dataframe(to_frame,  fetch.block_fetch_stock_comment(codes=codes))


async def fetch_stock_comment_his(*, code: str,
                                  to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取千股千评历史

    Args:
        code (str): 代码
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame, await fetch.fetch_stock_comment_his(code=code))


def block_fetch_stock_comment_his(*, code: str,
                                  to_frame=True) -> Union[Dict, pd.DataFrame]:
    """获取千股千评历史（阻塞版本）

    Args:
        code (str): 代码
        to_frame (bool, optional): 是否转换为DataFrame格式，默认 True

    Returns:
        Union[List[Dict], pd.DataFrame]: 
    """
    return _to_dataframe(to_frame,  fetch.block_fetch_stock_comment_his(code=code))
