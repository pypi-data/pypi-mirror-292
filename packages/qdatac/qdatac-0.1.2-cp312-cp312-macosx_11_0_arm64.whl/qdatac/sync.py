from typing import List, Optional, Tuple
from qdatac.qdatac import Sync, BlockSync


class Dest:
    """同步目的
    """

    def __init__(self,
                 *,
                 file: Optional[str] = None,
                 mongo: Optional[str] = None,
                 mysql: Optional[str] = None,) -> None:
        """同步目的，文件（路径），mongodb（连接串）或mysql（连接串）

        Args:
            file (Optional[str], optional): 文件，默认 None，不同步
            mongo (Optional[str], optional): mongodb链接，默认 None，不同步
            mysql (Optional[str], optional): mysql链接，默认 None，不同步
        """
        self.file = file
        self.mongo = mongo
        self.mysql = mysql

    def to_list(self) -> Optional[List[Tuple]]:
        """转换为list

        Returns:
            Optional[List[Tuple]]: list
        """
        list = []
        if self.file is not None:
            list.append(('file', self.file))
        if self.mongo is not None:
            list.append(('mongodb', self.mongo))
        if self.mysql is not None:
            list.append(('mysql', self.mysql))
        return list


class Funcs:
    """同步的数据类型
    """
    TradeDate = 1
    # index
    IndexInfo = 2
    IndexDaily = 3
    # stock
    StockInfo = 4
    StockBar = 5
    StockIndex = 6
    StockIndustry = 7
    StockIndustryDetail = 8
    StockIndustryBar = 9,
    StockConcept = 10,
    StockConceptDetail = 11
    StockConceptBar = 12,
    StockYJBB = 13
    StockMargin = 14

    # fund
    FundInfo = 15
    FundNet = 16
    FundBar = 17

    # bond
    BondInfo = 18
    BondBar = 19


class MySync:
    """数据同步
    """

    def __init__(self, dest: Dest, funcs: Optional[List[int]] = None):
        """构造函数

        Args:
            dest (Dest): 同步的目的地
            funcs (Optional[List[int]], optional): 同步的功能. 默认None，即全部。参考：:class:`qdatac.sync.Funcs`
        """
        self.inner = Sync(dest.to_list(), funcs)

    async def sync(self, skip_basic=False, task_count=4, split_count=5):
        """同步函数

        Args:
            skip_basic (bool, optional): 是否忽略基础数据，默认否。
            task_count (int, optional): 任务数量，默认4，如果不清楚，不要改变。过多并发容易被封。
            split_count (int, optional): 同一个任务切分分组数，默认5。
        """
        await self.inner.sync(skip_basic, task_count, split_count)

    def shutdown(self):
        """停止同步"""
        self.inner.shutdown()


class MyBlockSync:
    """数据同步（阻塞版本）"""

    def __init__(self, dest: Dest, funcs: Optional[List[int]] = None):
        """参考：:func:`qdatac.sync.MySync.__init__`"""
        self.inner = BlockSync(dest.to_list(), funcs)

    def sync(self, skip_basic=False, task_count=4, split_count=5):
        """参考：:func:`qdatac.sync.MySync.sync`"""
        self.inner.sync(skip_basic, task_count, split_count)

    def shutdown(self):
        """参考：:func:`qdatac.sync.MySync.shutdown`"""
        self.inner.shutdown()
