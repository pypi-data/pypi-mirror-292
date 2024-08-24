from datetime import datetime
from typing import List, Dict, Union, Optional
import pandas as pd
from abc import ABC


def _to_dataframe(to_frame, data):
    if to_frame and data is not None:
        return pd.DataFrame(data)
    return data


def _json_def_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return None


def _datetime_to_int(date: Union[str, datetime]) -> int:
    if type(date) == type(''):
        nd = None
        for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y-%m-%d %H', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']:
            try:
                nd = datetime.strptime(date, fmt)
                return nd
            except ValueError:
                pass
        if nd == None:
            raise Exception('date format invalid: {}'.format(date))
        date = nd

    return int(date.strftime('%Y%m%d%H%M%S'))


class Loader(ABC):
    """数据库查询接口
    """

    def __init__(self, url: str):
        """初始化

        Args:
            url (str): 链接字符串
        """
        pass

    @staticmethod
    def to_dataframe(to_frame, data):
        return _to_dataframe(to_frame, data)

    @staticmethod
    def datetime_to_int(date: Union[str, datetime]) -> int:
        """datetime转换为数据格式的时间"""
        return _datetime_to_int(date)

    @staticmethod
    def json_def_handler(obj):
        return _json_def_handler(obj)

    async def load_bond_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载可转债信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_bond_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载可转债k线信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_fund_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载etf基金信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_fund_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载etf基金k线信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_fund_net(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载etf基金净值信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_index_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载指数信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_index_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载指数指标信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票k线信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_index(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票指标信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_industry(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载行业信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_industry_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载行业k线信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_industry_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载行业明细信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_concept(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票概念信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_concept_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票k线信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_concept_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票明细信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_yjbb(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票业绩报表信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_stock_margin(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载股票融资融券信息

        Args:
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def count(
        self, *,
        tab: str
    ) -> int:
        """加载数据库条数

        Args:
            tab (str): 库表名称。

        Returns:
            int: 条数
        """
        pass

    async def load_info(
        self, *,
        tab: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载基本信息

        Args:
            tab (str): 库表名称。
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass

    async def load_daily(
        self, *,
        tab: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """加载基本k线信息

        Args:
            tab (str): 库表名称。
            filter (Optional[Dict], optional): 过滤条件，同mongodb格式，默认 {}。
            sort (Optional[Dict], optional): 排序条件， 同mongodb格式，默认 {}。
            limit (Optional[int], optional): 限制条数， 默认 None，不限制
            to_frame (bool, optional): 是否转换为DataFrame格式，默认 是

        Returns:
            Union[List[Dict], pd.DataFrame]: 
        """
        pass


class BlockLoader(ABC):
    """数据库查询接口(阻塞版本)"""

    def __init__(self, url: str):
        """初始化

        Args:
            url (str): 链接字符串
        """
        pass

    @staticmethod
    def to_dataframe(to_frame, data):
        return _to_dataframe(to_frame, data)

    @staticmethod
    def datetime_to_int(date: Union[str, datetime]) -> int:
        """datetime转换为数据格式的时间"""
        return _datetime_to_int(date)

    @staticmethod
    def json_def_handler(obj):
        return _json_def_handler(obj)

    def load_bond_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_bond_info`"""
        pass

    def load_bond_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_bond_daily`"""
        pass

    def load_fund_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_fund_info`"""
        pass

    def load_fund_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_fund_daily`"""
        pass

    def load_fund_net(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_fund_net`"""
        pass

    def load_index_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_index_info`"""
        pass

    def load_index_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_index_daily`"""
        pass

    def load_stock_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_info`"""
        pass

    def load_stock_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_daily`"""
        pass

    def load_stock_index(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_index`"""
        pass

    def load_stock_industry(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry`"""
        pass

    def load_stock_industry_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_daily`"""
        pass

    def load_stock_industry_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_detail`"""
        pass

    def load_stock_concept(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept`"""
        pass

    def load_stock_concept_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_daily`"""
        pass

    def load_stock_concept_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_detail`"""
        pass

    def load_stock_yjbb(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_yjbb`"""
        pass

    def load_stock_margin(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_stock_margin`"""
        pass

    def count(
        self, *,
        tab: str
    ) -> int:
        """参考: :func:`qdatac.loader.Loader.count`"""
        pass

    def load_info(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_info`"""
        pass

    def load_daily(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        """参考: :func:`qdatac.loader.Loader.load_daily`"""
        pass
