from typing import Optional
from qdatac.loader import Loader
from qdatac.mongo import MongoLoader, BlockMongoLoader

from qdatac.sync import MySync, MyBlockSync, Dest, Funcs


def get_loader(typ: str, url: str, block: bool = False) -> Optional[Loader]:
    """获取数据获取实例

    Args:
        typ (str): 类型，目前只支持mongodb
        url (str): 链接字符串
        block (bool, optional): 是否使用阻塞版本，默认否。

    Returns:
        Optional[Loader]: 
    """
    typ = typ.lower()
    loader = None
    if typ == "file":
        pass
    elif typ == "mongodb":
        loader = MongoLoader(
            url=url) if not block else BlockMongoLoader(url=url)
    elif typ == "mysql":
        pass

    return loader


def int_to_str_date(t: int) -> str:
    """数据库时间转换为字符串格式

    Args:
        t (int): 数据库时间

    Returns:
        str: 字符串格式时间
    """
    exam = '20240802000000'
    t = str(t)
    if len(t) != len(exam):
        return ''
    return '{}-{}-{}'.format(t[0:4], t[4:6], t[6:8])
