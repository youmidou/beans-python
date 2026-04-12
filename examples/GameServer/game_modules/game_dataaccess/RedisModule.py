import json
import logging
from typing import Any, Dict, Optional
import redis

from pkg.logger import logger
from pkg.ymd_dataaccess import YmdDataAccessBase


class RedisModule:
    def __init__(self, dataAccess:YmdDataAccessBase):
        self.dataAccess = dataAccess

