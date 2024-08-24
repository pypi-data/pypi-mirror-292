from typing import List, Dict, Union, Optional

from qdatac.qdatac import BlockMongoLoader as InnerBlockMongoLoader, MongoLoader as InnerMongoLoader
from qdatac.loader import Loader, BlockLoader
import pandas as pd
import json


class MongoLoader(Loader):
    """数据库查询接口，mongodb实现
    """

    def __init__(self, url: str):

        self.loader = InnerMongoLoader(url)

    async def load_bond_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_bond_info(filter=filter, sort=sort, limit=limit))

    async def load_bond_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_bond_daily(filter=filter, sort=sort, limit=limit))

    async def load_fund_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_fund_info(filter=filter, sort=sort, limit=limit))

    async def load_fund_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_fund_daily(filter=filter, sort=sort, limit=limit))

    async def load_fund_net(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_fund_net(filter=filter, sort=sort, limit=limit))

    async def load_index_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_index_info(filter=filter, sort=sort, limit=limit))

    async def load_index_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_index_daily(filter=filter, sort=sort, limit=limit))

    async def load_stock_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_info(filter=filter, sort=sort, limit=limit))

    async def load_stock_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_daily(filter=filter, sort=sort, limit=limit))

    async def load_stock_index(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_index(filter=filter, sort=sort, limit=limit))

    async def load_stock_industry(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_industry(filter=filter, sort=sort, limit=limit))

    async def load_stock_industry_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_industry_daily(filter=filter, sort=sort, limit=limit))

    async def load_stock_industry_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_industry_detail(filter=filter, sort=sort, limit=limit))

    async def load_stock_concept(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_concept(filter=filter, sort=sort, limit=limit))

    async def load_stock_concept_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_concept_daily(filter=filter, sort=sort, limit=limit))

    async def load_stock_concept_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_concept_detail(filter=filter, sort=sort, limit=limit))

    async def load_stock_yjbb(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_yjbb(filter=filter, sort=sort, limit=limit))

    async def load_stock_margin(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_stock_margin(filter=filter, sort=sort, limit=limit))

    async def count(
        self, *,
        tab: str
    ) -> int:
        return await self.loader.count(tab=tab)

    async def load_info(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_info(typ=typ, filter=filter, sort=sort, limit=limit))

    async def load_daily(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 await self.loader.load_daily(typ=typ, filter=filter, sort=sort, limit=limit))


class BlockMongoLoader(BlockLoader):
    """数据库查询接口，mongodb实现（阻塞版本）
    """

    def __init__(self, url: str):
        self.loader = InnerBlockMongoLoader(url)

    @staticmethod
    def to_dataframe(to_frame, data):
        if to_frame and data is not None:
            return pd.DataFrame(data)
        return data

    def load_bond_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_bond_info(filter=filter, sort=sort, limit=limit))

    def load_bond_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_bond_daily(filter=filter, sort=sort, limit=limit))

    def load_fund_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_fund_info(filter=filter, sort=sort, limit=limit))

    def load_fund_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_fund_daily(filter=filter, sort=sort, limit=limit))

    def load_fund_net(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_fund_net(filter=filter, sort=sort, limit=limit))

    def load_index_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_index_info(filter=filter, sort=sort, limit=limit))

    def load_index_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_index_daily(filter=filter, sort=sort, limit=limit))

    def load_stock_info(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_info(filter=filter, sort=sort, limit=limit))

    def load_stock_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_daily(filter=filter, sort=sort, limit=limit))

    def load_stock_index(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_index(filter=filter, sort=sort, limit=limit))

    def load_stock_industry(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_industry(filter=filter, sort=sort, limit=limit))

    def load_stock_industry_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_industry_daily(filter=filter, sort=sort, limit=limit))

    def load_stock_industry_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_industry_detail(filter=filter, sort=sort, limit=limit))

    def load_stock_concept(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_concept(filter=filter, sort=sort, limit=limit))

    def load_stock_concept_daily(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_concept_daily(filter=filter, sort=sort, limit=limit))

    def load_stock_concept_detail(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_concept_detail(filter=filter, sort=sort, limit=limit))

    def load_stock_yjbb(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_yjbb(filter=filter, sort=sort, limit=limit))

    def load_stock_margin(
        self, *,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:

        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_stock_margin(filter=filter, sort=sort, limit=limit))

    def count(
        self, *,
        tab: str
    ) -> int:
        return self.loader.count(tab=tab)

    def load_info(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_info(typ=typ, filter=filter, sort=sort, limit=limit))

    def load_daily(
        self, *,
        typ: str,
        filter: Optional[Dict] = {},
        sort: Optional[Dict] = {},
        limit: Optional[int] = None, to_frame=True
    ) -> Union[List[Dict], pd.DataFrame]:
        filter, sort = json.dumps(
            filter, default=self.json_def_handler), json.dumps(sort, default=self.json_def_handler)
        return self.to_dataframe(to_frame,
                                 self.loader.load_daily(typ=typ, filter=filter, sort=sort, limit=limit))
