from typing import List, Dict, Optional


class Sync:
    """参考: :class:`qdatac.sync.MySync`
    """
    def __init__(dest: List[(str, str)], funcs: Optional[List[int]] = None):
        """参考: :func:`qdatac.sync.MySync.__init__`
        """
        pass

    async def sync(self, skip_basic, task_count, split_count):
        """参考: :func:`qdatac.sync.MySync.sync`
        """
        pass

    def shutdown(self):
        """参考: :func:`qdatac.sync.MySync.shutdown`
        """
        pass


class BlockSync:
    """参考: :class:`qdatac.sync.MySync`
    """
    def __init__(dest: List[(str, str)], funcs: Optional[List[int]]):
        """参考: :func:`qdatac.sync.MySync.__init__`
        """
        pass

    def sync(self, skip_basic, task_count, split_count):
        """参考: :func:`qdatac.sync.MySync.sync`
        """
        pass

    def shutdown(self):
        """参考: :func:`qdatac.sync.MySync.shutdown`
        """
        pass


class MongoLoader:
    """参考: :class:`qdatac.loader.Loader`
    """
    def __init__(url: str):
        """参考: :func:`qdatac.loader.Loader.__init__`
        """
        pass

    async def load_bond_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_bond_info`
        """
        pass

    async def load_bond_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_bond_daily`
        """
        pass

    async def load_fund_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_info`
        """
        pass

    async def load_fund_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_daily`
        """
        pass

    async def load_fund_net(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_net`
        """
        pass

    async def load_index_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_index_info`
        """
        pass

    async def load_index_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_index_daily`
        """
        pass

    async def load_stock_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_info`
        """
        pass

    async def load_stock_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_daily`
        """
        pass

    async def load_stock_index(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_index`
        """
        pass

    async def load_stock_industry(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry`
        """
        pass

    async def load_stock_industry_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_daily`
        """
        pass

    async def load_stock_industry_detail(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_detail`
        """
        pass

    async def load_stock_concept(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept`
        """
        pass

    async def load_stock_concept_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_daily`
        """
        pass

    async def load_stock_concept_detail(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_detail`
        """
        pass

    async def load_stock_yjbb(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_yjbb`
        """
        pass

    async def load_stock_margin(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_margin`
        """
        pass

    async def count(
        self,
        tab: str
    ) -> int:
        """参考: :func:`qdatac.loader.Loader.count`
        """
        pass

    async def load_info(
        self,
        typ: str,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_info`
        """
        pass

    async def load_daily(
        self,
        typ: str,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_daily`
        """
        pass


class BlockMongoLoader:
    """参考: :func:`qdatac.loader.Loader`
    """
    def __init__(url: str):
        """参考: :func:`qdatac.loader.Loader.__init__`
        """
        pass

    def load_bond_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_bond_info`
        """
        pass

    def load_bond_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_bond_daily`
        """
        pass

    def load_fund_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_info`
        """
        pass

    def load_fund_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_daily`
        """
        pass

    def load_fund_net(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_fund_net`
        """
        pass

    def load_index_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_index_info`
        """
        pass

    def load_index_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_index_daily`
        """
        pass

    def load_stock_info(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_info`
        """
        pass

    def load_stock_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_daily`
        """
        pass

    def load_stock_index(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_index`
        """
        pass

    def load_stock_industry(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry`
        """
        pass

    def load_stock_industry_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_daily`
        """
        pass

    def load_stock_industry_detail(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_industry_detail`
        """
        pass

    def load_stock_concept(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept`
        """
        pass

    def load_stock_concept_daily(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_daily`
        """
        pass

    def load_stock_concept_detail(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_concept_detail`
        """
        pass

    def load_stock_yjbb(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_yjbb`
        """
        pass

    def load_stock_margin(
        self,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_stock_margin`
        """
        pass

    async def count(
        self,
        tab: str
    ) -> int:
        """参考: :func:`qdatac.loader.Loader.count`
        """
        pass

    async def load_info(
        self,
        typ: str,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_info`
        """
        pass

    async def load_daily(
        self,
        typ: str,
        filter: Optional[str],
        sort: Optional[str],
        limit: Optional[int],
    ) -> List[Dict]:
        """参考: :func:`qdatac.loader.Loader.load_daily`
        """
        pass
