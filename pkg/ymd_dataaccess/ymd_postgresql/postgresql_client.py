from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Type
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

Base = declarative_base()


@dataclass
class PostgresqlInfo:
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    echo: bool = False


class PostgresqlClient:
    def __init__(self, info: PostgresqlInfo):
        self._info = info
        self._engine = None
        self._session_factory = None

    def connect(self):
        """连接数据库，如果数据库不存在则自动创建"""
        # 先检查并创建数据库
        self._ensure_database_exists()

        connection_string = (
            f"postgresql://{self._info.user}:{self._info.password}"
            f"@{self._info.host}:{self._info.port}/{self._info.database}"
        )

        self._engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self._info.pool_size,
            max_overflow=self._info.max_overflow,
            pool_recycle=self._info.pool_recycle,
            echo=self._info.echo,
        )

        self._session_factory = sessionmaker(bind=self._engine)

    def _ensure_database_exists(self):
        """确保数据库存在，不存在则创建"""
        try:
            # 连接到默认的 postgres 数据库
            conn = psycopg2.connect(
                host=self._info.host,
                port=self._info.port,
                user=self._info.user,
                password=self._info.password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self._info.database,)
            )
            exists = cursor.fetchone()

            if not exists:
                # 创建数据库
                cursor.execute(f'CREATE DATABASE "{self._info.database}"')
                print(f"✅ 数据库 '{self._info.database}' 创建成功")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠️ 检查/创建数据库时出错: {e}")
            raise

    def AutoMigrate(self, *models_or_bases: Any) -> None:
        """自动迁移表结构

        注意：所有模型必须继承自同一个 Base 才能正确创建表
        参数 models_or_bases 保留用于兼容性，实际会创建所有已注册到 Base 的表
        """
        if self._engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        # 所有模型都已经继承自 Base，直接创建所有表
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory()

    def close(self):
        """关闭连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None

    # CRUD 操作
    def insert(self, obj: Any) -> bool:
        """插入单条记录"""
        session = self.get_session()
        try:
            session.add(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def insert_many(self, objs: List[Any]) -> bool:
        """批量插入记录"""
        session = self.get_session()
        try:
            session.add_all(objs)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, obj: Any) -> bool:
        """更新记录"""
        session = self.get_session()
        try:
            session.merge(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, obj: Any) -> bool:
        """删除记录"""
        session = self.get_session()
        try:
            session.delete(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def query(self, model: Type, filters: Optional[Dict] = None) -> List[Any]:
        """查询记录"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.all()
        finally:
            session.close()

    def query_one(self, model: Type, filters: Optional[Dict] = None) -> Optional[Any]:
        """查询单条记录"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.first()
        finally:
            session.close()

    def query_by_id(self, model: Type, id_value: Any) -> Optional[Any]:
        """根据主键查询"""
        session = self.get_session()
        try:
            return session.query(model).get(id_value)
        finally:
            session.close()

    def execute_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """执行原生 SQL"""
        session = self.get_session()
        try:
            result = session.execute(text(sql), params or {})
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def count(self, model: Type, filters: Optional[Dict] = None) -> int:
        """统计记录数"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.count()
        finally:
            session.close()