from typing import List, Dict, Optional, Set
from datetime import date


def to_std_code(typ: int, code: str) -> str:
    """转换代码为内部格式的代码场

    Args:
        typ (int): 场交易类型, 参考 :class:`qfetch.MarketType`
        code (str): 代码

    Returns:
        str: _description_
    """
    pass


async def fetch_trade_date() -> Set[int]:
    """参考 :func:`qfetch.fetch.fetch_trade_date`"""
    pass


def block_fetch_trade_date() -> Set[int]:
    """参考 :func:`qfetch.fetch.block_fetch_trade_date`"""
    pass


async def fetch_next_trade_date(d: date) -> int:
    """参考 :func:`qfetch.fetch.fetch_next_trade_date`"""
    pass


def block_fetch_next_trade_date(d: date) -> int:
    """参考 :func:`qfetch.fetch.block_fetch_next_trade_date`"""
    pass


async def fetch_prev_trade_date(d: date) -> int:
    """参考 :func:`qfetch.fetch.fetch_prev_trade_date`"""
    pass


def block_fetch_prev_trade_date(d: date) -> int:
    """参考 :func:`qfetch.fetch.block_fetch_prev_trade_date`"""
    pass


async def fetch_is_trade_date(d: date) -> bool:
    """参考 :func:`qfetch.fetch.fetch_is_trade_date`"""
    pass


def block_fetch_is_trade_date(d: date) -> bool:
    """参考 :func:`qfetch.fetch.block_fetch_is_trade_date`"""
    pass


async def fetch_rt_quot(code: List[str]) -> Dict[str, Dict]:
    """参考 :func:`qfetch.fetch.fetch_rt_quot`"""
    pass


def block_fetch_rt_quot(code: List[str]) -> Dict[str, Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_rt_quot`"""
    pass


async def fetch_stock_rt_quot(codes: Optional[List[str]]) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_rt_quot`"""
    pass


def block_fetch_stock_rt_quot(codes: Optional[List[str]]) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_rt_quot`"""
    pass


async def fetch_bond_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_bond_info`"""
    pass


def block_fetch_bond_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_bond_info`"""
    pass


async def fetch_bond_bar(code: str, name: str,
                         stock_code: str, stock_name: str,
                         freq: Optional[int],
                         start: Optional[date],
                         end: Optional[date],
                         skip_rt: bool) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_bond_bar`"""
    pass


def block_fetch_bond_bar(code: str, name: str,
                         stock_code: str, stock_name: str,
                         freq: Optional[int],
                         start: Optional[date],
                         end: Optional[date],
                         skip_rt: bool) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_bond_bar`"""
    pass


async def fetch_fund_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_fund_info`"""
    pass


def block_fetch_fund_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_fund_info`"""
    pass


async def fetch_fund_net(code: str, name: Optional[str],
                         start: Optional[date], end: Optional[date]) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_fund_net`"""
    pass


def block_fetch_fund_net(code: str, name: Optional[str],
                         start: Optional[date], end: Optional[date]) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_fund_net`"""
    pass


async def fetch_fund_bar(code: str, name: Optional[str],
                         freq: Optional[int],
                         start: Optional[date],
                         end: Optional[date],
                         skip_rt: bool) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_fund_bar`"""
    pass


def block_fetch_fund_bar(code: str, name: Optional[str],
                         freq: Optional[int],
                         start: Optional[date],
                         end: Optional[date],
                         skip_rt: bool) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_fund_bar`"""
    pass


async def fetch_index_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_index_info`"""
    pass


def block_fetch_index_info() -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_index_info`"""
    pass


async def fetch_index_bar(code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[date] = None,
                          end: Optional[date] = None,
                          skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_index_bar`"""
    pass


def block_fetch_index_bar(code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[date] = None,
                          end: Optional[date] = None,
                          skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_index_bar`"""
    pass


async def fetch_stock_info(market: int = 0) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_info`"""
    pass


def block_fetch_stock_info(market: int = 0) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_info`"""
    pass


async def fetch_stock_is_margin() -> Set[str]:
    """参考 :func:`qfetch.fetch.fetch_stock_is_margin`"""
    pass


def block_fetch_stock_is_margin() -> Set[str]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_is_margin`"""
    pass


async def fetch_stock_bar(code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[date] = None,
                          end: Optional[date] = None,
                          skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_bar`"""
    pass


def block_fetch_stock_bar(code: str, name: Optional[str] = None,
                          freq: Optional[int] = None,
                          start: Optional[date] = None,
                          end: Optional[date] = None,
                          skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_bar`"""
    pass


async def fetch_stock_index(index_date: Optional[date]) -> Dict[str, Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_index`"""
    pass


def block_fetch_stock_index(index_date: Optional[date]) -> Dict[str, Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_index`"""
    pass


async def fetch_stock_industry() -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_industry`"""
    pass


def block_fetch_stock_industry() -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_industry`"""
    pass


async def fetch_stock_industry_detail(code: Optional[str] = None,
                                      name: Optional[str] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_industry_detail`"""
    pass


def block_fetch_stock_industry_detail(code: Optional[str] = None,
                                      name: Optional[str] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_industry_detail`"""
    pass


async def fetch_stock_industry_daily(code: str, name: Optional[str] = None,
                                     start: Optional[date] = None,
                                     end: Optional[date] = None,
                                     skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_industry_daily`"""
    pass


def block_fetch_stock_industry_daily(code: str, name: Optional[str] = None,
                                     start: Optional[date] = None,
                                     end: Optional[date] = None,
                                     skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_industry_daily`"""
    pass


async def fetch_stock_concept() -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_concept`"""
    pass


def block_fetch_stock_concept() -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_concept`"""
    pass


async def fetch_stock_concept_detail(code: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_concept_detail`"""
    pass


def block_fetch_stock_concept_detail(code: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_concept_detail`"""
    pass


async def fetch_stock_concept_daily(code: str, name: Optional[str] = None,
                                    start: Optional[date] = None,
                                    end: Optional[date] = None,
                                    skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_concept_daily`"""
    pass


def block_fetch_stock_concept_daily(code: str, name: Optional[str] = None,
                                    start: Optional[date] = None,
                                    end: Optional[date] = None,
                                    skip_rt: bool = True) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_concept_daily`"""
    pass


async def fetch_stock_yjbb(year: int, season: int) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_yjbb`"""
    pass


def block_fetch_stock_yjbb(year: int, season: int) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_yjbb`"""
    pass


async def fetch_stock_margin(code: str, start: Optional[date] = None, end: Optional[date] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.fetch_stock_margin`"""
    pass


def block_fetch_stock_margin(code: str, start: Optional[date] = None, end: Optional[date] = None) -> List[Dict]:
    """参考 :func:`qfetch.fetch.block_fetch_stock_margin`"""
    pass


async def fetch_stock_hot_rank(code: str) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_hot_rank`"""
    pass


def block_fetch_stock_hot_rank(code: str) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_hot_rank`"""
    pass


async def fetch_stock_comment(codes: Optional[List[str]] = None) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_comment`"""
    pass


def block_fetch_stock_comment(codes: Optional[List[str]] = None) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_comment`"""
    pass


async def fetch_stock_comment_his(code: str) -> Dict:
    """参考 :func:`qfetch.fetch.fetch_stock_comment_his`"""
    pass


def block_fetch_stock_comment_his(code: str) -> Dict:
    """参考 :func:`qfetch.fetch.block_fetch_stock_comment_his`"""
    pass
