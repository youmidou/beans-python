import logging
from typing import Any, Dict, Optional
import pymysql
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from pkg.ymd_dataaccess import YmdDataAccessBase


class MysqlModule:
    def __init__(self, dataAccess:YmdDataAccessBase):
        self.dataAccess = dataAccess

